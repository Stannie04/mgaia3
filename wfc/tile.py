import numpy as np

class Tile:
    def __init__(self, pixel_length, pixels, bitmap, tile_id):
        self.pixel_length = pixel_length
        self.pixels = self.pixel_init(pixels)
        self.bitmap = bitmap
        self.state = np.full(len(self.bitmap.patterns), True)
        self.collapsed_state = None
        self.id = tile_id
        self.masked_states = []

        self.update_distribution_and_entropy()


    def update_distribution_and_entropy(self):
        """Update the tile's probability distribution based on the current state."""

        distribution = np.where(self.state, self.bitmap.pattern_weights, 0)
        total = np.sum(distribution)
        if total == 0:
            self.distribution = None
            return

        self.distribution = distribution / total
        self.entropy = -np.sum(self.distribution * np.log(self.distribution + 1e-10))


    def pixel_init(self, pixels):
        """Initialize the tile's pixels and add the tile to each pixel's list of tiles."""

        for pixel in pixels.flatten():
            pixel.add_tile(self)

        return np.array(pixels)


    def mask_state(self, pattern_id):
        """Mask a pattern in the tile's state.

        When updating, the tile will ignore this pattern.
        """

        self.masked_states.append(pattern_id)
        self.state[pattern_id] = False
        self.update_distribution_and_entropy()


    def backtrack(self):
        """Backtrack the tile's collapsed state to the last known state.

        Note that backtracking does not allow for collapses, so this does not need to be checked.
        """

        self.collapsed_state = None

        self.state = np.array([
            self.pattern_fits_tile(pattern)
            if (pattern.id not in self.masked_states) else False
            for pattern in self.bitmap
        ])

        self.update_distribution_and_entropy()


    def is_collapsed(self):
        """Check if the tile has collapsed to a single pattern."""

        return np.count_nonzero(self.state) == 1


    def update_state(self, updated_pixels):
        """Update the tile's state based on the current state of its pixels.

        If this tile is now collapsed, propagate this information to the neighbouring tiles.
        """

        if self.is_collapsed():
            return True

        self.state = np.array([
            self.pattern_fits_tile(pattern)
            if (self.state[pattern.id] and pattern.id not in self.masked_states) else False
            for pattern in self.bitmap.patterns])

        self.update_distribution_and_entropy()
        if self.distribution is None:
            return False

        if self.is_collapsed(): # If the tile has now collapsed, update the unknown pixels
            return self.collapse(updated_pixels)

        return True


    def pattern_fits_tile(self, pattern):
        """Check if a given pattern fits the tile's current state.

        If a pixel's value is None, it can still be anything.
        """

        return all(
            self.pixels[i][j].value is None or self.pixels[i][j].value == pattern.pattern[i][j]
            for i in range(self.pixel_length)
            for j in range(self.pixel_length)
        )


    def collapse(self, updated_pixels):
        """Collapse the tile to a single pattern and update the tile's state, according to the probability distribution."""

        pattern_id = np.random.choice(range(len(self.bitmap.patterns)), p=self.distribution)
        pattern = self.bitmap.get_pattern_from_id(pattern_id)
        self.collapsed_state = pattern_id

        self.state.fill(False)
        self.state[pattern_id] = True
        self.update_distribution_and_entropy()

        pixels_to_update = [
            self.pixels[i][j]
            for i in range(self.pixel_length)
            for j in range(self.pixel_length)
            if self.pixels[i][j].set_value(pattern.pattern[i][j], updated_pixels)
        ]
        return all(pixel.update_tile_states(updated_pixels) for pixel in pixels_to_update)
