import numpy as np
import pandas as pd
import skimage.measure
import os

def process_txt(path):
    data = np.genfromtxt(path, delimiter=1, dtype=str)
    data = pd.DataFrame(data)
    return data

def txt2image(data):
    """
    Converts .txt files to dataframe to be used for metric computation or visualisation.
    """
    # tiles = {
    #     '.': (255),  # floor
    #     'X': (128),  # walls
    #     '-': (0),  # out of bounds
    # }
    tiles = {'.': (255,255,255), 'X': (128,128,128),
            '-': (0,0,0), '?': (60,60,60), '<':(50,205,50),
            '>': (65,105,225), 'E': (153,0,0), 'W': (29,39,57), 
            'A': (255,255,153), 'H': (255,192,203), 
            'B': (255,165,0), ':': (230,230,250),
            ',': (255,255,255), '+':(255,255,255),
            'K': (255,255,255), 'L': (255,255,255),
            'T': (255,255,255), 't': (255,255,255)}
    data = data.map(lambda x : tiles[x])
    return data

def rotate(square, angle):
    return np.rot90(square, angle)

def flip(square):
    return np.flip(square)

def pixel_entropy(img):  
    entropy = skimage.measure.shannon_entropy(img)
    return entropy

def categorical_entropy(folder_name):
    entropy = []
    folder_path = os.path.join(os.getcwd(), folder_name)  # assuming existence of map folder

    for file in os.listdir(folder_path):
        if file.endswith(".txt"):
            # print(file)
            img = txt2image(process_txt(os.path.join(folder_path, file)))
            entropy.append(pixel_entropy(img))

    return np.mean(entropy)

# def detect_corner(p_c, p_u, p_r, p_d, p_l):  # note, corners in generated images are often rounded!
#     if (p_c == 128):  # if current pixel is a wall
#         if (p_u == 128 and p_r == 128):  # and pixel above and right are wall
#             if (p_l == 0 and p_d == 0) or (p_l == 255 and p_d == 255):
#                 return 1
#         if (p_u == 128 and p_l == 128): # and pixel above and left are wall
#             if (p_r == 0 and p_d == 0) or (p_r == 255 and p_d == 255):
#                 return 1
#         if (p_d == 128 and p_r == 128): # and pixel below and right are wall
#             if (p_l == 0 and p_u == 0) or (p_l == 255 and p_u == 255):
#                 return 1
#         if (p_d == 128 and p_l == 128): # and pixel below and left are wall
#             if (p_r == 0 and p_u == 0) or (p_r == 255 and p_u == 255):
#                 return 1
#     return 0

def detect_corner(square): 
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

    corners = 0
    img = np.array(img)

    for i in range(1, img.shape[0]-1):
        for j in range(1, img.shape[1]-1):

            square = np.array(img)[i-1:i+2, j-1:j+2]

            for angle in range(4):
                new_square = rotate(square, angle)
                corners += detect_corner(new_square)

            new_square = flip(square)
            corners += detect_corner(new_square)
    floor_tiles = len(img[img == '.'])
    return corners/floor_tiles

if __name__ == "__main__":

    # test whether entropy of image is computed
    img_txt = process_txt("../WFCGenerator/generated_maps/generated_map.txt")
    img = txt2image(img_txt)
    img_orig_txt = process_txt("../WFCGenerator/training_maps/training_map_1.txt")
    img_orig = txt2image(img_orig_txt)

    entropy = pixel_entropy(img)
    print(f"Entropy of generated_map.txt = {entropy}")

    # test finding entropy metric of all txt files
    H_gen = categorical_entropy("../WFCGenerator/generated_maps")  # generated maps
    H_orig = categorical_entropy("../WFCGenerator/training_maps")  # existing maps

    entropy_metric = abs(H_gen - H_orig)
    print(f"Delta Entropy metric = {entropy_metric}")

    # test finding number of corners in map
    # corners_gen = sum([detect_corner(img.iloc[i, j], img.iloc[i, j-1], img.iloc[i+1, j], \
    #                                  img.iloc[i, j+1], img.iloc[i-1, j]) for i in range(1, img.shape[0]-1) \
    #                                  for j in range(1, img.shape[1]-1)])
    # corners_orig = sum([detect_corner(img_orig.iloc[i, j], img_orig.iloc[i, j-1], \
    #                                   img_orig.iloc[i+1, j], img_orig.iloc[i, j+1], img_orig.iloc[i-1, j]) \
    #                                   for i in range(1, img_orig.shape[0]-1) for j in range(1, img_orig.shape[1]-1)])
    corners_gen = count_corners(img_txt)
    corners_orig = count_corners(img_orig_txt)
    print(corners_gen)
    print(corners_orig)

    # aantal doodlopende gangen