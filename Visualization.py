import pygame


class Visualization:
    # --- 🎨 Stałe z kolorami dla łatwiejszej edycji ---
    BG_COLOR = (240, 240, 240)
    WALL_COLOR = (0, 0, 0)
    DOOR_COLOR = (0, 200, 0)
    AGENT_COLOR = (50, 50, 255)

    # --- Nowe kolory otoczenia ---
    CASH_REGISTER_COLOR = (255, 100, 0)  # Np. pomarańczowy
    SHELF_COLOR = (120, 120, 120)  # Np. szary
    PALLET_COLOR = (139, 69, 19)  # Np. brązowy (kolor drewna)

    # --- Nowe kolory ścieżek ---
    PATH_LINE_COLOR = (200, 200, 200)  # Jasnoszara linia (ścieżka A*)
    WAYPOINT_COLOR = (0, 0, 255)  # Niebieskie kropki (cele strategiczne)
    CURRENT_TARGET_COLOR = (0, 255, 0)  # Zielona kropka (gdzie agent idzie teraz)

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

    def _draw_paths(self, agents):
        """
        Nowa metoda do wizualizacji ścieżek agentów.
        Rysuje:
        1. Linię całej ścieżki (szara)
        2. Cele strategiczne (niebieskie kropki) - jeśli agent ma atrybut 'waypoints'
        3. Aktualny cel (zielona kropka)
        """
        for agent in agents:
            # Rysujemy tylko dla aktywnych agentów, którzy mają ścieżkę
            if not agent.active or agent.path is None or len(agent.path) < 2:
                continue

            # --- 1. Konwersja całej ścieżki na piksele ---
            # Używamy list comprehension i Twojej metody transformacji
            pixel_path = [self._transform_coords(p) for p in agent.path]

            # Rysowanie linii ścieżki (szara)
            if len(pixel_path) > 1:
                pygame.draw.lines(self.screen, self.PATH_LINE_COLOR, False, pixel_path, 1)

            # --- 2. Rysowanie celów strategicznych (Niebieskie kropki) ---
            # Sprawdzamy czy agent ma zapisane 'waypoints' (te rzadkie punkty przed A*)
            if hasattr(agent, 'waypoints') and agent.waypoints:
                for wp in agent.waypoints:
                    wp_screen = self._transform_coords(wp)
                    pygame.draw.circle(self.screen, self.WAYPOINT_COLOR, wp_screen, 4)

            # --- 3. Aktualny cel (Zielona kropka) ---
            # Pokazuje, w który punkt ścieżki A* agent celuje w tej chwili
            current_idx = agent.path_index
            if 0 <= current_idx < len(pixel_path):
                current_target_screen = pixel_path[current_idx]
                pygame.draw.circle(self.screen, self.CURRENT_TARGET_COLOR, current_target_screen, 3)

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

        # 3. Rysuj ścieżki (POD agentami, żeby ich nie zasłaniały)
        if hasattr(self.env, 'agents'):
            self._draw_paths(self.env.agents)

        # 4. Rysuj agentów na wierzchu
        if hasattr(self.env, 'agents'):
            self._draw_agents(self.env.agents)

        # 5. Zaktualizuj wyświetlacz
        pygame.display.flip()