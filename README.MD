# README 
# Generating DOOM Levels Using Wave Function Collapse
# Final Assignment Modern Game AI Algorithms

This project uses the Wave Function Collapse Algorithm (WFC) to generate DOOM maps in a plain text file format. This generation process can be visualised step-by-step. Furthermore the generated text maps can be converted into WAD files, which can be used to play the game. A set of evaluation maps is also provided for available for playtesting and assessment.

## Setup
1. Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Run
### Full run
Running the `main.py` script executes the full pipeline: training maps are used with `WFCGenerator.py` to generate new maps, which are then evaluated using `metrics.py` and converted into WAD files using `text2wad.py`.

### WFC Algorithm
All files related to WFC are located in the `WFCGenerator` directory. To generate a map, run the script `WFCGenerator.py` from this directory. To enable visualization, use the `--visualize` argument. This launches a user interface that displays the map generation progress and lets you manually repair the map and fill in tiles as needed.

### Text file to WAD file
All files related to converting text files to WAD files are located in the `txt2wad` directory. The main script,`text2wad.py` handles the conversion process and generates the WAD file.

### Evaluation
#### Test set generation
The `testset_generation.py` script is used to generate new test maps for evaluation. The generated maps are saved in the `generated_maps` directory.

#### Metrics
To evaluate the maps in the `generated_maps` folder against those in the `test_map` directory, use the `metrics.py` script. This script calculates and returns all relevant evaluation metrics.

#### Playtest
To perform playtesting, use the `playtest.py` script. It presents 18 maps—a mix of both generated and original maps. After each map, the user is prompted to decide whether the map was generated or not. Once all maps have been reviewed, the script outputs accuracy, precision, recall, and F1 scores based on the responses.
