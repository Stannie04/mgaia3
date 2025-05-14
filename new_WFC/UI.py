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

        self.pressed = {'make': False, 'save': False, 'repair': False, 'options': False}
        self.generating = False

        self.font = pygame.font.SysFont('Arial', 18, bold=True)
        self.label_font = pygame.font.SysFont('Arial', 18)
        self.option_font = pygame.font.SysFont('Arial', 14)

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
            'width': pygame.Rect(bx, by - 230, sbw, 30),
            'height': pygame.Rect(bx + sbw + 10, by - 230, sbw, 30),
            'N': pygame.Rect(bx, by - 180, bw, 40)
        }

        self.buttons = {
            'make': pygame.Rect(bx, by, bw, bh),
            'save': pygame.Rect(bx, by + bh + 10, bw, bh),
            'repair': pygame.Rect(bx, by - bh - 25, bw, bh),
        }

        options_y = by - bh - bh - 35
        self.buttons['options'] = pygame.Rect(bx, options_y, bw, bh)

        self.repair_functions = [
            ("remove_small_rooms", "Remove small rooms"),
            ("correct_edges",       "Correct edges"),
            ("seal_against_bounds", "Seal against bounds"),
            ("prune_isolated_walls","Prune isolated walls"),
            ("connect_rooms",       "Connect rooms"),
            ("place_start_and_exit", "Place start and exit"),
        ]

        self.repair_options = { key: True for key, _ in self.repair_functions }
        checkbox_start_y = options_y + bh + 15
        self.checkbox_rects = {}

        for i, (key, _) in enumerate(self.repair_functions):
            rect = pygame.Rect(bx + 10, checkbox_start_y + i*30, 20, 20)
            self.checkbox_rects[key] = rect

        self.show_options = False


    def handle_event(self, event):
        """
        Handle mouse and keyboard events for inputs, buttons, and checkboxes.
        """
        make = save = repair = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            for key, rect in self.input_boxes.items():
                if rect.collidepoint(event.pos):
                    self.active_input = key
                    break
            else:
                self.active_input = None

            for key, rect in self.buttons.items():
                if rect.collidepoint(event.pos):
                    if self.show_options and key != 'options':
                        continue
                    self.pressed[key] = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if not self.show_options:
                make   = self.pressed['make']
                save   = self.pressed['save']
                if self.pressed['repair'] and not self.generating:
                    repair = True

            if self.pressed['options']:
                self.show_options = not self.show_options

            if self.show_options:
                for key, rect in self.checkbox_rects.items():
                    if rect.collidepoint(event.pos):
                        self.repair_options[key] = not self.repair_options[key]

            self.pressed = {k: False for k in self.pressed}

            return make, save, repair

        elif event.type == pygame.KEYDOWN and self.active_input:
            text = self.texts[self.active_input]
            if event.key == pygame.K_BACKSPACE:
                self.texts[self.active_input] = text[:-1]
            elif event.unicode.isdigit():
                new = text + event.unicode
                if self.active_input in ('width','height'):
                    if int(new) <= self.MAX_MAP_SIZE:
                        self.texts[self.active_input] = new
                else:
                    self.texts['N'] = new

        return make, save, repair


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
        for y, row in enumerate(output):
            for x, tile in enumerate(row):
                pygame.draw.rect(
                    self.screen,
                    colors.get(tile, (255, 0, 0)),
                    (x*self.cell_size, y*self.cell_size,
                     self.cell_size, self.cell_size)
                )

        pygame.draw.rect(
            self.screen,
            (40,40,40),
            (self.grid_width,0,self.legend_width,self.grid_height)
        )

        for key, rect in self.input_boxes.items():
            pygame.draw.rect(self.screen, (70,70,70), rect)
            border = (255,255,255) if key==self.active_input and self.cursor_visible else (200,200,200)
            pygame.draw.rect(self.screen, border, rect, 2)
            txt = self.texts[key] + ('|' if key==self.active_input and self.cursor_visible else '')
            offset_y = 5 if key!='N' else 8
            self.screen.blit(self.font.render(txt, True, (255,255,255)), (rect.x+5, rect.y+offset_y))
            label = {'width':'Width:','height':'Height:','N':'Pattern Size (N):'}[key]
            self.screen.blit(self.label_font.render(label,True,(255,255,255)), (rect.x, rect.y-20))

        for key, rect in self.buttons.items():
            pressed = self.pressed.get(key, False)
            bg = (50,50,50) if pressed else (70,70,70)
            pygame.draw.rect(self.screen, bg, rect)
            pygame.draw.rect(self.screen, (200,200,200), rect, 2)
            labels = {
                'repair': 'Repair',
                'make':   'Make New Map',
                'save':   'Save Map',
                'options':'Repair Options'
            }
            surf = self.font.render(labels[key], True, (255,255,255))
            self.screen.blit(surf, surf.get_rect(center=rect.center))

        if self.show_options:
            options_rect = pygame.Rect(
                self.buttons['options'].x,
                self.buttons['options'].y + self.buttons['options'].height + 5,
                self.buttons['options'].width,
                len(self.repair_functions)*30 + 10
            )
            pygame.draw.rect(self.screen, (60,60,60), options_rect)
            pygame.draw.rect(self.screen, (200,200,200), options_rect, 2)

            for key, label_text in self.repair_functions:
                rect = self.checkbox_rects[key]
                pygame.draw.rect(self.screen, (200,200,200), rect, 2)

                if self.repair_options[key]:
                    inner = rect.inflate(-4,-4)
                    pygame.draw.rect(self.screen, (0,200,0), inner)
                else:
                    inner = rect.inflate(-4,-4)
                    pygame.draw.rect(self.screen, (40,40,40), inner)

                self.screen.blit(
                    self.option_font.render(label_text, True, (255,255,255)),
                    (rect.x + rect.width + 5, rect.y+2)
                )

        legend = [
            ("White: Walkable", (255,255,255)),
            ("Grey: Walls",      (128,128,128)),
            ("Black: Out of Bounds", (0,0,0)),
            ("Green: Start", (0,153,76)),
            ("Red: Exit", (153,0,0)),	
            ("", (0,0,0)),
            (
                ('Generating'+self.dot_states[self.dot_index]) if generating else 'Finished wfc',
                (255,0,0) if generating else (0,255,0)
            )
        ]

        for i,(text,color) in enumerate(legend):
            self.screen.blit(
                self.font.render(text,True,color),
                (self.grid_width+10, 10 + i*int(self.font.get_linesize()*1.1))
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
