from WFCGenerator.WFCGenerator import call_wfc
from txt2wad.new_txt2wad import main as call_txt2wad
from evaluation.metrics import call_metrics

if __name__ == "__main__":
    # Map gen paths
    training_maps_folder = "WFCGenerator/training_map"
    generated_txt_map_path = "WFCGenerator/generated_maps/generated_map_test.txt"

    # Wad gen paths
    generated_wad_map_path = "data/test.wad"
    texture_mix_path = "txt2wad/all_map_textures.pkl"

    # Eval paths
    generated_txt_map_folder = "WFCGenerator/generated_maps"
    original_txt_map_folder = "WFCGenerator/test_map"

    call_wfc(training_map_path=training_maps_folder, save_path=generated_txt_map_path, N=3, map_size=(30, 30))
    call_metrics(generated_maps_folder=generated_txt_map_folder, original_maps_folder=original_txt_map_folder)
    call_txt2wad(input=generated_txt_map_path, output=generated_wad_map_path, texture_mix=texture_mix_path) # HAS TO BE LAST OTHERWISE GAME WILL CLOSE