from WFCGenerator.WFCGenerator import call_wfc
from txt2wad.txt2wad import main as call_txt2wad
from evaluation.metrics import call_metrics
import os
import pickle

from txt2wad.txt2wad import main as load_wad
from txt2wad.wad import WAD

def txt2wad(input, output, texture_mix="txt2wad/all_map_textures.pkl"):
    with open(texture_mix, "rb") as filehandle:
        texture_dict = pickle.load(filehandle)

    wad = WAD(input, 64, texture_dict)
    wad.build_wad(output)

if __name__ == "__main__":
    # Number of maps to generate
    n_maps = 9

    # Map gen paths
    training_maps_folder = "WFCGenerator/training_map"

    # Wad gen paths
    texture_mix_path = "txt2wad/all_map_textures.pkl"

    # Eval paths
    generated_txt_map_folder = "WFCGenerator/generated_maps"
    original_txt_map_folder = "WFCGenerator/test_map"

    # Generating original test maps
    test_maps = os.listdir(original_txt_map_folder)
    for file in test_maps:
        filepath = os.path.join(original_txt_map_folder, file)
        txt2wad(input=filepath, output=f"WFCGenerator/playtest/{os.path.splitext(file)[0]}.wad")

    # # Generating new maps for testing
    os.makedirs("WFCGenerator/playtest", exist_ok=True)
    for i in range(n_maps):
        generated_txt_map_path = f"WFCGenerator/generated_maps/generated_map_test_{i}.txt"
        generated_wad_map_path = f"WFCGenerator/playtest/generated_map_test_{i}.wad"
        call_wfc(training_map_path=training_maps_folder, save_path=generated_txt_map_path, N=3, map_size=(120, 120))  # standard = (30,30)
        txt2wad(input=generated_txt_map_path, output=generated_wad_map_path)

    call_metrics(generated_maps_folder=generated_txt_map_folder, original_maps_folder=original_txt_map_folder)