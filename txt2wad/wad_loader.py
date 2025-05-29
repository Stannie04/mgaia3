import vizdoom as vzd
import pygame


def get_action(keybinds):
    keys = pygame.key.get_pressed()
    action = [0, 0, 0, 0, 0, 0, 0, 0]
    for key, mapping in keybinds.items():
        if keys[key]:
            action = [a or b for a, b in zip(action, mapping)]
    return action


def init_game(filename):
    game = vzd.DoomGame()

    # game.set_doom_game_path("data/doom.wad")
    # game.set_doom_scenario_path("data/E1M1.wad")
    game.set_doom_scenario_path(filename)
    game.set_screen_resolution(vzd.ScreenResolution.RES_1024X768)
    game.set_screen_format(vzd.ScreenFormat.RGB24)
    game.set_render_hud(True)
    game.set_render_crosshair(True)
    game.set_render_weapon(True)
    game.set_render_decals(True)
    game.set_window_visible(False)

    game.add_available_button(vzd.Button.TURN_LEFT)
    game.add_available_button(vzd.Button.TURN_RIGHT)
    game.add_available_button(vzd.Button.MOVE_FORWARD)
    game.add_available_button(vzd.Button.MOVE_BACKWARD)
    game.add_available_button(vzd.Button.MOVE_LEFT)
    game.add_available_button(vzd.Button.MOVE_RIGHT)
    game.add_available_button(vzd.Button.ATTACK)
    game.add_available_button(vzd.Button.USE)


    game.set_mode(vzd.Mode.ASYNC_PLAYER)
    game.init()

    return game


def run_episode(game, keybinds, screen):
    running = True
    clock = pygame.time.Clock()
    while running and not game.is_episode_finished():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game.make_action(get_action(keybinds))
        if game.is_episode_finished():
            break
        frame = game.get_state().screen_buffer
        surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        screen.blit(surface, (0, 0))
        pygame.display.flip()

        clock.tick(35)

def main(filename):
    keybinds = {
        pygame.K_LEFT: [1, 0, 0, 0, 0, 0, 0, 0],  # TURN_LEFT
        pygame.K_RIGHT: [0, 1, 0, 0, 0, 0, 0, 0],  # TURN_RIGHT
        pygame.K_w: [0, 0, 1, 0, 0, 0, 0, 0],  # MOVE_FORWARD
        pygame.K_s: [0, 0, 0, 1, 0, 0, 0, 0],  # MOVE_BACKWARD
        pygame.K_a: [0, 0, 0, 0, 1, 0, 0, 0],  # MOVE_LEFT
        pygame.K_d: [0, 0, 0, 0, 0, 1, 0, 0],  # MOVE_RIGHT
        pygame.K_SPACE: [0, 0, 0, 0, 0, 0, 1, 0],  # ATTACK
        pygame.K_e: [0, 0, 0, 0, 0, 0, 0, 1],  # USE
    }
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    game = init_game(filename)

    run_episode(game, keybinds, screen)
    game.close()
    pygame.quit()

