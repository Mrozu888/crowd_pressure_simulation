import pygame

class Visualization:
    """
    PyGame-based visualization system with movable camera (pan & zoom).
    Hold left mouse button to drag, use mouse wheel to zoom.
    """

    def __init__(self, env):
        self.env = env
        self.scale = env.scale
        self.base_scale = env.scale  # zapamiętaj bazową skalę
        self.screen = pygame.display.set_mode(
            (int(env.width * self.scale), int(env.height * self.scale)), pygame.RESIZABLE
        )
        pygame.display.set_caption("Social Force Model Simulation")

        # Kamera (przesunięcie)
        self.camera_offset = [0, 0]
        self.dragging = False
        self.last_mouse = (0, 0)

    def handle_events(self):
        """Obsługuje zdarzenia myszy dla przesuwania i zoomowania."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False

            # --- Przeciąganie myszą ---
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # lewy przycisk
                    self.dragging = True
                    self.last_mouse = event.pos
                elif event.button == 4:  # scroll up
                    self.scale *= 1.1
                elif event.button == 5:  # scroll down
                    self.scale /= 1.1

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False

            elif event.type == pygame.MOUSEMOTION and self.dragging:
                dx = event.pos[0] - self.last_mouse[0]
                dy = event.pos[1] - self.last_mouse[1]
                self.camera_offset[0] += dx
                self.camera_offset[1] += dy
                self.last_mouse = event.pos

        return True

    def _to_screen(self, x_m, y_m):
        """Konwersja współrzędnych z metrów na piksele + przesunięcie i odwrócenie osi Y."""
        height_px = int(self.env.height * self.scale)
        x_px = int(x_m * self.scale) + self.camera_offset[0]
        y_px = height_px - int(y_m * self.scale) + self.camera_offset[1]
        return x_px, y_px

    def draw(self):
        """Renderuje cały kadr."""
        self.screen.fill((240, 240, 240))

        # === ŚCIANY ===
        for (p1, p2) in self.env.walls:
            x1, y1 = self._to_screen(p1[0], p1[1])
            x2, y2 = self._to_screen(p2[0], p2[1])
            pygame.draw.line(self.screen, (0, 0, 0), (x1, y1), (x2, y2), 3)

        # === DRZWI ===
        for door in self.env.doors:
    # jeśli to pionowe drzwi (x, y_min, y_max)
            if "x" in door and "y_min" in door and "y_max" in door:
                x, y1 = self._to_screen(door["x"], door["y_min"])
                _, y2 = self._to_screen(door["x"], door["y_max"])
                pygame.draw.line(self.screen, (0, 200, 0), (x, y1), (x, y2), 4)
    # jeśli to poziome drzwi (x_min, x_max, y)
            elif "x_min" in door and "x_max" in door and "y" in door:
                x1, y = self._to_screen(door["x_min"], door["y"])
                x2, _ = self._to_screen(door["x_max"], door["y"])
                pygame.draw.line(self.screen, (0, 200, 0), (x1, y), (x2, y), 4)

        # === AGENCI ===
        for a in self.env.agents:
            if not a.active:
                continue
            x, y = self._to_screen(a.position[0], a.position[1])
            pygame.draw.circle(
                self.screen, (50, 100, 255), (x, y), int(a.radius * self.scale)
            )

        pygame.display.flip()
