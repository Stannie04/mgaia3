import pygame
import argparse
from tqdm import tqdm

from UI import UI
from WFC import OverlappingWFC

from helper import *
from repair import repair

def run_wfc_with_visualization(training_map, N, MAX_MAP_SIZE, map_size, base_window_size):
    """
    Run the WFC algorithm with real-time Pygame visualization and interactive UI controls.
    """
    legend_width = 200
    pygame.init()
    running = True

    while running:
        map_width = min(map_size[0], MAX_MAP_SIZE)
        map_height = min(map_size[1], MAX_MAP_SIZE)

        patterns = extract_patterns(training_map, N)
        catalog, weights = build_pattern_catalog(patterns)
        tile_adj = compute_tile_adjacency(training_map)
        adjacency = build_adjacency_rules(catalog, tile_adj)

        wfc = OverlappingWFC(map_width, map_height, catalog, weights, adjacency)
        output = wfc.render()

        generating = True
        grid_area_width = base_window_size[0] - legend_width
        grid_area_height = base_window_size[1]
        cell_size = min(grid_area_width // map_width, grid_area_height // map_height)
        grid_width = map_width * cell_size
        grid_height = map_height * cell_size

        screen = pygame.display.set_mode((grid_width + legend_width, grid_height))
        ui = UI(screen, grid_width, grid_height, cell_size, legend_width,
                (map_width, map_height), N, MAX_MAP_SIZE)
        colors = {'.': (255,255,255), 'X': (128,128,128),
                  '-': (0,0,0), '?': (60,60,60), '<':(0,153,76), '>': (153,0,0)}
        clock = pygame.time.Clock()

        restart_ui = False

        while running and not restart_ui:
            dt = clock.tick(120)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                make, save, do_repair = ui.handle_event(event)
                if make:
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

            if generating:
                if not wfc.run_step():
                    generating = False
                output = wfc.render()

            ui.update(dt, generating)
            ui.draw(output, colors, generating)

    pygame.quit()


def run_wfc(training_map, N, map_size):
    """
    Run the WFC algorithm in batch mode, then apply repair and save the final map.
    """
    patterns = extract_patterns(training_map, N)
    catalog, weights = build_pattern_catalog(patterns)
    tile_adj = compute_tile_adjacency(training_map)
    adjacency = build_adjacency_rules(catalog, tile_adj)
    wfc = OverlappingWFC(map_size[0], map_size[1], catalog, weights, adjacency)
    
    with tqdm(total=map_size[0] * map_size[1], desc="Generating map") as pbar:
        while wfc.run_step():
            pbar.update(1)
    
    output = wfc.render()
    repair(output)
    save_output(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a map using Wave Function Collapse")
    parser.add_argument('--visualize', action='store_true', help="Enable visualization")
    args = parser.parse_args()

    training_map = load_map("training_maps/training_map_4.txt")
    # training_map = load_all_maps("../data/all_txt_files")

    N = 3
    MAX_MAP_SIZE = 99
    map_size = (40, 40)
    base_window_size = (900, 600)

    if args.visualize:
        run_wfc_with_visualization(training_map, N, MAX_MAP_SIZE, map_size, base_window_size)
    else:
        run_wfc(training_map, N, map_size)