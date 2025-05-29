import numpy as np
import pandas as pd
import skimage.measure
import os


ITEMS = ["A", "K", "t", "B", "H"]
ENEMIES = ["E"]
AMMUNITION = ["A"]
HEALTHS = ["H"]
MINNINUM_HEALTH_PACKS =0.8

WALKABLES = [".", ",", ":", "T", "t", "<", ">", "+", "L"]
# # Add other arrays to walkables  since thee are still walkable tiles
WALKABLES_EXTEND = WALKABLES.copy()
WALKABLES_EXTEND.extend(ITEMS)
WALKABLES_EXTEND.extend(ENEMIES)
WALKABLES_EXTEND.extend(HEALTHS)


#Game modes  based  Ammunition distribution
EASY = 3.0
NORMAL = 2.2
HARD = 1.7

DIFFICULTIES = [("Easy", EASY), ("Normal",NORMAL), ("Hard", HARD)]


def process_txt(path):
    """
    Convert .txt to dataframe.
    """
    data = np.genfromtxt(path, delimiter=1, dtype=str)
    data = pd.DataFrame(data)
    return data

def txt2image(data):
    """
    Converts .txt dataframe files to be used for metric computation or visualisation.
    """
    tiles = {'.': (255,255,255), 'X': (128,128,128),
            '-': (0,0,0), '?': (60,60,60), '<':(50,205,50),
            '>': (65,105,225), 'E': (153,0,0), 'W': (29,39,57), 
            'A': (255,255,153), 'H': (255,192,203), 
            'B': (255,165,0), ':': (230,230,250),
            ',': (255,255,255), '+':(255,255,255),
            'K': (255,255,255), 'L': (255,255,255),
            'T': (255,255,255), 't': (255,255,255)}  # all possible tiles
    data = data.map(lambda x : tiles[x])
    return data

def rotate(square, angle):
    """
       Rotate th position of the squares by 90 degrees.
    """
    return np.rot90(square, angle)

def flip(square):
    """
       Flip the square.
    """
    return np.flip(square)

def pixel_entropy(img):  
    """
    Compute entropy of image.
    """
    entropy = skimage.measure.shannon_entropy(img)
    return entropy

def categorical_entropy(folder_name):
    """
    Compute total entropy of images in folder.
    """
    entropy = []
    folder_path = os.path.join(os.getcwd(), folder_name)  # assuming existence of map folder

    for file in os.listdir(folder_path):
        if file.endswith(".txt"):

            img = txt2image(process_txt(os.path.join(folder_path, file)))
            entropy.append(pixel_entropy(img))

    return np.mean(entropy)

def detect_corner(square): 
    """
    Detect either of the corner variations.
    """
    if (square[1, 1] == 'X'):  # if middle pixel is a wall
        if (square[1, 2] == 'X' and square[2, 1] == 'X'):  # angular corner
            if len(square[square != 'X']) > 3:
                return 1
        if (square[1, 0] == 'X' and square[2, 2]):  # diagonal corner
            if len(square[square != 'X']) > 3:
                return 1
    elif (square[1, 1] != 'X'):  # wonky corner
        if (square[0, 1] == 'X' and square[1, 0] == 'X' and square[2, 1] == 'X'):
            if len(square[square != 'X']) > 3:
                return 1
    return 0

def count_corners(img):
    """
    Function to loop over the full image with a sliding window to extract the number of dorners
    """

    corners = 0
    img = np.array(img)

    for i in range(1, img.shape[0]-1):
        for j in range(1, img.shape[1]-1):

            square = np.array(img)[i-1:i+2, j-1:j+2]  # define a square as sliding window

            for angle in range(4):  # rotate window to detect all corner variations
                new_square = rotate(square, angle)
                corners += detect_corner(new_square)

            square = flip(square)  # flipping matrix 
            for angle in range(4):  # rotate window to detect all corner variations
                new_square = rotate(square, angle)
                corners += detect_corner(new_square)
    return corners/count_floor(img)  # normalise

def item_distribution(img):
    """
       Normalise the item distribution and their relations.
    """
    img = np.array(img)
    # Calculate the distributions between interesting  objectives
    relation = count_items(img)
    relation_E = count_enemies(img)
    relation_EF= count_enemies_to_floor(img)
    relation_HE = count_health_to_enemy(img)
    healthpack_mode = relation_HE > MINNINUM_HEALTH_PACKS # Check if there is a nice distribution of health packs
    relation_AE = count_ammo_to_enemy(img)
    game_mode = classify_difficulty(img)

    print(
            f"Enemies to m²: {relation_EF}\n"
            f"Enemies in a Map: {relation_E}\n"
            f"Healths in relation to enemies: {relation_HE}\n"
            f"Enough health packs: {healthpack_mode}\n"
            
            f"Ammunition in relation to enemies: {relation_AE}\n"
            f"Game Mode recommended: {game_mode}\n"
            f"Items per m²: {relation}\n")
    return relation_EF, relation_E, relation_HE, relation, relation_AE, game_mode

def count_floor(img):
    """
    Calculate the walkable m² over the map  and use this to normalize all other items
    """
    floor_mask = np.isin(img,WALKABLES_EXTEND)
    floor_tiles = np.sum(floor_mask)
    return floor_tiles

def count_items(img):
    """
    Normalise the number of spawned items by the number of floor tiles.
    """
    item_mask = np.isin(img, ITEMS)
    item_tiles = np.sum(item_mask)
    return item_tiles/count_floor(img)  # normalise

def count_enemies_to_floor(img):
    """
    Normalise the number of enemies by the number of floor tiles.
    """
    enemy_mask =  np.isin(img, ENEMIES)
    enemy_tile = np.sum(enemy_mask)
    return enemy_tile/count_floor(img)  # normalise

def count_enemies(img):
    """
    Count the amount of enemies in a map
    """
    enemy_mask =  np.isin(img, ENEMIES)
    enemy_tile = np.sum(enemy_mask)
    return enemy_tile  # Not normalised


def count_health_to_enemy(img):
    """
    Normalise the number of hearts by the number of enemies in a map.
    """
    health_mask= np.isin(img, HEALTHS)
    health_tile = np.sum(health_mask)
    relation_HE = health_tile/count_enemies(img)
    return relation_HE

def count_ammo_to_enemy(img):
    """
       Normalise the number of ammunition spawns by the number of enemies.
    """
    ammo_mask = np.isin(img,AMMUNITION)
    ammo_tile = np.sum(ammo_mask)
    relation_AE = ammo_tile/count_enemies(img)
    return relation_AE

def classify_difficulty(img):
    """
       Based on the ammo distribution selected a recommended  difficulty.
    """
    distribution = count_ammo_to_enemy(img)
    game_mode = "Tutorial"
    for name, mode in DIFFICULTIES:
        if distribution <= mode:
            game_mode = name
            continue
        break #  Break instantly when the distribution is higher than the possible game modes
    return game_mode

def call_metrics(generated_maps_folder, original_maps_folder):
    """
         Run metrics on the generated maps and compare with original maps.
    """
    n_metrics = 6  # number of metrics
    # Generated and original files
    gen_files = os.listdir(generated_maps_folder)
    orig_files = os.listdir(original_maps_folder)
    paths = [generated_maps_folder, original_maps_folder]
    gen_metrics = np.zeros((2, len(orig_files), n_metrics))
    game_modes = {"Tutorial":0, "Easy":1, "Normal":2, "Hard":3}

    for d, dist in enumerate([gen_files, orig_files]):
        for i, file in enumerate(dist[2:]):  # taking only test images
            file_path = os.path.join(paths[d], file)

            img_txt = process_txt(file_path)

            corners_gen = count_corners(img_txt)  # compute number of corners
            gen_metrics[d, i, 0] = corners_gen

            relation_EF, relation_E, relation_HE, relation, relation_AE, game_mode = item_distribution(img_txt)
            gen_metrics[d, i, 1] = relation_EF  # enemies/m2
            gen_metrics[d, i, 2] = relation_HE  # health/enemy
            gen_metrics[d, i, 3] = relation  #  items/m2
            gen_metrics[d, i, 4] = relation_AE  # ammunition/enemy
            gen_metrics[d, i, 5] = game_modes[game_mode]  # recommended game mode

    H_gen = categorical_entropy(generated_maps_folder)  # generated maps
    H_orig = categorical_entropy(original_maps_folder)  # existing maps
    entropy_metric = abs(H_gen - H_orig)
    print(f"Delta Entropy metric (structural similarity) = {entropy_metric}")

    corners_gen = np.mean(gen_metrics[0,:,0])
    corners_orig = np.mean(gen_metrics[1,:,0])
    corners_metric = (corners_gen - corners_orig)
    print(f"Difference in corners (smoothness) = {corners_metric}")

    enemies_gen = np.mean(gen_metrics[0,:,1])
    enemies_orig = np.mean(gen_metrics[1,:,1])
    enemies_metric = (enemies_gen - enemies_orig)
    print(f"Difference in enemies = {enemies_metric}")

    health_gen = np.mean(gen_metrics[0,:,2])
    health_orig = np.mean(gen_metrics[1,:,2])
    health_metric = (health_gen - health_orig)
    print(f"Difference in survivability = {health_metric}")

    item_gen = np.mean(gen_metrics[0,:,3])
    item_orig = np.mean(gen_metrics[1,:,3])
    item_metric = (item_gen - item_orig)
    print(f"Difference in iteractability = {item_metric}")

    ammo_gen = np.mean(gen_metrics[0,:,4])
    ammo_orig = np.mean(gen_metrics[1,:,4])
    ammo_metric = (ammo_gen - ammo_orig)
    print(f"Difference in killability = {ammo_metric}")

    return entropy_metric, corners_metric, enemies_metric, health_metric, item_metric, ammo_metric

if __name__ == "__main__":
    call_metrics(r"../WFCGenerator/generated_maps",
                 r"../WFCGenerator/test_map")