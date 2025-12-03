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
        self.cash_registers = env_conf["cash_registers"]

        self.scale = env_conf["scale"]
        self.width = env_conf["width"]
        self.height = env_conf["height"]

        # Ściany + półki + obrys kas jako dodatkowe „ściany” TYLKO dla A*
        all_obstacles = (
            self.walls
            + self.shelves
            + self._cashier_rects_to_lines()
        )

        self.grid_map = GridMap(
            self.width,
            self.height,
            all_obstacles,
            [],
            grid_size=0.1,
            obstacle_buffer=0.15
        )


        self.model = SocialForceModel(sfm_conf)
        self.agents = self._create_agents(config, sfm_conf["desired_speed"])
        self.model = SocialForceModel(sfm_conf)
        self.agents = self._create_agents(config, sfm_conf["desired_speed"])

        # Menedżer kolejek do kas
        self.queue_manager = QueueManager(self, config)

    def _create_agents(self, config, speed):
        agents = []
        if "agent_generation" not in config:
            return agents

        gen_conf = config["agent_generation"]
        n = gen_conf["n_agents"]
        max_spawn = gen_conf["max_spawn_time"]

        for _ in range(n):
            spawn_time = np.random.uniform(0, max_spawn)

            strategic_path = generate_shopping_path(gen_conf)
            detailed_path = self._calculate_full_path(strategic_path)

            if not detailed_path or len(detailed_path) < 2:
                continue

            # --- POPRAWKA: detailed_path to lista słowników ---
            # Musimy wyciągnąć samo 'pos' dla konstruktora Agenta
            start_pos = detailed_path[0]['pos']

            new_agent = Agent(
                position=start_pos,
                desired_speed=speed,
                path=detailed_path,
                spawn_time=spawn_time
            )

            # Opcjonalnie: zapisujemy waypoints (tylko pozycje) do wizualizacji
            # new_agent.waypoints = [wp['pos'] for wp in strategic_path]

            agents.append(new_agent)

        return agents

    def _calculate_full_path(self, waypoints):
        """
        Łączy rzadkie punkty (słowniki) gęstą ścieżką A*.
        """
        if not waypoints or len(waypoints) < 2:
            return []

        # Start (pierwszy punkt)
        full_path = [waypoints[0]]

        current_start_pos = waypoints[0]['pos']

        for i in range(1, len(waypoints)):
            target_node = waypoints[i]
            target_pos = target_node['pos']
            target_wait = target_node.get('wait', 0.0)  # Czas jaki agent ma spędzić w TYM celu

            # A* działa na krotkach (x,y)
            segment = a_star_search(self.grid_map, current_start_pos, target_pos)

            if segment is None or len(segment) < 2:
                print(f"Nie można dojść do celu: {target_pos}. Pomijam go.")
                continue

            # Konwersja segmentu A* na format słownikowy
            # Pomijamy pierwszy punkt (bo to start, który już mamy)
            for j in range(1, len(segment)):
                pos = segment[j]

                # Tylko OSTATNI punkt tego segmentu dziedziczy czas czekania
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
        wyłącznie przez siatkę A* (GridMap). SFM dalej widzi tylko
        self.walls + self.shelves.
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

            # najbliższy punkt prostokąta kasy do środka agenta
            nearest_x = np.clip(agent.position[0], x, x + w)
            nearest_y = np.clip(agent.position[1], y, y + h)
            nearest = np.array([nearest_x, nearest_y], dtype=np.float32)

            d_vec = agent.position - nearest
            dist = np.linalg.norm(d_vec)

            # jeśli środek agenta jest w zasięgu promienia od krawędzi kasy
            if dist < agent.radius:
                if dist < 1e-6:
                    # awaryjnie – wypchnięcie od środka prostokąta
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
                # przesuń na zewnątrz
                agent.position += n * penetration

                # usuń składową prędkości skierowaną do środka kasy
                vn = np.dot(agent.velocity, n)
                if vn < 0:
                    agent.velocity -= vn * n
