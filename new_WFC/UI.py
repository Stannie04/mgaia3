import pygame

class UI:
    def __init__(self, screen, grid_width, grid_height, cell_size, legend_width, map_size, N, MAX_MAP_SIZE):
        self.screen = screen
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_size = cell_size
        self.legend_width = legend_width
        self.window_width = grid_width + legend_width
        self.window_height = grid_height
        self.input_text = str(N)

        self.MAX_MAP_SIZE = MAX_MAP_SIZE

        self.width_text = str(min(map_size[0], self.MAX_MAP_SIZE))
        self.height_text = str(min(map_size[1], self.MAX_MAP_SIZE))

        self.active_input = None
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_switch_ms = 500
        self.make_pressed = False
        self.save_pressed = False

        self.font = pygame.font.SysFont('Arial', max(15, min(20, cell_size)), bold=True)
        self.dot_states = ['.', '..', '...']
        self.dot_index = 0
        self.dot_timer = 0
        self.dot_interval = 500

        self.button_width = legend_width - 20
        self.button_height = 40
        self.button_x = grid_width + 10
        self.button_y = self.window_height - self.button_height - 60

        small_box_width = (self.button_width - 10) // 2
        self.width_box_rect = pygame.Rect(self.button_x, self.button_y - 140, small_box_width, 30)
        self.height_box_rect = pygame.Rect(self.button_x + small_box_width + 10, self.button_y - 140, small_box_width, 30)
        self.n_box_rect = pygame.Rect(self.button_x, self.button_y - 90, self.button_width, 40)
        self.make_map_rect = pygame.Rect(self.button_x, self.button_y, self.button_width, self.button_height)
        self.save_map_rect = pygame.Rect(self.button_x, self.button_y + self.button_height + 10, self.button_width, self.button_height)


    def handle_event(self, event):
        make = False
        save = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.width_box_rect.collidepoint(event.pos):
                self.active_input = 'width'
            elif self.height_box_rect.collidepoint(event.pos):
                self.active_input = 'height'
            elif self.n_box_rect.collidepoint(event.pos):
                self.active_input = 'N'
            else:
                self.active_input = None

            if self.make_map_rect.collidepoint(event.pos):
                self.make_pressed = True
            if self.save_map_rect.collidepoint(event.pos):
                self.save_pressed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            make = self.make_pressed
            save = self.save_pressed
            self.make_pressed = False
            self.save_pressed = False

        elif event.type == pygame.KEYDOWN and self.active_input:
            if event.key == pygame.K_BACKSPACE:
                if self.active_input == 'width':
                    self.width_text = self.width_text[:-1]
                elif self.active_input == 'height':
                    self.height_text = self.height_text[:-1]
                elif self.active_input == 'N':
                    self.input_text = self.input_text[:-1]
            elif event.unicode.isdigit():
                if self.active_input == 'width':
                    new_val = (self.width_text + event.unicode) if self.width_text else event.unicode
                    if int(new_val) <= self.MAX_MAP_SIZE:
                        self.width_text = new_val
                elif self.active_input == 'height':
                    new_val = (self.height_text + event.unicode) if self.height_text else event.unicode
                    if int(new_val) <= self.MAX_MAP_SIZE:
                        self.height_text = new_val
                elif self.active_input == 'N':
                    self.input_text += event.unicode

        return make, save


    def update(self, dt, generating):
        self.dot_timer += dt
        self.cursor_timer += dt
        if generating and self.dot_timer >= self.dot_interval:
            self.dot_timer = 0
            self.dot_index = (self.dot_index + 1) % len(self.dot_states)
        if self.cursor_timer >= self.cursor_switch_ms:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible


    def draw(self, output, colors, generating):
        self.screen.fill((255, 71, 76))
        for y, row in enumerate(output):
            for x, tile in enumerate(row):
                color = colors.get(tile, (255, 0, 0))
                pygame.draw.rect(self.screen, color, (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))

        pygame.draw.rect(self.screen, (40, 40, 40), (self.grid_width, 0, self.legend_width, self.window_height))

        pygame.draw.rect(self.screen, (70, 70, 70), self.width_box_rect)
        pygame.draw.rect(self.screen, (255, 255, 255) if self.active_input == 'width' else (200, 200, 200), self.width_box_rect, 2)
        width_text = self.width_text + ('|' if self.active_input == 'width' and self.cursor_visible else '')
        width_surface = self.font.render(width_text, True, (255, 255, 255))
        self.screen.blit(width_surface, (self.width_box_rect.x + 5, self.width_box_rect.y + 5))

        pygame.draw.rect(self.screen, (70, 70, 70), self.height_box_rect)
        pygame.draw.rect(self.screen, (255, 255, 255) if self.active_input == 'height' and self.cursor_visible else (200, 200, 200), self.height_box_rect, 2)
        height_text = self.height_text + ('|' if self.active_input == 'height' and self.cursor_visible else '')
        height_surface = self.font.render(height_text, True, (255, 255, 255))
        self.screen.blit(height_surface, (self.height_box_rect.x + 5, self.height_box_rect.y + 5))

        label_font = pygame.font.SysFont('Arial', 14)
        width_label = label_font.render("Width:", True, (255, 255, 255))
        height_label = label_font.render("Height:", True, (255, 255, 255))
        self.screen.blit(width_label, (self.width_box_rect.x, self.width_box_rect.y - 20))
        self.screen.blit(height_label, (self.height_box_rect.x, self.height_box_rect.y - 20))

        pygame.draw.rect(self.screen, (70, 70, 70), self.n_box_rect)
        pygame.draw.rect(self.screen, (255, 255, 255) if self.active_input == 'N' and self.cursor_visible else (200, 200, 200), self.n_box_rect, 2)
        n_text = self.input_text + ('|' if self.active_input == 'N' and self.cursor_visible else '')
        n_surface = self.font.render(n_text, True, (255, 255, 255))
        self.screen.blit(n_surface, (self.n_box_rect.x + 5, self.n_box_rect.y + 8))
        n_label = label_font.render("Pattern Size (N):", True, (255, 255, 255))
        self.screen.blit(n_label, (self.n_box_rect.x, self.n_box_rect.y - 20))

        self.draw_button(self.make_map_rect, "Make New Map", self.make_pressed)
        self.draw_button(self.save_map_rect, "Save Map", self.save_pressed)

        legend = [
            ("White: Walkable", (255, 255, 255)),
            ("Grey: Walls", (128, 128, 128)),
            ("Black: Out of Bounds", (0, 0, 0)),
            ("", (0, 0, 0)),
            (f"{'Generating' + self.dot_states[self.dot_index] if generating else 'Finished :)'}", (255, 0, 0) if generating else (0, 255, 0))
        ]

        for i, (text, color) in enumerate(legend):
            legend_surf = self.font.render(text, True, color)
            self.screen.blit(legend_surf, (self.grid_width + 10, 10 + i * int(self.font.get_linesize() * 1.1)))

        pygame.display.update()


    def draw_button(self, rect, label, pressed):
        bg_color = (50, 50, 50) if pressed else (70, 70, 70)
        pygame.draw.rect(self.screen, bg_color, rect)
        pygame.draw.rect(self.screen, (200, 200, 200), rect, 2)
        btn_font = pygame.font.SysFont('Arial', 18, bold=True)
        label_render = btn_font.render(label, True, (255, 255, 255))
        label_rect = label_render.get_rect(center=rect.center)
        self.screen.blit(label_render, label_rect)


    def get_N_value(self):
        try:
            return int(self.input_text)
        except ValueError:
            return None


    def get_width_value(self):
        try:
            return min(int(self.width_text), self.MAX_MAP_SIZE)
        except ValueError:
            return None


    def get_height_value(self):
        try:
            return min(int(self.height_text), self.MAX_MAP_SIZE)
        except ValueError:
            return None