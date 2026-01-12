import pygame


class Visualization:
    BG_COLOR = (240, 240, 240)
    WALL_COLOR = (0, 0, 0)
    DOOR_COLOR = (0, 200, 0)
    AGENT_COLOR = (50, 50, 255)

    CASH_REGISTER_COLOR = (255, 100, 0)
    SHELF_COLOR = (120, 120, 120)
    PALLET_COLOR = (139, 69, 19)

    PATH_LINE_COLOR = (200, 200, 200)
    WAYPOINT_COLOR = (0, 0, 255)
    CURRENT_TARGET_COLOR = (0, 255, 0)
    WAITING_COLOR = (255, 0, 0)

    def __init__(self, env):
        self.env = env
        self.scale = env.scale

        self.scene_width = int(env.width * self.scale)
        self.scene_height = int(env.height * self.scale)

        self.window_width = 1200
        self.window_height = 800

        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Social Force Model Simulation - Sklep")

        self.offset_x = (self.window_width - self.scene_width) // 2
        self.offset_y = (self.window_height - self.scene_height) // 2
    
    def _transform_coords(self, sim_point):
        sim_x, sim_y = sim_point
        screen_x = int(sim_x * self.scale) + self.offset_x
        screen_y = int(sim_y * self.scale) + self.offset_y
        return screen_x, screen_y

    def world_to_screen(self, pos):
        return self._transform_coords(pos)

    def _draw_walls(self, walls):
        for (p1, p2) in walls:
            pygame.draw.line(self.screen, self.WALL_COLOR,
                             self._transform_coords(p1), self._transform_coords(p2), 4)

    def _draw_doors(self, doors):
        for (p1, p2) in doors:
            pygame.draw.line(self.screen, self.DOOR_COLOR,
                             self._transform_coords(p1), self._transform_coords(p2), 4)

    def _draw_shelves(self, shelves):
        for (p1, p2) in shelves:
            pygame.draw.line(self.screen, self.SHELF_COLOR,
                             self._transform_coords(p1), self._transform_coords(p2), 2)

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
        for agent in agents:
            if not getattr(agent, "active", True) or agent.path is None or len(agent.path) < 2:
                continue

            pixel_path = [self._transform_coords(p["pos"]) for p in agent.path]

            if len(pixel_path) > 1:
                pygame.draw.lines(self.screen, self.PATH_LINE_COLOR, False, pixel_path, 1)

            if hasattr(agent, "waypoints") and agent.waypoints:
                for wp in agent.waypoints:
                    coord = wp["pos"] if isinstance(wp, dict) else wp
                    pygame.draw.circle(self.screen, self.WAYPOINT_COLOR,
                                       self._transform_coords(coord), 4)

            current_idx = agent.path_index
            if 0 <= current_idx < len(pixel_path):
                current_target_screen = pixel_path[current_idx]
                color = self.WAITING_COLOR if getattr(agent, "is_waiting", False) else self.CURRENT_TARGET_COLOR
                pygame.draw.circle(self.screen, color, current_target_screen, 3)

    def _draw_agents(self, agents):
        for a in agents:
            if not getattr(a, "active", True):
                continue
            pos = self._transform_coords(a.position)
            radius = int(a.radius * self.scale)
            pygame.draw.circle(self.screen, self.AGENT_COLOR, pos, radius)

    def _draw_cash_payment(self):
        pts = self.env.config.get("environment", {}).get("cash_payment", [])
        for pt in pts:
            x, y = self._transform_coords(pt)
            pygame.draw.circle(self.screen, (0, 0, 0), (x, y), 4)
    def _draw_colored_shelves(self):
        env_conf = self.env.config.get("environment", {})
        shelves = env_conf.get("shelves_type", [])

        for shelf in shelves:
            x, y = shelf["rect"]["pos"]      # lewy-dolny róg (świat)
            w, h = shelf["rect"]["size"]
            color = shelf.get("color", (180, 180, 180))

            rect = pygame.Rect(
                x * self.scale + self.offset_x,
                self.scene_height - (y + h) * self.scale + self.offset_y,
                w * self.scale,
                h * self.scale
            )

            pygame.draw.rect(self.screen, color, rect)

    def _draw_legend(self):
        """
        Rysuje legendę na podstawie environment['shelves_type'].
        Każdy wpis: kolor + nazwa działu.
        """
        env_conf = self.env.config.get("environment", {})
        shelves = env_conf.get("shelves_type", [])

        if not shelves:
            return

        font = pygame.font.SysFont("Arial", 14)

        # lewy dolny róg ekranu
        x0 = 10
        y0 = self.scene_height + self.offset_y - 20
        dy = 18

        for i, shelf in enumerate(shelves):
            name = shelf.get("name", "UNKNOWN")
            color = shelf.get("color", (180, 180, 180))

            y = y0 - i * dy

            # kolorowy kwadrat
            pygame.draw.rect(
                self.screen,
                color,
                pygame.Rect(x0, y, 14, 14)
            )

            # tekst
            text = font.render(name, True, (0, 0, 0))
            self.screen.blit(text, (x0 + 20, y - 2))

    def draw(self, flip: bool = True):
        self.screen.fill(self.BG_COLOR)
        self._draw_cash_payment()
        self._draw_colored_shelves()
        if hasattr(self.env, "walls"):
            self._draw_walls(self.env.walls)
        if hasattr(self.env, "doors"):
            self._draw_doors(self.env.doors)
        if hasattr(self.env, "shelves"):
            self._draw_shelves(self.env.shelves)
        if hasattr(self.env, "pallets"):
            self._draw_rect_objects(self.env.pallets, self.PALLET_COLOR)
        if hasattr(self.env, "cash_registers"):
            self._draw_rect_objects(self.env.cash_registers, self.CASH_REGISTER_COLOR)

        if hasattr(self.env, "agents"):
            # self._draw_paths(self.env.agents)
            self._draw_agents(self.env.agents)
        self._draw_legend()
        if flip:
            pygame.display.flip()
