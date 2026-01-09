import numpy as np
from Agent import Agent
from SocialForceModel import SocialForceModel
from path_generation import generate_shopping_path
from PathFinding import GridMap, a_star_search
from QueueManager import QueueManager
import itertools


class SpatialGrid:
    """Divides the environment into a grid for efficient neighbor searches."""
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_width = int(np.ceil(width / cell_size))
        self.grid_height = int(np.ceil(height / cell_size))
        self.grid = {}

    def _get_cell_coords(self, position):
        """Returns the (x, y) grid coordinates for a given position."""
        x = int(position[0] / self.cell_size)
        y = int(position[1] / self.cell_size)
        return (x, y)

    def update(self, agents):
        """Clears and rebuilds the grid with current agent positions."""
        self.grid.clear()
        for agent in agents:
            if not getattr(agent, "active", True):
                continue
            cell_coords = self._get_cell_coords(agent.position)
            if cell_coords not in self.grid:
                self.grid[cell_coords] = []
            self.grid[cell_coords].append(agent)

    def get_neighbors(self, agent, search_radius):
        """Returns a list of agents within a given radius of the agent."""
        neighbors = []
        center_cell = self._get_cell_coords(agent.position)
        cell_search_range = int(np.ceil(search_radius / self.cell_size))

        for dx in range(-cell_search_range, cell_search_range + 1):
            for dy in range(-cell_search_range, cell_search_range + 1):
                cell_x = center_cell[0] + dx
                cell_y = center_cell[1] + dy

                if (cell_x, cell_y) in self.grid:
                    for other in self.grid[(cell_x, cell_y)]:
                        if other is not agent:
                            dist_sq = np.sum((agent.position - other.position)**2)
                            if dist_sq < search_radius**2:
                                neighbors.append(other)
        return neighbors


class WallGrid:
    """Spatial grid for static wall segments for efficient lookups."""
    def __init__(self, walls, cell_size):
        self.cell_size = cell_size
        self.grid = {}
        self._build(walls)

    def _get_cell_coords(self, position):
        x = int(position[0] / self.cell_size)
        y = int(position[1] / self.cell_size)
        return (x, y)

    def _build(self, walls):
        """Pre-calculates which walls fall into which grid cells."""
        for wall in walls:
            p1, p2 = np.array(wall[0]), np.array(wall[1])
            min_x, max_x = sorted((p1[0], p2[0]))
            min_y, max_y = sorted((p1[1], p2[1]))

            start_cell = self._get_cell_coords((min_x, min_y))
            end_cell = self._get_cell_coords((max_x, max_y))

            for x in range(start_cell[0], end_cell[0] + 1):
                for y in range(start_cell[1], end_cell[1] + 1):
                    if (x, y) not in self.grid:
                        self.grid[(x, y)] = []
                    self.grid[(x, y)].append(wall)

    def get_nearby_walls(self, agent, search_radius):
        """Returns a list of walls near the agent."""
        center_cell = self._get_cell_coords(agent.position)
        cell_search_range = int(np.ceil(search_radius / self.cell_size))
        
        nearby_walls = set()
        for dx in range(-cell_search_range, cell_search_range + 1):
            for dy in range(-cell_search_range, cell_search_range + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                if cell in self.grid:
                    for wall in self.grid[cell]:
                        nearby_walls.add(wall)
        return list(nearby_walls)


class Environment:
    def __init__(self, config):
        self.config = config
        env_conf = config["environment"]
        sfm_conf = config["sfm"]

        self.walls = env_conf["walls"]
        self.shelves = env_conf["shelves"]
        self.cash_registers = env_conf["cash_registers"]
        self.all_obstacles = self.walls + self.shelves

        self.scale = env_conf["scale"]
        self.width = env_conf["width"]
        self.height = env_conf["height"]

        a_star_obstacles = (
            self.walls
            + self.shelves
            + self._cashier_rects_to_lines()
        )

        self.grid_map = GridMap(
            self.width,
            self.height,
            a_star_obstacles,
            [],
            grid_size=0.1,
            obstacle_buffer=0.15
        )

        # --- OPTIMIZATION ---
        agent_cell_size = sfm_conf.get("B", 0.1) * 4
        self.spatial_grid = SpatialGrid(self.width, self.height, agent_cell_size)

        wall_cell_size = sfm_conf.get("B_w", 0.1) * 10
        self.wall_grid = WallGrid(self.all_obstacles, wall_cell_size)
        # --- END OPTIMIZATION ---

        self.model = SocialForceModel(sfm_conf)
        self.gen_conf = config["agent_generation"]
        self.agent_speed = sfm_conf["desired_speed"]
        self.agents = []
        self.queue_manager = QueueManager(self, config)

    def spawn_agent(self):
        strategic_path = generate_shopping_path(self.gen_conf)
        detailed_path = self._calculate_full_path(strategic_path)
        if not detailed_path or len(detailed_path) < 2:
            return
        start_pos = detailed_path[0]['pos']
        new_agent = Agent(
            position=start_pos,
            desired_speed=self.agent_speed,
            path=detailed_path,
            spawn_time=0.0
        )
        self.agents.append(new_agent)

    def _calculate_full_path(self, waypoints):
        if not waypoints or len(waypoints) < 2:
            return []
        full_path = [waypoints[0]]
        current_start_pos = waypoints[0]['pos']
        for i in range(1, len(waypoints)):
            target_node = waypoints[i]
            target_pos = target_node['pos']
            target_wait = target_node.get('wait', 0.0)
            segment = a_star_search(self.grid_map, current_start_pos, target_pos)
            if segment is None or len(segment) < 2:
                print(f"Nie można dojść do celu: {target_pos}. Pomijam go.")
                continue
            for j in range(1, len(segment)):
                pos = segment[j]
                is_last_in_segment = (j == len(segment) - 1)
                w = target_wait if is_last_in_segment else 0.0
                full_path.append({'pos': pos, 'wait': w})
            current_start_pos = segment[-1]
        return full_path if len(full_path) >= 2 else []

    def remove_exited_agents(self):
        self.agents = [agent for agent in self.agents if not getattr(agent, "exited", False)]

    def _cashier_rects_to_lines(self):
        segments = []
        for reg in self.cash_registers:
            x, y = reg["pos"]
            w, h = reg["size"]
            segments.extend([
                ((x, y), (x + w, y)),
                ((x + w, y), (x + w, y + h)),
                ((x + w, y + h), (x, y + h)),
                ((x, y + h), (x, y)),
            ])
        return segments

    def keep_agent_out_of_cashiers(self, agent):
        for reg in self.cash_registers:
            x, y = reg["pos"]
            w, h = reg["size"]
            nearest_x = np.clip(agent.position[0], x, x + w)
            nearest_y = np.clip(agent.position[1], y, y + h)
            nearest = np.array([nearest_x, nearest_y], dtype=np.float32)
            d_vec = agent.position - nearest
            dist = np.linalg.norm(d_vec)
            if dist < agent.radius:
                if dist < 1e-6:
                    center = np.array([x + w / 2.0, y + h / 2.0], dtype=np.float32)
                    d_vec = agent.position - center
                    norm = np.linalg.norm(d_vec)
                    n = d_vec / norm if norm > 1e-6 else np.array([1.0, 0.0], dtype=np.float32)
                else:
                    n = d_vec / dist
                penetration = agent.radius - dist
                agent.position += n * penetration
                vn = np.dot(agent.velocity, n)
                if vn < 0:
                    agent.velocity -= vn * n
