import pygame


class Visualization:
    BG_COLOR = (240, 240, 240)
    WALL_COLOR = (0, 0, 0)
    DOOR_COLOR = (0, 200, 0)
    AGENT_COLOR = (50, 50, 255)

    CASH_REGISTER_COLOR = (255, 100, 0)  # Np. pomarańczowy
    SHELF_COLOR = (120, 120, 120)  # Np. szary
    PALLET_COLOR = (139, 69, 19)  # Np. brązowy (kolor drewna)

    PATH_LINE_COLOR = (200, 200, 200)  # Jasnoszara linia (ścieżka A*)
    WAYPOINT_COLOR = (0, 0, 255)  # Niebieskie kropki (cele strategiczne)
    CURRENT_TARGET_COLOR = (0, 255, 0)  # Zielona kropka (gdzie agent idzie teraz)
    WAITING_COLOR = (255, 0, 0)  # Czerwona kropka (agent czeka)

    def __init__(self, env):
        self.env = env
        self.scale = env.scale

        # Rozmiar sceny 
        self.scene_width = int(env.width * self.scale)
        self.scene_height = int(env.height * self.scale)

        # Rozmiar okna
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
        z przestrzeni symulacji na przestrzeń okna.
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
        Rysuje ścieżki (obsługuje format słownikowy {'pos': (x,y), 'wait': t}).
        """
        for agent in agents:
            if not agent.active or agent.path is None or len(agent.path) < 2:
                continue

            pixel_path = [self._transform_coords(p['pos']) for p in agent.path]

            # Rysowanie linii ścieżki
            if len(pixel_path) > 1:
                pygame.draw.lines(self.screen, self.PATH_LINE_COLOR, False, pixel_path, 1)

            if hasattr(agent, 'waypoints') and agent.waypoints:
                for wp in agent.waypoints:
                    # Zabezpieczenie: sprawdzamy czy waypoint to słownik czy krotka
                    coord = wp['pos'] if isinstance(wp, dict) else wp
                    wp_screen = self._transform_coords(coord)
                    pygame.draw.circle(self.screen, self.WAYPOINT_COLOR, wp_screen, 4)

            current_idx = agent.path_index
            if 0 <= current_idx < len(pixel_path):
                current_target_screen = pixel_path[current_idx]

                # Jeśli agent czeka, kropka celu zmienia się na czerwoną
                color = self.WAITING_COLOR if getattr(agent, 'is_waiting', False) else self.CURRENT_TARGET_COLOR
                pygame.draw.circle(self.screen, color, current_target_screen, 3)

    def _draw_agents(self, agents):
        for a in agents:
            if not a.active:
                continue
            pos = self._transform_coords(a.position)
            radius = a.radius * self.scale
            pygame.draw.circle(self.screen, self.AGENT_COLOR, pos, radius)

    def draw(self):
        # Wyczyść ekran
        self.screen.fill(self.BG_COLOR)
        self._draw_cash_payment()

        # Rysuj otoczenie
        if hasattr(self.env, 'walls'): self._draw_walls(self.env.walls)
        if hasattr(self.env, 'doors'): self._draw_doors(self.env.doors)
        if hasattr(self.env, 'shelves'): self._draw_shelves(self.env.shelves)
        if hasattr(self.env, 'pallets'): self._draw_rect_objects(self.env.pallets, self.PALLET_COLOR)
        if hasattr(self.env, 'cash_registers'): self._draw_rect_objects(self.env.cash_registers,
                                                                        self.CASH_REGISTER_COLOR)

        # Rysuj ścieżki
        # if hasattr(self.env, 'agents'):
        #     self._draw_paths(self.env.agents)

        # Rysuj agentów
        if hasattr(self.env, 'agents'):
            self._draw_agents(self.env.agents)

        # Flip
        pygame.display.flip()
    def _draw_cash_payment(self):
        for pt in self.env.config["environment"]["cash_payment"]:
            x, y = self._transform_coords(pt)
            pygame.draw.circle(self.screen, (0,0,0), (x,y), 4)
