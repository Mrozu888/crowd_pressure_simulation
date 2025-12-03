import numpy as np
from Agent import Agent
from SocialForceModel import SocialForceModel
from path_generation import generate_shopping_path
from PathFinding import GridMap


class Environment:
    def __init__(self, config):
        env_conf = config["environment"]
        sfm_conf = config["sfm"]

        self.walls = env_conf["walls"]
        self.shelves = env_conf["shelves"]
        self.cash_registers = env_conf["cash_registers"]

        self.scale = env_conf["scale"]
        self.width = env_conf["width"]
        self.height = env_conf["height"]

        self.grid_map = GridMap(
            self.width,
            self.height,
            self.walls,
            self.shelves,
            grid_size=0.1,
            obstacle_buffer=0.3
        )

        self.model = SocialForceModel(sfm_conf)

        # Przechowujemy konfigurację do późniejszego spawnowania
        self.gen_conf = config["agent_generation"]
        self.agent_speed = sfm_conf["desired_speed"]

        # Na starcie lista agentów jest pusta
        self.agents = []

    def spawn_agent(self):
        """Tworzy i dodaje jednego nowego agenta."""

        # 1. Generujemy listę zakupów
        strategic_path = generate_shopping_path(self.gen_conf)

        # 2. Start pos
        start_pos = strategic_path[0]['pos']

        # 3. Tworzymy agenta (spawn_time=0, bo wchodzi od razu w momencie wywołania)
        new_agent = Agent(
            position=start_pos,
            waypoints=strategic_path,
            grid_map=self.grid_map,
            desired_speed=self.agent_speed,
            spawn_time=0.0  # Aktywny natychmiast
        )

        # Opcjonalnie do wizualizacji
        new_agent.waypoints = strategic_path

        self.agents.append(new_agent)
        # print(f"Spawned new agent. Total: {len(self.agents)}")

    def remove_exited_agents(self):
        """Usuwa agentów, którzy dotarli do celu (active=False)."""
        self.agents = [agent for agent in self.agents if agent.active]