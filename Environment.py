import numpy as np
from Agent import Agent
from SocialForceModel import SocialForceModel
from path_generation import generate_shopping_path
from PathFinding import GridMap, a_star_search


class Environment:
    def __init__(self, config):
        env_conf = config["environment"]
        sfm_conf = config["sfm"]

        self.walls = env_conf["walls"]
        self.shelves = env_conf["shelves"]
        self.cash_registers = env_conf["cash_registers"]

        # Ładowanie geometrii
        self.scale = env_conf["scale"]
        self.width = env_conf["width"]
        self.height = env_conf["height"]

        # --- Inicjalizacja Mapy dla A* ---
        self.grid_map = GridMap(
            self.width,
            self.height,
            self.walls,
            self.shelves,
            grid_size=0.1,  # Dokładność mapy
            obstacle_buffer=0.3  # Bufor (promień agenta)
        )

        self.model = SocialForceModel(sfm_conf)
        self.agents = self._create_agents(config, sfm_conf["desired_speed"])

    def _create_agents(self, config, speed):
        agents = []
        if "agent_generation" not in config:
            return agents

        # --- ZMIANA: Pobieramy cały config generacji ---
        gen_conf = config["agent_generation"]

        n = gen_conf["n_agents"]
        max_spawn = gen_conf["max_spawn_time"]

        for _ in range(n):
            spawn_time = np.random.uniform(0, max_spawn)

            # 1. Generujemy GŁÓWNE cele (Start -> Wybrane Punkty -> Kasa -> Wyjście)
            # Przekazujemy 'gen_conf' bo tam są nasze punkty
            strategic_path = generate_shopping_path(gen_conf)

            # 2. Obliczamy SZCZEGÓŁOWĄ trasę A* między tymi punktami
            detailed_path = self._calculate_full_path(strategic_path)

            # Zabezpieczenie: jeśli ścieżka jest pusta (błąd A*), pomiń agenta
            if not detailed_path:
                continue

            new_agent = Agent(
                position=detailed_path[0],
                desired_speed=speed,
                path=detailed_path,
                spawn_time=spawn_time
            )

            # Opcjonalnie: zapisujemy główne cele do wizualizacji (niebieskie kropki)
            new_agent.waypoints = strategic_path

            agents.append(new_agent)

        return agents

        # ... w klasie Environment ...

    def _calculate_full_path(self, waypoints):
        """
        Łączy rzadkie punkty strategiczne gęstą ścieżką omijającą przeszkody.
        Odporna na błędy (pomija nieosiągalne cele).
        """
        if not waypoints or len(waypoints) < 2:
            return []

        # Startujemy od pierwszego punktu
        full_path = [waypoints[0]]

        # current_start to punkt, z którego aktualnie wyruszamy
        current_start = waypoints[0]

        # Iterujemy po celach (omijając start)
        for target in waypoints[1:]:

            # Próbujemy znaleźć drogę A*
            segment = a_star_search(self.grid_map, current_start, target)

            # JEŚLI A* ZWRÓCIŁ BŁĄD (None) LUB TYLKO PUNKT KOŃCOWY (brak trasy)
            if segment is None or len(segment) < 2:
                print(f"⚠️ Nie można dojść do celu: {target}. Pomijam go.")
                # Nie aktualizujemy current_start, próbujemy dojść
                # ze STAREGO startu do NASTĘPNEGO celu w kolejnej pętli
                continue

                # JEŚLI DROGA JEST OK:
            # Dodajemy segment (bez pierwszego punktu, bo on już jest w full_path)
            full_path.extend(segment[1:])

            # Nowym startem staje się koniec tego segmentu
            current_start = segment[-1]

        # Zabezpieczenie: Jeśli po wszystkim mamy tylko 1 punkt (Start),
        # to znaczy, że agent nigdzie nie może dojść. Zwróć pustą listę, żeby go nie tworzyć.
        if len(full_path) < 2:
            return []

        return full_path

    def remove_exited_agents(self):
        """Usuwa agentów, którzy dotarli do celu."""
        self.agents = [
            agent for agent in self.agents
            if agent.path is not None and agent.path_index < len(agent.path)
        ]