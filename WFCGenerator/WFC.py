import random
import numpy as np
from scipy.stats import entropy as shannon_entropy

class OverlappingWFC:
    def __init__(self, width, height, catalog, weights, adjacency):
        """
        Initialize the WFC grid, patterns, weights, and adjacency rules.
        """
        self.width = width
        self.height = height
        self.catalog = catalog # List of all unique patterns
        self.weights = weights # Frequency/probability of each pattern
        self.adjacency = adjacency # Directional adjacency rules for patterns
        self.pattern_size = len(catalog[0]) # Size of a single pattern (assumed square)

        # The wave is a grid of sets, each set contains indices of possible patterns
        self.wave = [[set(range(len(catalog))) for _ in range(width)] for _ in range(height)]

        # Grid to cache entropy values (optional, not used yet)
        self.entropies = [[None for _ in range(width)] for _ in range(height)]

        # Boolean grid to mark cells that have been collapsed to one pattern
        self.collapsed = [[False for _ in range(width)] for _ in range(height)]


    def run_step(self):
        """
        Perform one collapse step by selecting the cell with minimal entropy and propagating constraints.
        """
        min_entropy = float('inf')
        min_pos = None
    	
        # Loop over each cell to find the one with lowest entropy
        for y in range(self.height):
            for x in range(self.width):
                if not self.collapsed[y][x] and len(self.wave[y][x]) > 1:
                    # Extract weights of possible patterns
                    choices = list(self.wave[y][x])
                    weights = np.array([self.weights[i] for i in choices], dtype=float)

                    # Normalize to probabilities
                    probs = weights / weights.sum()

                    # Shannon entropy (in bits)
                    entropy = shannon_entropy(probs, base=2)

                    # Add tiny noise for tie-breaking
                    entropy += random.random() * 1e-6

                    # Track cell with the minimum entropy
                    if entropy < min_entropy:
                        min_entropy = entropy
                        min_pos = (x, y)

        # If no uncollapsed cells remain, WFC is complete
        if min_pos is None:
            return False

        # Collapse the chosen cell to a single pattern
        x, y = min_pos
        choices = list(self.wave[y][x])
        weights = [self.weights[i] for i in choices]
        chosen = random.choices(choices, weights=weights)[0]

        # Update wave and mark as collapsed
        self.wave[y][x] = {chosen}
        self.collapsed[y][x] = True

        # Propagate constraints to neighbors
        self.propagate(x, y)

        return True


    def propagate(self, x, y):
        """
        Propagate constraints from a collapsed cell to its neighbors using adjacency rules.
        """
        stack = [(x, y)]

        while stack:
            cx, cy = stack.pop()

            # Check all 4 cardinal directions
            for direction, (dx, dy) in enumerate([(0, -1), (1, 0), (0, 1), (-1, 0)]):
                nx, ny = cx + dx, cy + dy

                # Skip out-of-bounds neighbors
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    possible = set()

                    # Collect all patterns that are valid in the given direction
                    for t in self.wave[cy][cx]:
                        possible.update(self.adjacency[t][direction])
                    
                    # Update the neighbor's wave by intersecting with allowed patterns
                    new_wave = self.wave[ny][nx].intersection(possible)

                    # If the neighbor's possibilities changed, propagate further
                    if new_wave != self.wave[ny][nx]:
                        self.wave[ny][nx] = new_wave
                        stack.append((nx, ny))


    def render(self):
        """
        Render the current wave state to a 2D grid by sampling the center tile of each collapsed pattern.
        """
        output = [['?' for _ in range(self.width)] for _ in range(self.height)]
        center = self.pattern_size // 2

        for y in range(self.height):
            for x in range(self.width):
                if len(self.wave[y][x]) == 1:
                    # Get the only pattern and extract its center character
                    pattern = self.catalog[next(iter(self.wave[y][x]))]
                    output[y][x] = pattern[center][center]

        return output