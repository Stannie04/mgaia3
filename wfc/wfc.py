import sys
import numpy as np
from bitmap import Bitmap
from output import Output
from tile import Tile
from tqdm import tqdm
from collections import deque
import copy

class WFC:
    def __init__(self):
        self.bitmap = None
        self.output = None
        self.tiles = None
        self.history = None
        self.attempts = 0


    def __deepcopy__(self, memo):
        current_state = WFC()

        current_state.bitmap = self.bitmap
        current_state.output = copy.deepcopy(self.output)
        current_state.tiles = self.tile_init(self.bitmap.pattern_length)
        for tile in current_state.tiles:
            tile.update_state()

        return current_state


    def initialize(self, bitmap_file, pattern_length, output_height, output_width):
        self.bitmap = Bitmap(bitmap_file=bitmap_file, pattern_length=pattern_length)
        self.output = Output(height=output_height, width=output_width, bitmap=self.bitmap)
        self.tiles = self.tile_init(pattern_length)
        self.history = deque()


    def tile_init(self, pattern_length):
        """Initialize the tiles of the output map."""

        tile_id = 0
        tiles = []
        for i in range(self.output.map.shape[0] - pattern_length + 1):
            for j in range(self.output.map.shape[1] - pattern_length + 1):
                tiles.append(Tile(pixel_length=pattern_length, pixels=self.output.map[i:i+pattern_length, j:j+pattern_length], bitmap=self.bitmap, tile_id=tile_id))
                tile_id += 1
        return tiles


    def random_nonzero_argmin(self):
        """Get a random index of the set of non-collapsed tiles with the lowest Shannon entropy."""

        mask = np.array([not tile.is_collapsed() for tile in self.tiles])
        if not mask.any(): # If all tiles have collapsed
            return None

        entropy_map = np.array([tile.entropy for tile in self.tiles])
        all_argmin = np.flatnonzero(entropy_map == entropy_map[mask].min())

        return np.random.choice(all_argmin)


    def backtrack(self):
        """Backtrack to the previous state of the WFC object."""

        self.attempts += 1

        if not self.history:
            return

        collapsed_tile, last_updates = self.history.pop()
        collapsed_state = collapsed_tile.collapsed_state

        if collapsed_state is None:
            sys.exit("Invalid state: collapsed tile has no collapsed state.")

        # Restore pixels
        tiles_to_update = set()
        for pixel in last_updates:
            pixel.value = None
            tiles_to_update.update(pixel.tiles)

        # Restore tile states
        for tile in tiles_to_update:
            tile.backtrack()

        collapsed_tile.mask_state(collapsed_state)
        if collapsed_tile.is_collapsed():
            new_history = []
            valid_state = collapsed_tile.collapse(new_history)
            self.history.append((collapsed_tile, new_history))
            if not valid_state:
                self.backtrack()

        if not any(collapsed_tile.state):
            for state in collapsed_tile.masked_states:
                collapsed_tile.state[state] = True
            collapsed_tile.masked_states = []
            collapsed_tile.update_distribution_and_entropy()

            self.backtrack()


    def run_wfc(self, n_pixels):
        """Run the WFC algorithm until all pixels are valid, or an invalid solution is found.

        Each time a tile is collapsed, the current state of the WFC object is saved.
        That way, if the following forced collapses cause it to reach an invalid state,
        the previous state can be restored.
        """

        progress_bar = tqdm(total=n_pixels, desc="Progress", position=0, leave=False)

        while self.attempts < 1000:

            idx_min_entropy = self.random_nonzero_argmin()
            if idx_min_entropy is None:
                break
            tile = self.tiles[idx_min_entropy]

            current_history = []
            valid_state = tile.collapse(current_history)
            self.history.append((tile, current_history))
            if not valid_state:
                self.backtrack()

            progress_bar.n = n_pixels - self.output.n_unknown_states()
            progress_bar.refresh()


    def prime_border(self, value):
        """Fix an initial state for the output map."""

        for edge in [self.output.map[0, :], self.output.map[-1, :], self.output.map[:, 0], self.output.map[:, -1]]:
            for pixel in edge:
                pixel.set_value(value)

        for tile in self.tiles:
            tile.update_state([])


    def prime_area(self, starting_map):
        """Prime the output map with a starting map."""

        for i in range(self.output.height):
            for j in range(self.output.width):
                self.output.map[i, j].value = starting_map[i, j]

        for tile in self.tiles:
            tile.update_state([])


def get_wfc_ouptut(area_length, area_width, border_value, bitmap_file, pattern_length=2, starting_map=None):
    n_pixels = area_length*area_width

    while True:
        wfc = WFC()
        wfc.initialize(bitmap_file=bitmap_file, pattern_length=pattern_length, output_height=area_length, output_width=area_width)
        if starting_map is not None:
            wfc.prime_area(starting_map)
        else:
            wfc.prime_border(border_value)
        wfc.run_wfc(n_pixels)

        invalid_states = wfc.output.n_unknown_states()
        if invalid_states == 0:
            break

    return wfc


def main():
    bitmap_file = "wfc/bitmaps/test.txt"
    pattern_length = 2
    output_height = 49
    output_width = 49

    n_pixels = output_height * output_width

    # In extreme cases, recursion from collapsing tiles can exceed the default recursion limit.
    # The recursive process goes through three methods (collapse_and_propagate, Tile.collapse, Tile.update_state),
    # so the limit is set to 3 times the number of pixels. This is slightly overkill as there are more pixels than tiles, but it's a safe bet.
    sys.setrecursionlimit(n_pixels*3)

    while True:
        wfc = WFC()
        wfc.initialize(bitmap_file=bitmap_file, pattern_length=pattern_length, output_height=output_height, output_width=output_width)
        wfc.prime_border(1)
        wfc.run_wfc(n_pixels)

        invalid_states = wfc.output.n_unknown_states()
        if invalid_states == 0:
            break

        print(f"{invalid_states} invalid pixels out of {n_pixels} total ({100 - (invalid_states / n_pixels * 100)}%), retrying.")
        # print(wfc.output)

    print(f"Completed after {wfc.attempts} attempts")
    print(wfc.output)
    wfc.output.as_image()


if __name__=="__main__":
    main()