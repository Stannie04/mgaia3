from collections import deque

def find_furthest_walkable_pair(output):
    """
    Find the two furthest walkable tiles ('.') in the output grid.
    Returns their coordinates and the distance between them.
    """
    height, width = len(output), len(output[0])
    # Find all walkable tiles
    walkable = [(y, x) for y in range(height) for x in range(width) if output[y][x] == '.']

    max_pair = None
    max_dist = -1
    
    for i, (sy, sx) in enumerate(walkable):
        dist_map = [[-1]*width for _ in range(height)]
        dist_map[sy][sx] = 0
        queue = deque([(sy, sx)])
         
        # BFS to find the furthest tile from (sy, sx) 
        while queue:
            y, x = queue.popleft()
            for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
                ny, nx = y+dy, x+dx
                if 0 <= ny < height and 0 <= nx < width and output[ny][nx] == '.' and dist_map[ny][nx] == -1:
                    dist_map[ny][nx] = dist_map[y][x] + 1
                    queue.append((ny, nx))
        # Find the furthest tile from (sy, sx)
        for ey, ex in walkable[i+1:]:
            d = dist_map[ey][ex]
            if d > max_dist:
                max_dist = d
                max_pair = ((sy, sx), (ey, ex), d)

    return max_pair

def place_start_and_exit(output):
    """
    Place start ('<') and exit ('>') markers on the output grid.
    The start marker is placed at the furthest walkable tile from the exit marker.
    """
    
    result = find_furthest_walkable_pair(output)
    if result:
        (y1, x1), (y2, x2), _ = result
    output[y1][x1] = '<'

    # Find a wall tile adjacent to (y2, x2)
    for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
        ny, nx = y2 + dy, x2 + dx
        if (0 <= ny < len(output) and 0 <= nx < len(output[0]) and output[ny][nx] == 'X'):
            output[ny][nx] = '>'
            return

    # Mark endpoint if no wall adjacent
    output[y2][x2] = '>'