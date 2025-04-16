import numpy as np
import matplotlib.pyplot as plt

class Output:
    def __init__(self, height, width, bitmap):
        self.bitmap = bitmap
        self.height = height
        self.width = width
        self.map = self.init_map()


    def __str__(self):
        string = "\n"
        for row in self.map:
            for pixel in row:
                string += f"{pixel.value} " if pixel.value is not None else "? "
            string += "\n"
        return string


    def __deepcopy__(self, memo):
        new_output = Output(height=self.height, width=self.width, bitmap=self.bitmap)
        for i in range(self.height):
            for j in range(self.width):
                new_output.map[i, j].value = self.map[i, j].value
        return new_output


    def init_map(self):
        """Initialize the output map with empty pixels."""

        return np.array([[Pixel(x, y) for y in range(self.width)] for x in range(self.height)])


    def n_unknown_states(self):
        """Get the number of unknown pixels in the ouptut map."""

        return sum(pixel.value is None for row in self.map for pixel in row)


    def as_image(self):
        """Display the output map as an image."""

        image = np.zeros((self.height, self.width, 3))
        for i in range(self.height):
            for j in range(self.width):
                if self.map[i, j].value is None:
                    image[i, j] = [1,0,0]
                elif self.map[i, j].value == 0:
                    image[i, j] = [0,0,0]
                elif self.map[i, j].value == 1:
                    image[i, j] = [1,1,1]
                elif self.map[i, j].value == 2:
                    image[i, j] = [0,0,1]
                elif self.map[i, j].value == 3:
                    image[i, j] = [1,0,1]

        plt.imshow((image*255).astype(np.uint8))
        plt.show()


class Pixel:
    def __init__(self, x, z):
        self.x = x
        self.z = z
        self.value = None
        self.tiles = []


    def add_tile(self, tile):
        """Add a tile to the list of tiles that contain this pixel."""

        self.tiles.append(tile)


    def set_value(self, value, updated_pixels=[]):
        """Set the value of the pixel, if not fixed already."""
        if self.value is not None:
            return False

        updated_pixels.append(self)

        self.value = value
        return True


    def update_tile_states(self, updated_pixels=[]):
        """Update the state of all tiles that contain this pixel."""

        for tile in self.tiles:
            if not tile.update_state(updated_pixels):
                return False
        return True