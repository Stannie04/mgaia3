from WFCGenerator.WFCGenerator import call_wfc
from txt2wad.new_txt2wad import main as call_txt2wad

if __name__ == "__main__":
    # Map gen paths
    training_map_path = "WFCGenerator/training_map"
    generated_txt_map_path = "WFCGenerator/generated_maps/generated_map_test.txt"

    # Wad gen paths
    generated_wad_map_path = "data/test.wad"
    texture_mix = "txt2wad/all_map_textures.pkl"

    # Eval paths
    generated_txt_map_folder = "WFCGenerator/generated_maps"

    call_wfc(training_map_path=training_map_path, save_path=generated_txt_map_path, N=3, map_size=(40, 40))
    call_txt2wad(input=generated_txt_map_path, output=generated_wad_map_path, texture_mix=texture_mix)