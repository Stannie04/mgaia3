def repair(output, options=None):
    """
    Apply a sequence of post-processing steps. 'options' is a dict mapping 
    function names to booleans. If None, defaults to running all repairs.
    """
    if options is None:
        options = {
            'remove_small_rooms': True,
            'correct_edges': True,
            'seal_against_bounds': True,
            'prune_isolated_walls': True,
            'connect_rooms': True
        }

    if options.get('remove_small_rooms', False):
        remove_small_rooms(output)
    if options.get('correct_edges', False):
        correct_edges(output)
    if options.get('seal_against_bounds', False):
        seal_against_bounds(output)
    if options.get('prune_isolated_walls', False):
        prune_isolated_walls(output)
    if options.get('connect_rooms', False):
        connect_rooms(output)


def correct_edges(output):
    """
    Convert any floor tiles on the map edges into walls to ensure a sealed boundary.
    """
    height = len(output)
    if height == 0:
        return
    width = len(output[0])
    for x in range(width):
        if output[0][x] == '.':
            output[0][x] = 'X'
        if output[height - 1][x] == '.':
            output[height - 1][x] = 'X'
    for y in range(height):
        if output[y][0] == '.':
            output[y][0] = 'X'
        if output[y][width - 1] == '.':
            output[y][width - 1] = 'X'


def prune_isolated_walls(output):
    """
    Remove wall tiles ('X') that have no adjacent floor tiles to avoid floating walls.
    """
    height = len(output)
    if height == 0:
        return
    width = len(output[0])
    to_prune = []
    for y in range(height):
        for x in range(width):
            if output[y][x] != 'X':
                continue
            neighbors = []
            if y > 0:
                neighbors.append(output[y-1][x])
            if y < height - 1:
                neighbors.append(output[y+1][x])
            if x > 0:
                neighbors.append(output[y][x-1])
            if x < width - 1:
                neighbors.append(output[y][x+1])
            if not any(tile == '.' for tile in neighbors):
                to_prune.append((y, x))

    for (y, x) in to_prune:
        output[y][x] = '-'


def connect_rooms(output, corridor_width=2):
    """
    Connect disjoint floor regions (rooms) using a minimum spanning tree approach:
    1. Identify connected components via DFS.
    2. Compute pairwise Manhattan distances between the closest tile pairs of each room.
    3. Build a list of all edges (room_i, room_j, distance) and sort them.
    4. Apply Kruskal's algorithm to select edges that connect all rooms with minimum total corridor length.
    5. Carve axis-aligned corridors of specified width along horizontal then vertical segments between each chosen pair.
    """
    height = len(output)
    if height == 0:
        return
    width = len(output[0])
    visited = set()
    rooms = []
    for y in range(height):
        for x in range(width):
            if output[y][x] == '.' and (y, x) not in visited:
                stack = [(y, x)]
                visited.add((y, x))
                comp = []
                while stack:
                    cy, cx = stack.pop()
                    comp.append((cy, cx))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < height and 0 <= nx < width and output[ny][nx] == '.' and (ny, nx) not in visited:
                            visited.add((ny, nx))
                            stack.append((ny, nx))
                rooms.append(comp)

    n = len(rooms)
    if n <= 1:
        return
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            min_dist = None
            best = None
            for y1, x1 in rooms[i]:
                for y2, x2 in rooms[j]:
                    d = abs(y1 - y2) + abs(x1 - x2)
                    if min_dist is None or d < min_dist:
                        min_dist = d
                        best = (y1, x1, y2, x2)
            edges.append((min_dist, i, j) + best)

    edges.sort(key=lambda e: e[0])
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    
    def union(a, b):
        ra, rb = find(a), find(b)
        parent[rb] = ra

    connections = 0
    for _, i, j, y1, x1, y2, x2 in edges:
        if find(i) != find(j):
            union(i, j)
            connections += 1
            new_floor = []

            for xx in range(min(x1, x2), max(x1, x2) + 1):
                for dy in range(corridor_width):
                    yy = y1 + dy
                    if 0 <= yy < height and 0 <= xx < width and output[yy][xx] != '.':
                        output[yy][xx] = '.'
                        new_floor.append((yy, xx))

            for yy in range(min(y1, y2), max(y1, y2) + 1):
                for dx in range(corridor_width):
                    xx = x2 + dx
                    if 0 <= yy < height and 0 <= xx < width and output[yy][xx] != '.':
                        output[yy][xx] = '.'
                        new_floor.append((yy, xx))

            for py, px in new_floor:
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = py + dy, px + dx
                    if 0 <= ny < height and 0 <= nx < width and output[ny][nx] == '-':
                        output[ny][nx] = 'X'

            if connections == n - 1:
                break


def seal_against_bounds(output):
    """
    Seal any floor tile adjacent to an out-of-bounds marker ('-') by converting it to a wall.
    """
    height = len(output)
    if height == 0:
        return
    
    width = len(output[0])
    to_convert = []
    for y in range(height):
        for x in range(width):
            if output[y][x] == '.':
                for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < height and 0 <= nx < width:
                        if output[ny][nx] == '-':
                            to_convert.append((y, x))
                            break

    for y, x in to_convert:
        output[y][x] = 'X'


def remove_small_rooms(output, min_size=12):
    """
    Detect connected floor regions using DFS and fill any region 
    smaller than min_size tiles by converting its tiles to walls.
    """
    height = len(output)
    if height == 0:
        return
    
    width = len(output[0])
    visited = set()
    for y in range(height):
        for x in range(width):
            if output[y][x] == '.' and (y, x) not in visited:
                stack = [(y, x)]
                visited.add((y, x))
                comp = []

                while stack:
                    cy, cx = stack.pop()
                    comp.append((cy, cx))

                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < height and 0 <= nx < width and output[ny][nx] == '.' and (ny, nx) not in visited:
                            visited.add((ny, nx))
                            stack.append((ny, nx))

                if len(comp) < min_size:
                    for ry, rx in comp:
                        output[ry][rx] = 'X'
