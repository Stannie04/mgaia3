from collections import defaultdict, Counter

def load_map(filename):
    print(f"\nLoading map from: {filename}")
    with open(filename, "r") as f:
        map_data = [list(line.strip()) for line in f]
    print(f"Loaded map with dimensions: {len(map_data[0])}x{len(map_data)}\n")
    return map_data


def extract_patterns(map_data, N):
    print(f"Extracting {N}x{N} patterns from map...")
    patterns = []
    height, width = len(map_data), len(map_data[0])
    pattern_count = 0

    for y in range(height - N + 1):
        for x in range(width - N + 1):
            pattern = tuple(tuple(map_data[y + dy][x + dx] for dx in range(N)) for dy in range(N))
            patterns.append(pattern)
            pattern_count += 1

    print(f"Extracted {pattern_count} unique {N}x{N} patterns")
    return patterns


def build_pattern_catalog(patterns):
    print("Building pattern catalog...")
    counter = Counter(patterns)
    catalog = list(counter.keys())
    weights = [counter[p] for p in catalog]

    print(f"Catalog contains {len(catalog)} unique patterns")
    print(f"Most common pattern appears {max(weights)} times")
    print(f"Least common pattern appears {min(weights)} times")

    return catalog, weights


def pattern_match(p1, p2, direction):
    directions = ["up", "right", "down", "left"]
    N = len(p1)
    if direction == 0:  # up
        return all(p1[0][i] == p2[-1][i] for i in range(N))
    elif direction == 1:  # right
        return all(p1[i][-1] == p2[i][0] for i in range(N))
    elif direction == 2:  # down
        return all(p1[-1][i] == p2[0][i] for i in range(N))
    elif direction == 3:  # left
        return all(p1[i][0] == p2[i][-1] for i in range(N))


def build_adjacency_rules(catalog):
    print("Building adjacency rules...")
    adjacency = defaultdict(lambda: [set() for _ in range(4)])
    total_rules = 0

    for i, a in enumerate(catalog):
        for j, b in enumerate(catalog):
            for direction in range(4):
                if pattern_match(a, b, direction):
                    adjacency[i][direction].add(j)
                    total_rules += 1

    print(f"Generated {total_rules} adjacency rules for {len(catalog)} patterns")
    print(f"Average rules per pattern: {total_rules/len(catalog):.1f}\n")
    return adjacency


def save_output(output, filename="generated_map.txt"):
    print(f"Saving generated map to: {filename}")
    with open(filename, "w") as f:
        for row in output:
            f.write("".join(row) + "\n")
    print(f"Map saved successfully. Dimensions: {len(output[0])}x{len(output)}\n")