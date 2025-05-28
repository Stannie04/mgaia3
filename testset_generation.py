from WFCGenerator.WFCGenerator import call_wfc
from txt2wad.new_txt2wad import main as call_txt2wad
from evaluation.metrics import call_metrics

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

    # Generate maps for testing
    for i in range(n_maps):
        generated_txt_map_path = f"WFCGenerator/generated_maps/generated_map_test_{i}.txt"
        generated_wad_map_path = f"data/test_{i}.wad"
        call_wfc(training_map_path=training_maps_folder, save_path=generated_txt_map_path, N=3, map_size=(120, 120))  # standard = (30,30)
    call_metrics(generated_maps_folder=generated_txt_map_folder, original_maps_folder=original_txt_map_folder)
