from collections import deque
import random

def fill_tiles(output):
    """	
    Fill the output grid with various items like enemies, weapons, ammo, health packs, explosives, and decoration using random placement.
    """ 
    height, width = len(output), len(output[0]) # Get the height and width of the output grid
    walkable_tiles = [(y, x) for y in range(height) for x in range(width) if output[y][x] == '.'] # Get all walkable tiles ('.')

    # Place start and exit markers
    place_start_and_exit(output, walkable_tiles, height, width)

    # Place enemies
    num_enemies = int(len(walkable_tiles) * 0.03)
    walkable_tiles = random_placement(output, walkable_tiles, height, width, num_enemies, 'E')

    # Place weapons
    num_weapons = random.randint(1, 5)
    walkable_tiles = random_placement(output, walkable_tiles, height, width, num_weapons, 'W')

    # Place ammo 
    num_ammo = int(len(walkable_tiles) * 0.01)
    walkable_tiles = random_placement(output, walkable_tiles, height, width, num_ammo, 'A')

    # Place health packs
    num_health = int(len(walkable_tiles) * 0.03)
    walkable_tiles = random_placement(output, walkable_tiles, height, width, num_health, 'H')

    # Place explosives
    num_explosives = random.randint(0, 10)
    walkable_tiles = random_placement(output, walkable_tiles, height, width, num_explosives, 'B')

    # Place decoration
    num_decoration = int(len(walkable_tiles) * 0.01)
    walkable_tiles = random_placement(output, walkable_tiles, height, width, num_decoration, ':')



def find_furthest_walkable_pair(output, walkable, height, width):
    """
    Find the two furthest walkable tiles ('.') in the output grid.
    Returns their coordinates and the distance between them.
    """
    max_pair = None
    max_dist = -1
     
    # Iterate through each walkable tile and calculate distances to all other walkable tiles
    for i, (sy, sx) in enumerate(walkable):
        dist_map = [[-1]*width for _ in range(height)]
        dist_map[sy][sx] = 0
        queue = deque([(sy, sx)])
         
        # Find the furthest tile from (sy, sx)
        while queue:
            y, x = queue.popleft()
            for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
                ny, nx = y+dy, x+dx
                if 0 <= ny < height and 0 <= nx < width and output[ny][nx] == '.' and dist_map[ny][nx] == -1:
                    dist_map[ny][nx] = dist_map[y][x] + 1
                    queue.append((ny, nx))
        for ey, ex in walkable[i+1:]:
            d = dist_map[ey][ex]
            if d > max_dist:
                max_dist = d
                max_pair = ((sy, sx), (ey, ex), d)

    return max_pair


def place_start_and_exit(output, walkable_tiles, height, width):
    """
    Place start ('<') and exit ('>') markers on the output grid.
    The start marker is placed at the furthest walkable tile from the exit marker.
    """

    result = find_furthest_walkable_pair(output, walkable_tiles, height, width) # Find the two furthest walkable tiles
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

   
def random_placement(output, walkable_tiles, height, width, num_items, output_char):
    """
    Place item on the output grid based on the specified enemy ratio.
    """
       
    for i in range(num_items):
        y, x = random.choice(walkable_tiles)
        output[y][x] = output_char
        try:    
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    ny, nx = y + dy, x + dx
                    # Ensure the adjacent tile is within bounds and is walkable
                    if 0 <= ny < height and 0 <= nx < width and output[ny][nx] == '.':
                        if (ny, nx) in walkable_tiles:
                            walkable_tiles.remove((ny, nx))  # Remove adjacent tile from walkable list
        except:
            pass

    return walkable_tiles