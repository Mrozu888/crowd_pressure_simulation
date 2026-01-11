import numpy as np
from Agent import Agent
from SocialForceModel import SocialForceModel
from path_generation import generate_shopping_path
from PathFinding import GridMap, a_star_search
from QueueManager import QueueManager


class Environment:
    def __init__(self, config):
        self.config = config
        env_conf = config["environment"]
        sfm_conf = config["sfm"]

        self.walls = env_conf["walls"]
        self.shelves = env_conf["shelves"]
        # Optional elements used by visualization/stats
        self.doors = env_conf.get("doors", [])
        self.pallets = env_conf.get("pallets", [])
        self.cash_registers = env_conf["cash_registers"]

        self.scale = env_conf["scale"]
        self.width = env_conf["width"]
        self.height = env_conf["height"]

        all_obstacles = (
            self.walls
            + self.shelves
            + self._cashier_rects_to_lines()
        )

        self.grid_map = GridMap(
            self.width,
            self.height,
            all_obstacles,   # jako „walls”
            [],              # osobno „shelves” – nie używane, więc puste
            grid_size=0.2,
            obstacle_buffer=0.25
        )

        # Model sił społecznych
        self.model = SocialForceModel(sfm_conf)

        # KONFIGURACJA GENEROWANIA AGENTÓW (jak w master)
        self.gen_conf = config["agent_generation"]
        self.agent_speed = sfm_conf["desired_speed"]

        # Na starcie brak agentów – będą się respić w trakcie
        self.agents = []

        # Menedżer kolejek do kas (z gałęzi „kolejki”)
        self.queue_manager = QueueManager(self, config)

    def spawn_agent(self):
        """
        Tworzy i dodaje jednego nowego agenta:
        - generujemy ścieżkę zakupową (punkty POI),
        - rozwijamy ją do gęstego pathu A* (jak wcześniej w _create_agents),
        - agent startuje od razu (spawn_time=0, active=True).
        """

        # 1. Punkty strategiczne (spawn -> wejście -> półki)
        strategic_path = generate_shopping_path(self.gen_conf)

        # 2. Rozwinięcie do pełnej ścieżki A* z czasami „wait”
        detailed_path = self._calculate_full_path(strategic_path)

        if not detailed_path or len(detailed_path) < 2:
            # Nie udało się wyznaczyć sensownej ścieżki – pomijamy
            return

        # 3. Pozycja startowa = pierwszy punkt ścieżki
        start_pos = detailed_path[0]['pos']

        new_agent = Agent(
            position=start_pos,
            desired_speed=self.agent_speed,
            path=detailed_path,
            spawn_time=0.0  # aktywny od razu
        )

        self.agents.append(new_agent)

    def _calculate_full_path(self, waypoints):
        """
        Łączy rzadkie punkty (słowniki) gęstą ścieżką A*.
        waypoints: [{'pos': (x,y), 'wait': t}, ...]
        """
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

        if len(full_path) < 2:
            return []

        return full_path

    def remove_exited_agents(self):
        """Usuwa agentów, którzy opuścili sklep (oznaczonych jako exited=True)."""
        self.agents = [
            agent for agent in self.agents
            if not getattr(agent, "exited", False)
        ]

    def _cashier_rects_to_lines(self):
        """
        Konwertuje prostokątne kasy na 4 segmenty 'ścian' używane
        wyłącznie przez siatkę A* (GridMap). SFM widzi tylko walls + shelves.
        """
        segments = []
        for reg in self.cash_registers:
            x, y = reg["pos"]
            w, h = reg["size"]

            segments.extend([
                ((x,         y        ), (x + w,     y        )),  # dół
                ((x + w,     y        ), (x + w,     y + h    )),  # prawa
                ((x + w,     y + h    ), (x,         y + h    )),  # góra
                ((x,         y + h    ), (x,         y        )),  # lewa
            ])
        return segments

    def keep_agent_out_of_cashiers(self, agent):
        """
        Twarda blokada: jeśli agent nachodzi na prostokąt kasy,
        przesuwamy go na krawędź kasy (bez użycia sił SFM).
        """
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
                    if norm < 1e-6:
                        n = np.array([1.0, 0.0], dtype=np.float32)
                    else:
                        n = d_vec / norm
                else:
                    n = d_vec / dist

                penetration = agent.radius - dist
                agent.position += n * penetration

                vn = np.dot(agent.velocity, n)
                if vn < 0:
                    agent.velocity -= vn * n
