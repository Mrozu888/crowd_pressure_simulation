import pygame
import numpy as np


class Visualization:
    BG_COLOR = (240, 240, 240)
    WALL_COLOR = (0, 0, 0)
    DOOR_COLOR = (0, 200, 0)
    AGENT_COLOR = (50, 50, 255)
    AGENT_BLUE = (50, 50, 255)
    AGENT_QUEUE_GREEN = (0, 200, 0)
    AGENT_CROWD_YELLOW = (240, 200, 0)
    AGENT_CROWD_RED = (220, 50, 50)

    CASH_REGISTER_COLOR = (255, 100, 0)
    CASH_WORKING_FILL = CASH_REGISTER_COLOR
    CASH_OFF_FILL = (220, 60, 60)
    PALLET_FILL = (170, 120, 60)
    SHELF_COLOR = (120, 120, 120)
    PALLET_COLOR = (139, 69, 19)

    PATH_LINE_COLOR = (200, 200, 200)
    WAYPOINT_COLOR = (0, 0, 255)
    CURRENT_TARGET_COLOR = (0, 255, 0)
    WAITING_COLOR = (255, 0, 0)

    def __init__(self, env, screen: pygame.Surface | None = None):
        self.env = env
        self.scale = env.scale

        self.scene_width = int(env.width * self.scale)
        self.scene_height = int(env.height * self.scale)

        # Create / reuse pygame screen
        if screen is None:
            self.window_width = 1200
            self.window_height = 800
            self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE | pygame.SCALED)
        else:
            self.screen = screen
            self.window_width, self.window_height = self.screen.get_size()
        # fonts (emoji-friendly)
        pygame.font.init()
        self.legend_font = pygame.font.SysFont("Segoe UI Emoji", 12)
        self.legend_font_small = pygame.font.SysFont("Segoe UI Emoji", 10)
        # fallback if emoji font unavailable
        if self.legend_font is None:
            self.legend_font = pygame.font.SysFont("Arial", 14)
        if self.legend_font_small is None:
            self.legend_font_small = pygame.font.SysFont("Arial", 12)

        pygame.display.set_caption("Social Force Model Simulation - Sklep")

        # Keep the shop layout unchanged, but pin it to the left side so that
        # the right side stays free for graphs/legend (no overlap).
        self.sidebar_gap = 20
        # Reserve space on the right for HUD graphs (StatsHUD uses ~330px width).
        self.right_reserved_w = 370

        # Layout offsets are computed dynamically each frame to keep the shop centered.
        self.offset_x = 10
        self.offset_y = 10

        # Remember legend rect for layout/debug
        self.legend_rect = None
    
    
    def _update_layout_offsets(self) -> None:
        # Center the shop in the available area (screen minus right HUD panel).
        self.window_width, self.window_height = self.screen.get_size()
        avail_w = max(200, self.window_width - self.right_reserved_w - self.sidebar_gap)
        self.offset_x = max(10, (avail_w - self.scene_width) // 2)
        self.offset_y = max(10, (self.window_height - self.scene_height) // 2)

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

    def _draw_cash_registers(self, cash_registers):
        """Draw cash registers with status:
        - orange: working (has a nearby cash_payment point)
        - red with X: not working
        """
        env_conf = self.env.config.get("environment", {})
        pay_pts = env_conf.get("cash_payment", [])
        pay_pts_np = [np.array(p, dtype=np.float32) for p in pay_pts]

        def is_working(rect_center: np.ndarray) -> bool:
            # working if any cash_payment point is close enough to its center
            if not pay_pts_np:
                return False
            for p in pay_pts_np:
                if float(np.linalg.norm(p - rect_center)) <= 0.75:
                    return True
            return False

        for obj in cash_registers:
            pos = obj["pos"]
            size = obj["size"]

            # world center
            cx = float(pos[0] + size[0] * 0.5)
            cy = float(pos[1] + size[1] * 0.5)
            center = np.array([cx, cy], dtype=np.float32)

            working = is_working(center)

            base_col = self.CASH_REGISTER_COLOR if working else (210, 60, 60)
            outline = (180, 85, 0) if working else (140, 30, 30)

            screen_pos = self._transform_coords(pos)
            screen_w = int(size[0] * self.scale)
            screen_h = int(size[1] * self.scale)

            rect = pygame.Rect(screen_pos[0], screen_pos[1], screen_w, screen_h)
            # nice rounded box
            pygame.draw.rect(self.screen, base_col, rect, border_radius=5)
            pygame.draw.rect(self.screen, outline, rect, 2, border_radius=5)

            if not working:
                # draw X inside
                x1, y1 = rect.left + 4, rect.top + 4
                x2, y2 = rect.right - 4, rect.bottom - 4
                pygame.draw.line(self.screen, (255, 235, 235), (x1, y1), (x2, y2), 3)
                pygame.draw.line(self.screen, (255, 235, 235), (x1, y2), (x2, y1), 3)


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

    

    def _is_green_queue_agent(self, agent) -> bool:
        """Return True only for agents that are actually in cashier queue or being served.
        Priority over crowd (yellow/red).
        """
        qm = getattr(self.env, "queue_manager", None)
        if qm is None:
            return False
        phase = None
        if hasattr(qm, "agent_phase"):
            phase = qm.agent_phase.get(agent)
        # In the queue slots / waiting in queue
        if phase in ("to_queue_slot", "in_queue"):
            return True
        # Being served at cashier: agent reached cashier and is waiting (service time)
        if phase == "to_cashier" and getattr(agent, "is_waiting", False):
            return True
        return False

    def _crowd_group_sizes(self, agents, radius: float, skip_ids: set[int]) -> dict[int, int]:
        """Compute connected components by distance<=radius using a spatial hash grid.
        Returns mapping from id(agent) to component size (includes self). Agents in skip_ids are ignored.
        This is O(N) expected for large N (no O(N^2) all-pairs).
        """
        # collect active, non-skipped agents
        pts = []
        ids = []
        for a in agents:
            if not getattr(a, "active", True):
                continue
            aid = id(a)
            if aid in skip_ids:
                continue
            ids.append(aid)
            pts.append((float(a.position[0]), float(a.position[1])))

        n = len(ids)
        if n == 0:
            return {}

        cell = max(1e-6, float(radius))
        grid = {}
        for i, (x, y) in enumerate(pts):
            cx = int(x // cell)
            cy = int(y // cell)
            grid.setdefault((cx, cy), []).append(i)

        parent = list(range(n))
        size = [1] * n

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        def union(i, j):
            ri = find(i)
            rj = find(j)
            if ri == rj:
                return
            if size[ri] < size[rj]:
                ri, rj = rj, ri
            parent[rj] = ri
            size[ri] += size[rj]

        r2 = radius * radius
        for (cx, cy), idxs in grid.items():
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    neigh = grid.get((cx + dx, cy + dy))
                    if not neigh:
                        continue
                    for i in idxs:
                        xi, yi = pts[i]
                        for j in neigh:
                            if j <= i and (dx == 0 and dy == 0):
                                continue
                            xj, yj = pts[j]
                            ddx = xi - xj
                            ddy = yi - yj
                            if ddx * ddx + ddy * ddy <= r2:
                                union(i, j)

        comp_sizes = {}
        for i in range(n):
            root = find(i)
            comp_sizes[root] = comp_sizes.get(root, 0) + 1

        out = {}
        for i, aid in enumerate(ids):
            out[aid] = comp_sizes[find(i)]
        return out



    def _draw_agents(self, agents):
        crowd_radius = float(self.env.config.get("visualization", {}).get("crowd_radius", 0.55))

        # Green agents: in queue (slots) or being served (standing at cashier paying).
        green_ids = set()
        for a in agents:
            if not getattr(a, "active", True):
                continue
            if self._is_green_queue_agent(a):
                green_ids.add(id(a))

        # Crowd groups for remaining agents
        group_sizes = self._crowd_group_sizes(agents, radius=crowd_radius, skip_ids=green_ids)

        for a in agents:
            if not getattr(a, "active", True):
                continue

            pos = self._transform_coords(a.position)
            rad = int(a.radius * self.scale)

            aid = id(a)
            if aid in green_ids:
                color = self.AGENT_QUEUE_GREEN
            else:
                g = int(group_sizes.get(aid, 1))
                # thresholds: 2 agents => yellow, 3+ => red
                if g > 2:
                    color = self.AGENT_CROWD_RED
                elif g == 2:
                    color = self.AGENT_CROWD_YELLOW
                else:
                    color = self.AGENT_BLUE

            pygame.draw.circle(self.screen, color, pos, rad)

    def _draw_cash_payment(self):
        pts = self.env.config.get("environment", {}).get("cash_payment", [])
        for pt in pts:
            x, y = self._transform_coords(pt)
            pygame.draw.circle(self.screen, (255, 255, 255),  (x, y), 4)
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
        """Draw legend (bottom-left):
        - shelves_type colors + names (names may include emoji)
        - agent color section
        - cashiers: working (orange) / not working (red with X)
        - pallet
        """
        env_conf = self.env.config.get("environment", {})
        shelves = env_conf.get("shelves_type", [])

        font = getattr(self, "legend_font", pygame.font.SysFont("Segoe UI Emoji", 14))
        small = getattr(self, "legend_font_small", pygame.font.SysFont("Segoe UI Emoji", 12))
        if font is None:
            font = pygame.font.SysFont("Arial", 14)
        if small is None:
            small = pygame.font.SysFont("Arial", 12)

        # Build shelves list: keep order but unique names
        legend_items = []
        seen = set()
        for shelf in shelves:
            name = str(shelf.get("name", "UNKNOWN"))
            if name in seen:
                continue
            seen.add(name)
            color = shelf.get("color", (180, 180, 180))
            legend_items.append((name, color))

        # Sections
        agent_lines = [
            ("Klient", self.AGENT_BLUE),
            ("Kolejka / kasa", self.AGENT_QUEUE_GREEN),
            ("Tłok (2 osoby)", self.AGENT_CROWD_YELLOW),
            ("Zator (3+)", self.AGENT_CROWD_RED),
        ]
        misc_lines = [
            ("Kasa (działa)", self.CASH_WORKING_FILL),
            ("Kasa (nie działa)", self.CASH_OFF_FILL),
            ("Paleta", self.PALLET_FILL),
        ]

        # Measure width/height dynamically
        padding = 10
        line_h = 14
        section_gap = 6
        swatch = 10
        swatch_gap = 8

        def measure_text(s: str) -> int:
            return font.size(s)[0]

        max_w = 0
        # shelves lines include emoji already
        for name, _ in legend_items:
            max_w = max(max_w, measure_text(name))
        for name, _ in agent_lines:
            max_w = max(max_w, measure_text(name))
        for name, _ in misc_lines:
            max_w = max(max_w, measure_text(name))

        card_w = padding * 2 + swatch + swatch_gap + max_w
        # total lines
        n_lines = len(misc_lines) + len(agent_lines) + len(legend_items)
        card_h = padding * 2 + n_lines * line_h + section_gap * 2

        # Position: bottom-left
        x0 = self.screen.get_width() - card_w - 20
        y0 = self.screen.get_height() - card_h - 20
        if y0 < 20:
            y0 = 20

        card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card.fill((255, 255, 255, 230))
        pygame.draw.rect(card, (0, 0, 0, 60), card.get_rect(), 1, border_radius=12)

        y = padding

        # --- misc first (cashiers + pallet) ---
        for text, col in misc_lines:
            pygame.draw.rect(card, col, (padding, y + 3, swatch, swatch), border_radius=2)
            # draw red X for "not working cashier"
            if "nie działa" in text:
                x1 = padding
                y1 = y + 3
                x2 = padding + swatch
                y2 = y + 3 + swatch
                pygame.draw.line(card, (255, 255, 255), (x1, y1), (x2, y2), 2)
                pygame.draw.line(card, (255, 255, 255), (x2, y1), (x1, y2), 2)

            label = font.render(text, True, (10, 10, 10))
            card.blit(label, (padding + swatch + swatch_gap, y))
            y += line_h

        y += section_gap

        # --- agents section ---
        for text, col in agent_lines:
            pygame.draw.rect(card, col, (padding, y + 3, swatch, swatch), border_radius=2)
            label = font.render(text, True, (10, 10, 10))
            card.blit(label, (padding + swatch + swatch_gap, y))
            y += line_h

        y += section_gap

        # --- shelves_type section ---
        for name, col in legend_items:
            pygame.draw.rect(card, col, (padding, y + 3, swatch, swatch), border_radius=2)
            label = font.render(name, True, (10, 10, 10))
            card.blit(label, (padding + swatch + swatch_gap, y))
            y += line_h

        self.screen.blit(card, (x0, y0))

    def draw(self, flip: bool = True):
        self._update_layout_offsets()
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
            self._draw_cash_registers(self.env.cash_registers)

        if hasattr(self.env, "agents"):
            # self._draw_paths(self.env.agents)
            self._draw_agents(self.env.agents)
        self._draw_legend()
        if flip:
            pygame.display.flip()