import random

class OverlappingWFC:
    def __init__(self, width, height, catalog, weights, adjacency):
        self.width = width
        self.height = height
        self.catalog = catalog
        self.weights = weights
        self.adjacency = adjacency
        self.pattern_size = len(catalog[0])
        self.wave = [[set(range(len(catalog))) for _ in range(width)] for _ in range(height)]
        self.entropies = [[None for _ in range(width)] for _ in range(height)]
        self.collapsed = [[False for _ in range(width)] for _ in range(height)]


    def run_step(self):
        min_entropy = float('inf')
        min_pos = None
        for y in range(self.height):
            for x in range(self.width):
                if not self.collapsed[y][x] and len(self.wave[y][x]) > 1:
                    entropy = len(self.wave[y][x]) + random.random() * 0.1
                    if entropy < min_entropy:
                        min_entropy = entropy
                        min_pos = (x, y)

        if min_pos is None:
            return False

        x, y = min_pos
        choices = list(self.wave[y][x])
        weights = [self.weights[i] for i in choices]
        chosen = random.choices(choices, weights=weights)[0]
        self.wave[y][x] = {chosen}
        self.collapsed[y][x] = True
        self.propagate(x, y)
        return True


    def propagate(self, x, y):
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            for direction, (dx, dy) in enumerate([(0, -1), (1, 0), (0, 1), (-1, 0)]):
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    changed = False
                    possible = set()
                    for t in self.wave[cy][cx]:
                        possible.update(self.adjacency[t][direction])
                    new_wave = self.wave[ny][nx].intersection(possible)
                    if new_wave != self.wave[ny][nx]:
                        self.wave[ny][nx] = new_wave
                        stack.append((nx, ny))


    def render(self):
        output = [['?' for _ in range(self.width)] for _ in range(self.height)]
        center = self.pattern_size // 2
        for y in range(self.height):
            for x in range(self.width):
                if len(self.wave[y][x]) == 1:
                    pattern = self.catalog[next(iter(self.wave[y][x]))]
                    output[y][x] = pattern[center][center]
        return output