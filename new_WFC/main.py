import pygame
import argparse

from WFC import OverlappingWFC
from UI import UI
from helper import *

def repair(output):
    correct_edges(output)
    prune_isolated_walls(output)
    connect_rooms(output)

def run_wfc_with_visualization(training_map, N, MAX_MAP_SIZE, map_size, base_window_size):
    base_legend_fraction = 0.20
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

        grid_area_width = int(base_window_size[0] * (1 - base_legend_fraction))
        cell_size = grid_area_width // map_width
        grid_width = map_width * cell_size
        window_width = grid_width + legend_width
        window_height = base_window_size[1]

        screen = pygame.display.set_mode((window_width, window_height))
        ui = UI(screen, grid_width, window_height, cell_size,
                legend_width, (map_width, map_height), N, MAX_MAP_SIZE)

        colors = {
            '.': (255, 255, 255),
            'X': (128, 128, 128),
            '-': (0, 0, 0),
            '?': (60, 60, 60)
        }

        clock = pygame.time.Clock()
        restart_ui = False

        while running and not restart_ui:
            dt = clock.tick(120)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                make, save = ui.handle_event(event)
                if make:
                    new_N = ui.get_N_value() or N
                    new_w = ui.get_width_value() or map_width
                    new_h = ui.get_height_value() or map_height

                    N, map_width, map_height = new_N, new_w, new_h
                    map_size = (map_width, map_height)
                    restart_ui = True
                    break


                if save:
                    save_output(output)

            if generating:
                if not wfc.run_step():
                    generating = False
                output = wfc.render()

                if not generating:
                    repair(output)

            ui.update(dt, generating)
            ui.draw(output, colors, generating)

    pygame.quit()



def run_wfc(training_map, N, map_size):
    patterns = extract_patterns(training_map, N)
    catalog, weights = build_pattern_catalog(patterns)
    tile_adj = compute_tile_adjacency(training_map)
    adjacency = build_adjacency_rules(catalog, tile_adj)

    wfc = OverlappingWFC(map_size[0], map_size[1], catalog, weights, adjacency)
    while wfc.run_step():
        pass

    output = wfc.render()
    repair(output)
    save_output(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a map using Wave Function Collapse")
    parser.add_argument('--visualize', action='store_true', help="Enable visualization")
    args = parser.parse_args()

    training_map_path = "training_maps/training_map_1.txt"
    training_map = load_map(training_map_path)

    # Or use multiple maps:
    # training_map = load_all_maps("../data/all_txt_files")

    N = 3
    MAX_MAP_SIZE = 99
    map_size = (40, 40)
    base_window_size = (900, 600)

    if args.visualize:
        run_wfc_with_visualization(training_map, N, MAX_MAP_SIZE, map_size, base_window_size)
    else:
        run_wfc(training_map, N, map_size)
