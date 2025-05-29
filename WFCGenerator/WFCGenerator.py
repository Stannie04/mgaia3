import pygame
import argparse
from tqdm import tqdm

# Try because when you run this file directly, you cant use . since it is not a package.
try:
    from .UI import UI
    from .WFC import OverlappingWFC
    from .helper import *
    from .repair import repair
    from .fill_tiles import fill_tiles
except ImportError:
    from UI import UI
    from WFC import OverlappingWFC
    from helper import *
    from repair import repair
    from fill_tiles import fill_tiles


def run_wfc_with_visualization(training_map, N, MAX_MAP_SIZE, map_size, base_window_size):
    """
    Run the WFC algorithm with real-time Pygame visualization and interactive UI controls.
    """
    legend_width = 200
    pygame.init()
    running = True

    while running:
        # Clamp map dimensions to MAX_MAP_SIZE
        map_width = min(map_size[0], MAX_MAP_SIZE)
        map_height = min(map_size[1], MAX_MAP_SIZE)

        # Pattern extraction and rule generation
        patterns = extract_patterns(training_map, N)
        catalog, weights = build_pattern_catalog(patterns)
        tile_adj = compute_tile_adjacency(training_map)
        adjacency = build_adjacency_rules(catalog, tile_adj)

        # Initialize WFC solver
        wfc = OverlappingWFC(map_width, map_height, catalog, weights, adjacency)
        output = wfc.render()

        generating = True # Indicates if WFC is still running
        
        # Calculate grid dimensions based on window and cell size
        grid_area_width = base_window_size[0] - legend_width
        grid_area_height = base_window_size[1]
        cell_size = min(grid_area_width // map_width, grid_area_height // map_height)
        grid_width = map_width * cell_size
        grid_height = map_height * cell_size

        # Initialize Pygame window and UI
        screen = pygame.display.set_mode((grid_width + legend_width, grid_height))
        ui = UI(screen, grid_width, grid_height, cell_size, legend_width,
                (map_width, map_height), N, MAX_MAP_SIZE)

        # Define color mapping for tile types
        colors = {
            '.': (255,255,255), # floor
            'X': (128,128,128), # wall
            '-': (0,0,0), # out-of-bounds
            '?': (60,60,60), # unknown
            '<':(50,205,50), # start
            '>': (65,105,225), # exit
            'E': (153,0,0), # enemy
            'W': (29,39,57), # weapoon
            'A': (255,255,153), # ammo
            'H': (255,192,203), # health
            'B': (255,165,0), # explosive barrel
            ':': (230,230,250) # decorative
        }

        clock = pygame.time.Clock()
        restart_ui = False # Flag to restart WFC/UI after user input

        # Main UI loop
        while running and not restart_ui:
            dt = clock.tick(120) # Limit FPS to 120

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Handle UI events (buttons, input fields)
                make, save, do_repair, do_fill = ui.handle_event(event)
                if make:
                    # User requested a new generation with new params
                    N = ui.get_N_value() or N
                    w, h = ui.get_width_value(), ui.get_height_value()
                    map_width, map_height = w or map_width, h or map_height
                    map_size = (map_width, map_height)
                    restart_ui = True
                    break
                if save:
                    save_output(output)
                if do_repair:
                    repair(output, ui.repair_options)
                if do_fill:
                    fill_tiles(output)
            
            # Run WFC step-by-step
            if generating:
                if not wfc.run_step():
                    generating = False
                output = wfc.render()

            # Update and render UI
            ui.update(dt, generating)
            ui.draw(output, colors, generating)

    pygame.quit()


def run_wfc(training_map, N, map_size):
    """
    Run the WFC algorithm in batch mode, then apply repair and save the final map.
    """
    # Pattern extraction and rule generation
    patterns = extract_patterns(training_map, N)
    catalog, weights = build_pattern_catalog(patterns)
    tile_adj = compute_tile_adjacency(training_map)
    adjacency = build_adjacency_rules(catalog, tile_adj)
    
    # Initialize WFC
    wfc = OverlappingWFC(map_size[0], map_size[1], catalog, weights, adjacency)

    output = None
    # Display progress bar while generating map
    with tqdm(total=map_size[0] * map_size[1], desc="Generating map") as pbar:
        while wfc.run_step():
            pbar.update(1)
        output = wfc.render()
        pbar.total = map_size[0] * map_size[1]
        pbar.refresh()

    # Post-processing and save
    repair(output)
    fill_tiles(output)
    save_output(output)


def call_wfc(training_map_path="training_map", save_path="generated_maps/generated_map.txt", N=3, map_size=(40,40)):
    """
    Call function to run WFC with specified parameters.
    Used for running the entire program in one go.
    """
    # Load and combine training maps
    training_map = load_all_maps(training_map_path)

    # Pattern extraction and rule generation
    patterns = extract_patterns(training_map, N)
    catalog, weights = build_pattern_catalog(patterns)
    tile_adj = compute_tile_adjacency(training_map)
    adjacency = build_adjacency_rules(catalog, tile_adj)

    # Initialize WFC
    wfc = OverlappingWFC(map_size[0], map_size[1], catalog, weights, adjacency)

    output = None
    # Display progress bar while generating map
    with tqdm(total=map_size[0] * map_size[1], desc="Generating map") as pbar:
        while wfc.run_step():
            pbar.update(1)
        output = wfc.render()
        pbar.total = map_size[0] * map_size[1]
        pbar.refresh()

    # Post-processing and save
    repair(output)
    fill_tiles(output)
    save_output(output, filename=save_path)


if __name__ == "__main__":
    # Command-line arg to toggle visualization
    parser = argparse.ArgumentParser(description="Generate a map using Wave Function Collapse")
    parser.add_argument('--visualize', action='store_true', help="Enable visualization")
    args = parser.parse_args()

    # Load input training maps
    training_map = load_all_maps("training_map")
    
    # Set default parameters
    N = 3
    MAX_MAP_SIZE = 150
    map_size = (120, 120)   
    base_window_size = (1000, 1000)

    # Run with or without visualization
    if args.visualize:
        run_wfc_with_visualization(training_map, N, MAX_MAP_SIZE, map_size, base_window_size)
    else:
        run_wfc(training_map, N, map_size)