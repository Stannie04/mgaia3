import numpy as np

class Bitmap:
    def __init__(self, bitmap_file, pattern_length):
        self.bitmap = self.read_bitmap(bitmap_file)
        self.pattern_length = pattern_length
        self.patterns = []
        self.pattern_weights = []

        self.pattern_init()


    def __len__(self):
        return len(self.patterns)


    def __getitem__(self, key):
        return self.patterns[key]


    def read_bitmap(self, pattern_file):
        """"Extract the contents of pattern_file into a 2D array."""

        with open(pattern_file, "r") as f:
            bitmap = []
            for line in f:
                bitmap.append([int(i) for i in line.strip()])
        return np.array(bitmap)


    def pattern_init(self):
        """Read the input bitmap and extract the distribution of patterns in it.

        Patterns are of size pattern_length x pattern_length.
        """

        self.patterns = []
        pattern_id = 0
        for bitmap_flips in range(2):
            for bitmap_rotations in range(4):
                for i in range(self.bitmap.shape[0] - self.pattern_length + 1):
                    for j in range(self.bitmap.shape[1] - self.pattern_length + 1):
                        pattern = self.bitmap[i:i+self.pattern_length, j:j+self.pattern_length]

                        existing_pattern_id = self.pattern_exists(pattern)
                        if existing_pattern_id is not None:
                            exisiting_pattern = self.get_pattern_from_id(existing_pattern_id)
                            exisiting_pattern.counts += 1

                        else:
                            self.patterns.append(Pattern(pattern=pattern, pattern_id=pattern_id))
                            pattern_id += 1

                self.bitmap = np.rot90(self.bitmap) # Rotate the bitmap 90 degrees to get all possible patterns
            self.bitmap = np.flip(self.bitmap, axis=0) # Also mirror it

        self.pattern_weights = np.array([p.counts for p in self.patterns])


    def get_pattern_from_id(self, pattern_id):
        """Return the pattern with the given ID."""	
        return self.patterns[pattern_id]


    def pattern_exists(self, pattern):
        """If the same pattern as the given one already exists, return its ID."""

        for i, p in enumerate(self.patterns):
            if np.array_equal(p.pattern, pattern):
                return i
        return None
        
        
class Pattern:
    def __init__(self, pattern, pattern_id):
        self.pattern = pattern
        self.pattern_length = len(pattern)
        self.id = pattern_id
        self.counts = 1


    def __len__(self):
        return len(self.pattern)


    def __getitem__(self, key):
        return self.pattern[key]
