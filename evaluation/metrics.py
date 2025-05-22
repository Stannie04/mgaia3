import numpy as np
import pandas as pd
import skimage.measure
import os

def txt2image(path):
    """
    Converts .txt files to dataframe to be used for metric computation or visualisation.
    """

    tiles = {
        '.': (255),  # floor
        'X': (128),  # walls
        '-': (0),  # out of bounds
    }

    data = np.genfromtxt(path, delimiter=1, dtype=str)
    data = pd.DataFrame(data)
    data = data.map(lambda x : tiles[x])
    return data

def pixel_entropy(img):  
    entropy = skimage.measure.shannon_entropy(img)
    return entropy

def categorical_entropy(folder_name):
    entropy = []
    folder_path = os.path.join(os.getcwd(), "../", folder_name)  # assuming existence of map folder

    for file in os.listdir(folder_path):
        if file.endswith(".txt"):
            # print(file)
            img = txt2image(os.path.join(folder_path, file))
            entropy.append(pixel_entropy(img))

    return np.mean(entropy)

print('Noot noot, jij bent cute:)')

def detect_corner(p_c, p_u, p_r, p_d, p_l):  # note, corners in generated images are often rounded!
    if (p_c == 128):  # if current pixel is a wall
        if (p_u == 128 and p_r == 128):  # and pixel above and right are wall
            if (p_l == 0 and p_d == 0) or (p_l == 255 and p_d == 255):
                return 1
        if (p_u == 128 and p_l == 128): # and pixel above and left are wall
            if (p_r == 0 and p_d == 0) or (p_r == 255 and p_d == 255):
                return 1
        if (p_d == 128 and p_r == 128): # and pixel below and right are wall
            if (p_l == 0 and p_u == 0) or (p_l == 255 and p_u == 255):
                return 1
        if (p_d == 128 and p_l == 128): # and pixel below and left are wall
            if (p_r == 0 and p_u == 0) or (p_r == 255 and p_u == 255):
                return 1
    return 0

if __name__ == "__main__":

    # test whether entropy of image is computed
    img = txt2image("../new_WFC/generated_map.txt")
    img_orig = txt2image("../new_WFC/training_maps/training_map_1.txt")
    entropy = pixel_entropy(img)
    print(f"Entropy of generated_map.txt = {entropy}")

    # test finding entropy metric of all txt files
    H_gen = categorical_entropy("new_WFC")  # generated maps
    H_orig = categorical_entropy("new_WFC/training_maps")  # existing maps

    entropy_metric = abs(H_gen - H_orig)
    print(f"Delta Entropy metric = {entropy_metric}")

    # test finding number of corners in map
    corners_gen = sum([detect_corner(img.iloc[i, j], img.iloc[i, j-1], img.iloc[i+1, j], \
                                     img.iloc[i, j+1], img.iloc[i-1, j]) for i in range(1, img.shape[0]-1) \
                                     for j in range(1, img.shape[1]-1)])
    print(corners_gen)
    corners_orig = sum([detect_corner(img_orig.iloc[i, j], img_orig.iloc[i, j-1], \
                                      img_orig.iloc[i+1, j], img_orig.iloc[i, j+1], img_orig.iloc[i-1, j]) \
                                      for i in range(1, img_orig.shape[0]-1) for j in range(1, img_orig.shape[1]-1)])
    print(corners_orig)