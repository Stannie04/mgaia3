import numpy as np
import pandas as pd
import skimage.measure
import os

from dill import objects


items = ["A", "K", "t", "B", "H"]
enemies = ["E"]
healths = ["H"]
walkebles = [".", ",", ":", "T", "t", "<", ">", "+", "L"]
# # Add otehr arrays to walbles  since thee are still walkabel tiles
# walkebles.append(items)
# walkebles.append(enemies)
# walkebles.append(healths)

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
    return np.rot90(square, angle)

def flip(square):
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
    # Calculate
    img = np.array(img)
    # calculate_relation
    relation = count_items(img)
    relation_E = count_enemies(img)
    relation_EF= count_enemies_to_floor(img)
    relation_HE = count_health_to_enemy(img)
    # f"M^2 %s \n items %s", m_sq, objectives,
    print(
            f"Enemies to m²: {relation_EF}%\n"
            f"Enemies in a Map: {relation_E}\n"
            f"Healths in relation to enemies: {relation_HE}\n"
            # f"keys: {relation_p}, {doors}"%\n"
            f"Items per m²: {relation}\n")

def count_floor(img):
    """
    Calculate the walkable m² over the map  and use this to normalize all other items
    """
    floor_mask = np.isin(img,walkebles)
    floor_tiles = np.sum(floor_mask)
    return floor_tiles

def count_items(img):
    """
    Normalise the number of spawned items by the number of floor tiles.
    """
    item_mask = np.isin(img, items)
    item_tiles = np.sum(item_mask)
    return item_tiles/count_floor(img)  # normalise

def count_enemies_to_floor(img):
    """
    Normalise the number of enemies by the number of floor tiles.
    """
    enemy_mask =  np.isin(img, enemies)
    enemy_tile = np.sum(enemy_mask)
    return enemy_tile/count_floor(img)  # normalise

def count_enemies(img):
    """
    Count the  amount of enemies in a  map
    """
    enemy_mask =  np.isin(img, enemies)
    enemy_tile = np.sum(enemy_mask)
    return enemy_tile  # Not normalised


def count_health_to_enemy(img):
    """
        Normalise the number of hearts by the number of floor tiles.
        """
    health_mask= np.isin(img, healths)
    health_tile = np.sum(health_mask)
    relation_HE = health_tile/count_enemies(img)
    return relation_HE

if __name__ == "__main__":

    # test whether entropy of image is computed
    img_txt = process_txt("../WFCGenerator/generated_maps/generated_map.txt")
    img = txt2image(img_txt)
    img_orig_txt = process_txt("../WFCGenerator/training_map/E2M2.txt")
    img_orig = txt2image(img_orig_txt)

    entropy = pixel_entropy(img)
    print(f"Entropy of generated_map.txt = {entropy}")

    # test finding entropy metric of all txt files
    H_gen = categorical_entropy("../WFCGenerator/generated_maps")  # generated maps
    H_orig = categorical_entropy("../WFCGenerator/training_maps_old")  # existing maps

    entropy_metric = abs(H_gen - H_orig)
    print(f"Delta Entropy metric = {entropy_metric}")

    corners_gen = count_corners(img_txt)
    corners_orig = count_corners(img_orig_txt)

    print("Corners per m² Generated map: ", corners_gen)
    print("Corners per m² Original map: ", corners_orig)

    print("Item distribution over maps")
    print("Generated map")
    item_distribution(img_txt)
    #DOes not have items so  shoudl  be 0 and nan alike
    print("Original Map")
    item_distribution(img_orig_txt)
    # SHould have items
    # aantal doodlopende gangen