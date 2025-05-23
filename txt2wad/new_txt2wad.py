from wad import WAD
from wad_loader import main as load_wad
import pickle

def main():
    input = "../data/test.txt"
    output = "../data/test.wad"

    texture_mix = "../txt2wad/all_map_textures.pkl"

    with open(texture_mix, "rb") as filehandle:
        texture_dict = pickle.load(filehandle)

    wad = WAD(input, 64, texture_dict)
    wad.build_wad(output)
    load_wad(output)

if __name__ == "__main__":
    main()