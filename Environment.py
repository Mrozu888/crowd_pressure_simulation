# environment.py
import numpy as np
from Agent import Agent
from SocialForceModel import SocialForceModel
from path_generation import generate_shopping_path


class Environment:
    def __init__(self, config):
        env_conf = config["environment"]
        sfm_conf = config["sfm"]

        # Ładowanie geometrii
        self.scale = env_conf["scale"]
        self.width = env_conf["width"]
        self.height = env_conf["height"]

        self.walls = env_conf["walls"]
        self.shelves = env_conf["shelves"]
        self.cash_registers = env_conf["cash_registers"]

        # Inicjalizacja modelu fizycznego
        self.model = SocialForceModel(sfm_conf)

        # Tworzenie agentów
        self.agents = self._create_agents(config, sfm_conf["desired_speed"])

    def _create_agents(self, config, speed):
        agents = []
        if "agent_generation" not in config:
            return agents

        gen_conf = config["agent_generation"]
        zones_conf = gen_conf["path_zones"]
        path_conf = gen_conf["path_config"]

        n = gen_conf["n_agents"]
        max_spawn = gen_conf["max_spawn_time"]

        for _ in range(n):
            spawn_time = np.random.uniform(0, max_spawn)

            path = generate_shopping_path(zones_conf, path_conf)
            start_pos = path[0]

            agents.append(Agent(
                position=start_pos,
                desired_speed=speed,
                path=path,
                spawn_time=spawn_time
            ))

        return agents

    def remove_exited_agents(self):
        """
        Usuwa z listy agentów tych, którzy dotarli do końca swojej ścieżki.
        Zatrzymuje agentów, którzy dopiero czekają na pojawienie się (spawn).
        """
        # Zliczamy agentów przed usunięciem (dla debugowania)
        before_count = len(self.agents)

        # Logika filtrowania:
        # Zachowujemy agenta, JEŚLI:
        # 1. Jego ścieżka istnieje (path is not None)
        #    ORAZ
        # 2. Jego indeks ścieżki jest mniejszy niż liczba punktów (path_index < len(path))
        #
        # To działa, ponieważ w klasie Agent, gdy path_index osiągnie len(path),
        # agent ustawia active=False i kończy ruch.

        self.agents = [
            agent for agent in self.agents
            if agent.path is not None and agent.path_index < len(agent.path)
        ]

        # Opcjonalnie: wypisz informację, jeśli ktoś został usunięty
        removed_count = before_count - len(self.agents)
        if removed_count > 0:
            print(f"Usunięto {removed_count} agentów (zakończyli zakupy). Pozostało: {len(self.agents)}")