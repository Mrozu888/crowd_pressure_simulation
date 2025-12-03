# Visualization.py
import pygame
import math


class Visualization:
    """
    Obsługuje całą wizualizację z użyciem PyGame.

    Klasa rysuje ściany, drzwi i agentów na ekranie, używając geometrii
    zapisanej w obiekcie Environment (walls, shelves, pallets, cash_registers).
    Na to nakładani są agenci.

    Kolorowanie tłumu:
    - kolor bazowy: niebieski  (normalna gęstość)
    - średnie zagęszczenie: pomarańczowy (>= CROWD_MED_NEIGHBORS sąsiadów)
    - wysokie zagęszczenie: czerwony     (>= CROWD_HIGH_NEIGHBORS sąsiadów)

    Zagęszczenie liczymy w prosty sposób, na podstawie liczby sąsiadów
    w zadanym promieniu w *współrzędnych świata*.
    """

    # --- 🎨 Stałe z kolorami dla łatwiejszej edycji ---
    BG_COLOR = (240, 240, 240)
    WALL_COLOR = (0, 0, 0)
    DOOR_COLOR = (0, 200, 0)
    AGENT_COLOR = (50, 50, 255)

    # --- Kolory elementów wyposażenia ---
    CASH_REGISTER_COLOR = (255, 100, 0)  # np. pomarańczowy
    SHELF_COLOR = (120, 120, 120)        # np. szary
    PALLET_COLOR = (139, 69, 19)         # np. brązowy (drewno)

    # --- Kolory ścieżek ---
    PATH_LINE_COLOR = (200, 200, 200)    # jasnoszara linia (ścieżka A*)
    WAYPOINT_COLOR = (0, 0, 255)         # niebieskie kropki (cele strategiczne)
    CURRENT_TARGET_COLOR = (0, 255, 0)   # zielona kropka (aktualny cel agenta)
    WAITING_COLOR = (255, 0, 0)          # czerwona kropka (agent czeka)

    # --- Kolorowanie zagęszczenia (na podstawie odległości) ---
    # promień sąsiedztwa, w którym liczymy sąsiadów [metry]
    CROWD_NEAR_RADIUS = 1.0
    # progi liczby sąsiadów w tym promieniu:
    # 0–1 sąsiad   → kolor bazowy
    # 2–3 sąsiadów → średnie zagęszczenie (żółty/pomarańczowy)
    # 4+ sąsiadów  → duże zagęszczenie (czerwony)
    CROWD_MED_NEIGHBORS = 2
    CROWD_HIGH_NEIGHBORS = 4

    CROWD_COLOR_MED = (255, 200, 0)   # żółto-pomarańczowy
    CROWD_COLOR_HIGH = (220, 20, 60)  # czerwony

    def __init__(self, env, stats_manager=None):
        """
        System renderowania.

        env           – instancja Environment (geometria + agenci).
        stats_manager – opcjonalny obiekt ze statystykami (może być None;
                        zostawiony na przyszłość, np. do rysowania HUD/overlays).
        """
        self.env = env
        self.stats = stats_manager  # na razie nieużywane, tylko przechowywane

        self.scale = env.scale

        # Rozmiar sceny (w jednostkach symulacji * scale)
        self.scene_width = int(env.width * self.scale)
        self.scene_height = int(env.height * self.scale)

        # Rozmiar okna (może być większy niż scena)
        self.window_width = 1200
        self.window_height = 800

        # Tworzenie okna
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Social Force Model Simulation - Sklep")

        # Przesunięcie, żeby scena była wycentrowana w oknie
        self.offset_x = (self.window_width - self.scene_width) // 2
        self.offset_y = (self.window_height - self.scene_height) // 2

    def _transform_coords(self, sim_point):
        """
        Transformacja współrzędnych z przestrzeni symulacji do przestrzeni okna.
        """
        sim_x, sim_y = sim_point
        screen_x = int(sim_x * self.scale) + self.offset_x
        screen_y = int(sim_y * self.scale) + self.offset_y
        return screen_x, screen_y

    def _draw_walls(self, walls):
        for (p1, p2) in walls:
            start_pos = self._transform_coords(p1)
            end_pos = self._transform_coords(p2)
            pygame.draw.line(self.screen, self.WALL_COLOR, start_pos, end_pos, 4)

    def _draw_doors(self, doors):
        for (p1, p2) in doors:
            start_pos = self._transform_coords(p1)
            end_pos = self._transform_coords(p2)
            pygame.draw.line(self.screen, self.DOOR_COLOR, start_pos, end_pos, 4)

    def _draw_shelves(self, shelves):
        for (p1, p2) in shelves:
            start_pos = self._transform_coords(p1)
            end_pos = self._transform_coords(p2)
            pygame.draw.line(self.screen, self.SHELF_COLOR, start_pos, end_pos, 2)

    def _draw_rect_objects(self, objects, color):
        for obj in objects:
            pos = obj["pos"]
            size = obj["size"]
            screen_pos = self._transform_coords(pos)
            screen_w = int(size[0] * self.scale)
            screen_h = int(size[1] * self.scale)
            obj_rect = pygame.Rect(screen_pos[0], screen_pos[1], screen_w, screen_h)
            pygame.draw.rect(self.screen, color, obj_rect)

    def _draw_paths(self, agents):
        """
        Rysuje ścieżki (obsługuje format listy słowników
        [{'pos': (x, y), 'wait': t}, ...]).
        """
        for agent in agents:
            if not agent.active or agent.path is None or len(agent.path) < 2:
                continue

            # ścieżka to lista słowników; bierzemy pole 'pos'
            pixel_path = [self._transform_coords(p['pos']) for p in agent.path]

            # Rysowanie linii ścieżki
            if len(pixel_path) > 1:
                pygame.draw.lines(self.screen, self.PATH_LINE_COLOR, False, pixel_path, 1)

            # Rysowanie celów strategicznych (waypoints)
            if hasattr(agent, 'waypoints') and agent.waypoints:
                for wp in agent.waypoints:
                    coord = wp['pos'] if isinstance(wp, dict) else wp
                    wp_screen = self._transform_coords(coord)
                    pygame.draw.circle(self.screen, self.WAYPOINT_COLOR, wp_screen, 4)

            # Rysowanie aktualnego celu
            current_idx = agent.path_index
            if 0 <= current_idx < len(pixel_path):
                current_target_screen = pixel_path[current_idx]
                color = self.WAITING_COLOR if getattr(agent, 'is_waiting', False) else self.CURRENT_TARGET_COLOR
                pygame.draw.circle(self.screen, color, current_target_screen, 3)

    def _draw_agents(self, agents):
        """
        Rysuje agentów z kolorem zależnym od lokalnego zagęszczenia.

        Przez „zagęszczenie” rozumiemy liczbę najbliższych sąsiadów
        w promieniu CROWD_NEAR_RADIUS. Dla każdego agenta:
        - jeśli sąsiadów >= CROWD_HIGH_NEIGHBORS → czerwony;
        - elif sąsiadów >= CROWD_MED_NEIGHBORS  → żółto-pomarańczowy;
        - w przeciwnym razie kolor bazowy AGENT_COLOR.
        """
        # wybieramy tylko aktywnych agentów
        alive = [a for a in agents if getattr(a, "active", True)]

        n = len(alive)
        if n == 0:
            return

        r2 = self.CROWD_NEAR_RADIUS * self.CROWD_NEAR_RADIUS

        # Licznik sąsiadów dla każdego agenta (prosty algorytm O(N^2))
        neighbor_counts = [0] * n

        for i in range(n):
            ai = alive[i]
            xi, yi = ai.position
            for j in range(i + 1, n):
                aj = alive[j]
                xj, yj = aj.position
                dx = xi - xj
                dy = yi - yj
                dist2 = dx * dx + dy * dy
                if dist2 <= r2:
                    neighbor_counts[i] += 1
                    neighbor_counts[j] += 1

        # Rysowanie z odpowiednim kolorem
        for idx, a in enumerate(alive):
            neighbors = neighbor_counts[idx]

            if neighbors >= self.CROWD_HIGH_NEIGHBORS:
                color = self.CROWD_COLOR_HIGH   # duże zagęszczenie
            elif neighbors >= self.CROWD_MED_NEIGHBORS:
                color = self.CROWD_COLOR_MED    # średnie zagęszczenie
            else:
                color = self.AGENT_COLOR        # normalny przepływ

            pos = self._transform_coords(a.position)
            radius = int(max(1, a.radius * self.scale))
            pygame.draw.circle(self.screen, color, pos, radius)

    def draw(self):
        """
        Rysuje pełną klatkę wizualizacji:

        1) czyści ekran,
        2) rysuje statyczną geometrię,
        3) rysuje ścieżki agentów,
        4) rysuje agentów z kolorowaniem tłumu,
        5) odświeża okno (flip).
        """
        # 1. Czyszczenie tła
        self.screen.fill(self.BG_COLOR)

        # 2. Otoczenie ze środowiska
        if hasattr(self.env, 'walls'):
            self._draw_walls(self.env.walls)
        if hasattr(self.env, 'doors'):
            self._draw_doors(self.env.doors)
        if hasattr(self.env, 'shelves'):
            self._draw_shelves(self.env.shelves)
        if hasattr(self.env, 'pallets'):
            self._draw_rect_objects(self.env.pallets, self.PALLET_COLOR)
        if hasattr(self.env, 'cash_registers'):
            self._draw_rect_objects(self.env.cash_registers, self.CASH_REGISTER_COLOR)

        # 3. Ścieżki agentów
        if hasattr(self.env, 'agents'):
            self._draw_paths(self.env.agents)

        # 4. Agenci (z kolorowaniem zagęszczenia)
        if hasattr(self.env, 'agents'):
            self._draw_agents(self.env.agents)

        # 5. Wysyłka bufora na ekran
        pygame.display.flip()
