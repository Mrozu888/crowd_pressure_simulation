import pygame


class Visualization:
    # --- 🎨 Stałe z kolorami dla łatwiejszej edycji ---
    BG_COLOR = (240, 240, 240)
    WALL_COLOR = (0, 0, 0)
    DOOR_COLOR = (0, 200, 0)
    AGENT_COLOR = (50, 50, 255)

    # --- Nowe kolory ---
    CASH_REGISTER_COLOR = (255, 100, 0)  # Np. pomarańczowy
    SHELF_COLOR = (120, 120, 120)  # Np. szary
    PALLET_COLOR = (139, 69, 19)  # Np. brązowy (kolor drewna)

    def __init__(self, env):
        self.env = env
        self.scale = env.scale

        # Rozmiar sceny (symulacji)
        self.scene_width = int(env.width * self.scale)
        self.scene_height = int(env.height * self.scale)

        # Rozmiar okna (może być większe niż scena)
        self.window_width = 1200
        self.window_height = 800

        # Utwórz okno
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Social Force Model Simulation - Sklep")

        # Oblicz offset, aby scena była wycentrowana
        self.offset_x = (self.window_width - self.scene_width) // 2
        self.offset_y = (self.window_height - self.scene_height) // 2

    def _transform_coords(self, sim_point):
        """
        Pomocnicza metoda do transformacji współrzędnych
        z przestrzeni symulacji na przestrzeń okna (uwzględniając skalę i offset).
        """
        sim_x, sim_y = sim_point
        screen_x = int(sim_x * self.scale) + self.offset_x
        screen_y = int(sim_y * self.scale) + self.offset_y
        return screen_x, screen_y

    def _draw_walls(self, walls):
        """Rysuje ściany (jako linie)."""
        for (p1, p2) in walls:
            start_pos = self._transform_coords(p1)
            end_pos = self._transform_coords(p2)
            pygame.draw.line(self.screen, self.WALL_COLOR, start_pos, end_pos, 4)

    def _draw_doors(self, doors):
        """
        Rysuje drzwi (jako linie).
        Zakładamy, że `doors` to lista linii, tak jak ściany [(p1, p2), ...].
        """
        for (p1, p2) in doors:
            start_pos = self._transform_coords(p1)
            end_pos = self._transform_coords(p2)
            pygame.draw.line(self.screen, self.DOOR_COLOR, start_pos, end_pos, 4)

    def _draw_shelves(self, shelves):
        """Rysuje półki (jako linie)."""
        for (p1, p2) in shelves:
            start_pos = self._transform_coords(p1)
            end_pos = self._transform_coords(p2)
            # Półki mogą być cieńsze niż ściany
            pygame.draw.line(self.screen, self.SHELF_COLOR, start_pos, end_pos, 2)
    
    def _draw_rect_objects(self, objects, color):
        """
        Pomocnicza metoda do rysowania obiektów prostokątnych (kasy, palety).
        Zakłada, że 'objects' to lista słowników:
        [ {"pos": (x, y), "size": (w, h)}, ... ]
        """
        for obj in objects:
            pos = obj["pos"]
            size = obj["size"]

            # Transformuj pozycję (lewy górny róg)
            screen_pos = self._transform_coords(pos)

            # Przeskaluj wymiary
            screen_w = int(size[0] * self.scale)
            screen_h = int(size[1] * self.scale)

            # Stwórz obiekt Rect i narysuj go
            obj_rect = pygame.Rect(screen_pos[0], screen_pos[1], screen_w, screen_h)
            pygame.draw.rect(self.screen, color, obj_rect)

    def _draw_agents(self, agents):
        """Rysuje agentów (jako kółka)."""
        for a in agents:
            # print("position", a.position)
            if not a.active:
                continue

            pos = self._transform_coords(a.position)
            radius = a.radius * self.scale
            pygame.draw.circle(self.screen, self.AGENT_COLOR, pos, radius)

    def draw(self):
        """
        Główna metoda rysująca. Czyści ekran i wywołuje
        prywatne metody do rysowania poszczególnych elementów.
        """
        # 1. Wyczyść ekran
        self.screen.fill(self.BG_COLOR)

        # 2. Rysuj elementy otoczenia (w kolejności od tyłu do przodu)
        # Zakładamy, że env dostarcza teraz listy tych obiektów

        if hasattr(self.env, 'walls'):
            self._draw_walls(self.env.walls)

        if hasattr(self.env, 'doors'):
            self._draw_doors(self.env.doors)

        if hasattr(self.env, 'shelves'):
            self._draw_shelves(self.env.shelves)

        if hasattr(self.env, 'pallets'):
            # Palety rysujemy jako prostokąty
            self._draw_rect_objects(self.env.pallets, self.PALLET_COLOR)

        if hasattr(self.env, 'cash_registers'):
            # Kasy również jako prostokąty, ale w innym kolorze
            self._draw_rect_objects(self.env.cash_registers, self.CASH_REGISTER_COLOR)

        # 3. Rysuj agentów na wierzchu
        if hasattr(self.env, 'agents'):
            self._draw_agents(self.env.agents)

        # 4. Zaktualizuj wyświetlacz
        pygame.display.flip()