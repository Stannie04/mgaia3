import os
from tqdm import tqdm
from collections import defaultdict, Counter

def load_map(filename):
    """
    Load a single map from a text file, sanitize invalid characters into 
    floor ('.'), wall ('X'), or out-of-bounds ('-'), 
    and return it as a list containing the map grid.
    """
    print(f"\nLoading map from: {filename}")
    with open(filename, "r") as f:
        map_data = [
            [c if c in ['-', '.', 'X'] else '.' for c in line.strip()]
            for line in f
        ]
    print(f"Loaded map with dimensions: {len(map_data[0])}x{len(map_data)}\n")

    return [map_data]


def load_all_maps(folder_path):
    """
    Load all .txt maps in a folder, sanitize each
    line into valid tiles, and return a list of map grids.
    """
    print(f"\nLoading all maps from: {folder_path}")
    maps = []
    file_count = 0
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as f:
                lines = []
                for line in f:
                    sanitized_line = ''.join(c if c in ['-', '.', 'X'] else '.' for c in line.strip())
                    lines.append(list(sanitized_line))
                if lines:
                    maps.append(lines)
                    file_count += 1
    print(f"Loaded {file_count} maps\n")

    return maps


def save_output(output, filename="generated_map.txt"):
    """
    Write the generated map grid to a text file, one row per line.
    """
    print(f"Saving generated map to: {filename}")
    with open(filename, "w") as f:
        for row in output:
            f.write("".join(row) + "\n")
    print(f"Map saved successfully, dimensions: {len(output[0])}x{len(output)}\n")


def extract_patterns(maps, N):
    """
    Extract all N×N tile patterns from each map by sliding a window 
    over every possible position and return them as tuples.
    """
    print(f"Extracting {N}x{N} patterns")
    patterns = []
    pattern_count = 0
    for map_data in maps:
        height, width = len(map_data), len(map_data[0])
        for y in range(height - N + 1):
            for x in range(width - N + 1):
                pattern = tuple(
                    tuple(map_data[y + dy][x + dx] for dx in range(N))
                    for dy in range(N)
                )
                patterns.append(pattern)
                pattern_count += 1
    print(f"Extracted {pattern_count} total {N}x{N} patterns")

    return patterns


def build_pattern_catalog(patterns):
    """
    Build a catalog of unique patterns and corresponding 
    weights based on their frequency in the training set.
    """
    print("Building pattern catalog")
    counter = Counter(patterns)
    catalog = list(counter.keys())
    weights = [counter[p] for p in catalog]
    print(f"Catalog contains {len(catalog)} unique patterns")
    print(f"Most common pattern appears {max(weights)} times")
    print(f"Least common pattern appears {min(weights)} times")

    return catalog, weights


def pattern_match(p1, p2, direction):
    """Check if two patterns p1 and p2 match along the given direction 
    (0=up,1=right,2=down,3=left) by comparing their bordering rows or columns.
    """
    N = len(p1)
    if direction == 0:
        return all(p1[0][i] == p2[-1][i] for i in range(N))
    elif direction == 1:
        return all(p1[i][-1] == p2[i][0] for i in range(N))
    elif direction == 2:
        return all(p1[-1][i] == p2[0][i] for i in range(N))
    elif direction == 3:
        return all(p1[i][0] == p2[i][-1] for i in range(N))


def compute_tile_adjacency(maps):
    """
    Compute sets of adjacent tile pairs in each of 
    four cardinal directions across all training maps.
    """
    tile_adj = {d: set() for d in range(4)}
    for map_data in maps:
        H, W = len(map_data), len(map_data[0])
        for y in range(H):
            for x in range(W):
                t1 = map_data[y][x]
                for d, (dx, dy) in enumerate([(0, -1), (1, 0), (0, 1), (-1, 0)]):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H:
                        t2 = map_data[ny][nx]
                        tile_adj[d].add((t1, t2))

    return tile_adj


def build_adjacency_rules(catalog, tile_adj=None):
    """
    Generate adjacency rules for each pattern index: 
    if two patterns match on their border and (optionally) their center 
    tiles respect training tile adjacency, allow that transition.
    """
    print("Building adjacency rules")
    adjacency = defaultdict(lambda: [set() for _ in range(4)])
    total_rules = 0
    for i, a in enumerate(tqdm(catalog, desc="Processing patterns")):
        for j, b in enumerate(catalog):
            for direction in range(4):
                if not pattern_match(a, b, direction):
                    continue
                if tile_adj is not None:
                    c = len(a) // 2
                    t1 = a[c][c]
                    t2 = b[c][c]
                    if (t1, t2) not in tile_adj[direction]:
                        continue
                adjacency[i][direction].add(j)
                total_rules += 1
    print(f"Generated {total_rules} adjacency rules for {len(catalog)} patterns")
    print(f"Average rules per pattern: {total_rules / len(catalog):.1f}\n")

    return adjacency