import pygame
import argparse

from WFC import OverlappingWFC
from UI import UI
from helper import (
    load_map,
    extract_patterns,
    build_pattern_catalog,
    build_adjacency_rules,
    save_output
)

def run_wfc_with_visualization(training_map, N, MAX_MAP_SIZE, map_size, base_window_size):
    pygame.init()
    base_legend_fraction = 0.20
    min_legend_width = 150

    map_width = min(map_size[0], MAX_MAP_SIZE)
    map_height = min(map_size[1], MAX_MAP_SIZE)
    generating = True
    running = True

    while running:
        grid_area_width = int(base_window_size[0] * (1 - base_legend_fraction))
        cell_size_width = grid_area_width // map_width
        cell_size_height = base_window_size[1] // map_height
        cell_size = min(cell_size_width, cell_size_height)

        if cell_size < 1:
            cell_size = 1
            map_width = min(map_width, grid_area_width)
            map_height = min(map_height, base_window_size[1])

        grid_width = map_width * cell_size
        legend_width = base_window_size[0] - grid_width

        if legend_width < min_legend_width:
            legend_width = min_legend_width
            grid_width = base_window_size[0] - legend_width
            cell_size = grid_width // map_width
            grid_width = map_width * cell_size

        window_width = grid_width + legend_width
        window_height = base_window_size[1]

        screen = pygame.display.set_mode((window_width, window_height))
        ui = UI(screen, grid_width, window_height, cell_size, legend_width, (map_width, map_height), N, MAX_MAP_SIZE)

        patterns = extract_patterns(training_map, N)
        catalog, weights = build_pattern_catalog(patterns)
        adjacency = build_adjacency_rules(catalog)
        wfc = OverlappingWFC(map_width, map_height, catalog, weights, adjacency)
        output = wfc.render()

        colors = {
            '.': (255, 255, 255),
            'X': (128, 128, 128),
            '-': (0, 0, 0),
            '?': (60, 60, 60)
        }

        clock = pygame.time.Clock()
        restart_ui = False

        while running and not restart_ui:
            dt = clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                make, save = ui.handle_event(event)

                if make:
                    new_N = ui.get_N_value() or N
                    new_width = ui.get_width_value() or map_width
                    new_height = ui.get_height_value() or map_height

                    if new_N != N or new_width != map_width or new_height != map_height:
                        N = new_N
                        map_width = new_width
                        map_height = new_height
                        restart_ui = True
                        break

                    patterns = extract_patterns(training_map, N)
                    catalog, weights = build_pattern_catalog(patterns)
                    adjacency = build_adjacency_rules(catalog)
                    wfc = OverlappingWFC(map_width, map_height, catalog, weights, adjacency)
                    generating = True

                if save:
                    save_output(output)

            if generating:
                if not wfc.run_step():
                    generating = False
                output = wfc.render()

            ui.update(dt, generating)
            ui.draw(output, colors, generating)

    pygame.quit()


def run_wfc(training_map, N, map_size):
    patterns = extract_patterns(training_map, N)
    catalog, weights = build_pattern_catalog(patterns)
    adjacency = build_adjacency_rules(catalog)
    wfc = OverlappingWFC(map_size[0], map_size[1], catalog, weights, adjacency)
    while True:
        if not wfc.run_step():
            break
    output = wfc.render()
    save_output(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a map using Wave Function Collapse")
    parser.add_argument('--visualize', action='store_true', help="Enable visualization")
    args = parser.parse_args()

    training_map_path = "training_maps/training_map_1.txt"
    training_map = load_map(training_map_path)

    N = 3
    MAX_MAP_SIZE = 80
    map_size = (30, 30)
    base_window_size = (900, 600)

    if args.visualize:
        run_wfc_with_visualization(training_map, N, MAX_MAP_SIZE, map_size, base_window_size)
    else:
        run_wfc(training_map, N, map_size)
