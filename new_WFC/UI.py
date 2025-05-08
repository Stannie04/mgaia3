import pygame

class UI:
    def __init__(self, screen, grid_width, grid_height, cell_size, legend_width, map_size, N, MAX_MAP_SIZE):
        """
        Initialize UI with screen, dimensions, and default states.
        """
        self.screen = screen
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_size = cell_size
        self.legend_width = legend_width
        self.MAX_MAP_SIZE = MAX_MAP_SIZE

        self.texts = {
            'width': str(min(map_size[0], MAX_MAP_SIZE)),
            'height': str(min(map_size[1], MAX_MAP_SIZE)),
            'N': str(N)
        }

        self.active_input = None
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_switch_ms = 500
        self.pressed = {'make': False, 'save': False, 'repair': False}
        self.repaired = False
        self.generating = False

        self.font = pygame.font.SysFont('Arial', 18, bold=True)
        self.label_font = pygame.font.SysFont('Arial', 18)

        self.dot_states = ['.', '..', '...']
        self.dot_index = 0
        self.dot_timer = 0
        self.dot_interval = 500

        bw = legend_width - 20
        bh = 40
        bx = grid_width + 10
        by = grid_height - bh - 60
        sbw = (bw - 10) // 2

        self.input_boxes = {
            'width': pygame.Rect(bx, by - 190, sbw, 30),
            'height': pygame.Rect(bx + sbw + 10, by - 190, sbw, 30),
            'N': pygame.Rect(bx, by - 140, bw, 40)
        }

        self.buttons = {
            'repair': pygame.Rect(bx, by - bh - 10, bw, bh),
            'make': pygame.Rect(bx, by, bw, bh),
            'save': pygame.Rect(bx, by + bh + 10, bw, bh)
        }


    def handle_event(self, event):
        """
        Handle mouse and keyboard events for inputs and buttons.
        """
        make = False
        save = False
        repair = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            for key, rect in self.input_boxes.items():
                if rect.collidepoint(event.pos):
                    self.active_input = key
                    break
            else:
                self.active_input = None
            for key, rect in self.buttons.items():
                if rect.collidepoint(event.pos):
                    self.pressed[key] = True
        elif event.type == pygame.MOUSEBUTTONUP:
            make = self.pressed['make']
            save = self.pressed['save']
            repair = self.pressed['repair']
            # only allow repair if generation is finished
            if repair and not self.generating:
                self.repaired = True
            self.pressed = {k: False for k in self.pressed}
        elif event.type == pygame.KEYDOWN and self.active_input:
            text = self.texts[self.active_input]
            if event.key == pygame.K_BACKSPACE:
                self.texts[self.active_input] = text[:-1]
            elif event.unicode.isdigit():
                new = text + event.unicode if text else event.unicode
                if self.active_input in ('width', 'height'):
                    if int(new) <= self.MAX_MAP_SIZE:
                        self.texts[self.active_input] = new
                else:
                    self.texts['N'] = new

        return make, save, repair


    def update(self, dt, generating):
        """
        Update blinking cursor and generation progress indicator.
        """
        self.generating = generating

        self.dot_timer += dt
        self.cursor_timer += dt
        if generating and self.dot_timer >= self.dot_interval:
            self.dot_timer = 0
            self.dot_index = (self.dot_index + 1) % len(self.dot_states)
        if self.cursor_timer >= self.cursor_switch_ms:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible


    def draw(self, output, colors, generating):
        """
        Render the map grid, UI controls, and status legend.
        """
        self.screen.fill((255, 71, 76))
        for y, row in enumerate(output):
            for x, tile in enumerate(row):
                pygame.draw.rect(
                    self.screen,
                    colors.get(tile, (255, 0, 0)),
                    (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                )

        pygame.draw.rect(
            self.screen,
            (40, 40, 40),
            (self.grid_width, 0, self.legend_width, self.grid_height)
        )

        for key, rect in self.input_boxes.items():
            pygame.draw.rect(self.screen, (70, 70, 70), rect)
            border = (255, 255, 255) if self.active_input == key and self.cursor_visible else (200, 200, 200)
            pygame.draw.rect(self.screen, border, rect, 2)
            txt = self.texts[key] + ('|' if self.active_input == key and self.cursor_visible else '')
            offset_y = 5 if key != 'N' else 8
            self.screen.blit(self.font.render(txt, True, (255, 255, 255)), (rect.x + 5, rect.y + offset_y))
            label = {'width': 'Width:', 'height': 'Height:', 'N': 'Pattern Size (N):'}[key]
            self.screen.blit(self.label_font.render(label, True, (255, 255, 255)), (rect.x, rect.y - 20))

        for key, rect in self.buttons.items():
            bg = (50, 50, 50) if self.pressed[key] else (70, 70, 70)
            pygame.draw.rect(self.screen, bg, rect)
            pygame.draw.rect(self.screen, (200, 200, 200), rect, 2)
            label = {'repair': 'Repair', 'make': 'Make New Map', 'save': 'Save Map'}[key]
            text_surf = self.font.render(label, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=rect.center)
            self.screen.blit(text_surf, text_rect)

        legend = [
            ("White: Walkable", (255, 255, 255)),
            ("Grey: Walls", (128, 128, 128)),
            ("Black: Out of Bounds", (0, 0, 0)),
            ("", (0, 0, 0)),
            (
                ('Generating' + self.dot_states[self.dot_index]) if generating else 'Finished wfc',
                (255, 0, 0) if generating else (0, 255, 0)
            )
        ]

        if self.repaired:
            legend.append(("Repaired", (0, 255, 0)))
        for i, (text, color) in enumerate(legend):
            self.screen.blit(
                self.font.render(text, True, color),
                (self.grid_width + 10, 10 + i * int(self.font.get_linesize() * 1.1))
            )

        pygame.display.update()


    def draw_button(self, rect, label, pressed):
        """
        Draw a button rectangle with its label in the appropriate pressed state.
        """
        bg = (50, 50, 50) if pressed else (70, 70, 70)
        pygame.draw.rect(self.screen, bg, rect)
        pygame.draw.rect(self.screen, (200, 200, 200), rect, 2)
        text_surf = self.font.render(label, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)


    def get_N_value(self):
        """
        Return the integer pattern size from input or None if invalid.
        """
        try:
            return int(self.texts['N'])
        except ValueError:
            return None


    def get_width_value(self):
        """
        Return the integer width from input capped at MAX_MAP_SIZE or None if invalid.
        """
        try:
            return min(int(self.texts['width']), self.MAX_MAP_SIZE)
        except ValueError:
            return None


    def get_height_value(self):
        """
        Return the integer height from input capped at MAX_MAP_SIZE or None if invalid.
        """
        try:
            return min(int(self.texts['height']), self.MAX_MAP_SIZE)
        except ValueError:
            return None