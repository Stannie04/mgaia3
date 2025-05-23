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

        # Track pressed state for buttons
        self.pressed = {'make': False, 'save': False, 'repair': False, 'options': False, 'fill': False}
        self.generating = False

        # Track whether repair/fill have been used
        self.repaired = False
        self.filled = False

        self.font = pygame.font.SysFont('Arial', 18, bold=True)
        self.label_font = pygame.font.SysFont('Arial', 18)
        self.option_font = pygame.font.SysFont('Arial', 14)

        self.dot_states = ['.', '..', '...']
        self.dot_index = 0
        self.dot_timer = 0
        self.dot_interval = 500

        # Layout metrics
        bw = legend_width - 20           # Button/text width
        bh = 40                          # Button height
        small_h = 30                     # Input box height for width/height
        pattern_h = 40                   # Input box height for N
        spacing = 10                     # Space between elements
        margin_bottom = 20               # Bottom margin
        bx = grid_width + 10             # Left x-coordinate for UI elements

        # Buttons vertical positions (from bottom up): save, make, fill, repair, options
        y_save = self.grid_height - margin_bottom - bh
        y_make = y_save - spacing - bh
        y_fill = y_make - spacing - bh
        y_repair = y_fill - spacing - bh
        y_options = y_repair - spacing - bh

        # Input boxes vertical positions (above options)
        y_pattern = y_options - spacing - pattern_h - 10
        y_width = y_pattern - spacing - small_h - 10

        sbw = (bw - 10) // 2  # Small box width for width/height

        # Define input boxes
        self.input_boxes = {
            'width': pygame.Rect(bx, y_width, sbw, small_h),
            'height': pygame.Rect(bx + sbw + 10, y_width, sbw, small_h),
            'N': pygame.Rect(bx, y_pattern, bw, pattern_h)
        }

        # Define buttons
        self.buttons = {
            'options': pygame.Rect(bx, y_options, bw, bh),
            'repair':  pygame.Rect(bx, y_repair, bw, bh),
            'fill':    pygame.Rect(bx, y_fill, bw, bh),
            'make':    pygame.Rect(bx, y_make, bw, bh),
            'save':    pygame.Rect(bx, y_save, bw, bh)
        }

        # Repair functions and checkbox setup
        self.repair_functions = [
            ("remove_small_rooms", "Remove small rooms"),
            ("correct_edges",       "Correct edges"),
            ("seal_against_bounds", "Seal against bounds"),
            ("prune_isolated_walls","Prune isolated walls"),
            ("connect_rooms",       "Connect rooms")
        ]

        self.repair_options = {key: True for key, _ in self.repair_functions}
        checkbox_start_y = y_options + bh + spacing
        self.checkbox_rects = {}
        for i, (key, _) in enumerate(self.repair_functions):
            rect = pygame.Rect(bx + 10, checkbox_start_y + i * (small_h), 20, 20)
            self.checkbox_rects[key] = rect

        self.show_options = False

    def handle_event(self, event):
        """
        Handle mouse and keyboard events for inputs, buttons, and checkboxes.
        """
        make = save = repair = fill = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check input boxes
            for key, rect in self.input_boxes.items():
                if rect.collidepoint(event.pos):
                    self.active_input = key
                    break
            else:
                self.active_input = None

            # Track button press
            for key, rect in self.buttons.items():
                if rect.collidepoint(event.pos) and not (self.show_options and key != 'options'):
                    self.pressed[key] = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if not self.show_options:
                make = self.pressed['make']
                save = self.pressed['save']
                # Only enable repair once and after generation
                if self.pressed['repair'] and not self.generating and not self.repaired:
                    repair = True
                    self.repaired = True
                # Only enable fill after repair and once
                if self.pressed['fill'] and not self.generating and self.repaired and not self.filled:
                    fill = True
                    self.filled = True

            # Toggle options dropdown
            if self.pressed['options']:
                self.show_options = not self.show_options

            # Toggle individual repair options
            if self.show_options:
                for key, rect in self.checkbox_rects.items():
                    if rect.collidepoint(event.pos):
                        self.repair_options[key] = not self.repair_options[key]

            # Reset pressed states
            self.pressed = {k: False for k in self.pressed}
            return make, save, repair, fill

        elif event.type == pygame.KEYDOWN and self.active_input:
            # Handle text input
            text = self.texts[self.active_input]
            if event.key == pygame.K_BACKSPACE:
                self.texts[self.active_input] = text[:-1]
            elif event.unicode.isdigit():
                new = text + event.unicode
                if self.active_input in ('width', 'height') and int(new) <= self.MAX_MAP_SIZE:
                    self.texts[self.active_input] = new
                elif self.active_input == 'N':
                    self.texts['N'] = new

        return make, save, repair, fill

    def update(self, dt, generating):
        """
        Update blinking cursor and loading indicator.
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
        Render grid, legend background, inputs, buttons, dropdown, and status text.
        """
        self.screen.fill((255, 71, 76))
        # Draw grid
        for y, row in enumerate(output):
            for x, tile in enumerate(row):
                pygame.draw.rect(
                    self.screen,
                    colors.get(tile, (255, 0, 0)),
                    (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                )
        # Draw sidebar background
        pygame.draw.rect(
            self.screen,
            (40, 40, 40),
            (self.grid_width, 0, self.legend_width, self.grid_height)
        )
        # Draw inputs
        for key, rect in self.input_boxes.items():
            pygame.draw.rect(self.screen, (70, 70, 70), rect)
            border_color = (255, 255, 255) if key == self.active_input and self.cursor_visible else (200, 200, 200)
            pygame.draw.rect(self.screen, border_color, rect, 2)
            txt = self.texts[key] + ('|' if key == self.active_input and self.cursor_visible else '')
            offset_y = 5 if key != 'N' else 8
            self.screen.blit(self.font.render(txt, True, (255, 255, 255)), (rect.x + 5, rect.y + offset_y))
            label_map = {'width': 'Width:', 'height': 'Height:', 'N': 'Pattern Size (N):'}
            self.screen.blit(self.label_font.render(label_map[key], True, (255, 255, 255)), (rect.x, rect.y - 20))
        # Draw buttons
        for key, rect in self.buttons.items():
            disabled = False
            if key == 'repair' and (self.repaired or generating):
                disabled = True
            elif key == 'fill' and (not self.repaired or self.filled):
                disabled = True
            bg = (40, 40, 40) if disabled else ((50, 50, 50) if self.pressed[key] else (70, 70, 70))
            pygame.draw.rect(self.screen, bg, rect)
            pygame.draw.rect(self.screen, (200, 200, 200), rect, 2)
            label_texts = {'options':'Repair Options','repair':'Repair','fill':'Fill Tiles','make':'Make New Map','save':'Save Map'}
            surf = self.font.render(label_texts[key], True, (255, 255, 255))
            self.screen.blit(surf, surf.get_rect(center=rect.center))
        # Draw repair options if toggled
        if self.show_options:
            options_rect = pygame.Rect(
                self.buttons['options'].x,
                self.buttons['options'].y + self.buttons['options'].height + 5,
                self.buttons['options'].width,
                len(self.repair_functions) * 30 + 10
            )
            pygame.draw.rect(self.screen, (60, 60, 60), options_rect)
            pygame.draw.rect(self.screen, (200, 200, 200), options_rect, 2)
            for key, label_text in self.repair_functions:
                rect = self.checkbox_rects[key]
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 2)
                if self.repair_options[key]:
                    inner = rect.inflate(-4, -4)
                    pygame.draw.rect(self.screen, (0, 200, 0), inner)
                else:
                    inner = rect.inflate(-4, -4)
                    pygame.draw.rect(self.screen, (40, 40, 40), inner)
                self.screen.blit(
                    self.option_font.render(label_text, True, (255, 255, 255)),
                    (rect.x + rect.width + 5, rect.y + 2)
                )
        # Draw legend/status
        legend = [
            ("White: Walkable", (255, 255, 255)),
            ("Grey: Walls", (128, 128, 128)),
            ("Black: Out of Bounds", (0, 0, 0)),
            ("Pink: Start", (255, 204, 255)),
            ("Green: Exit", (0, 153, 76)),
            ("Red: Enemy", (153, 0, 0)),
            ("", (0, 0, 0)),
            (('Generating'+self.dot_states[self.dot_index]) if generating else 'Finished wfc',
             (255, 0, 0) if generating else (0, 255, 0))
        ]
        for i, (text, color) in enumerate(legend):
            self.screen.blit(
                self.font.render(text, True, color),
                (self.grid_width + 10, 10 + i * int(self.font.get_linesize() * 1.1))
            )
        pygame.display.update()

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