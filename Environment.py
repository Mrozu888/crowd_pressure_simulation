import numpy as np
from Agent import Agent
from SocialForceModel import SocialForceModel


class Environment:
    def __init__(self, config):
        env_conf = config["environment"]
        sfm_conf = config["sfm"]

        self.scale = env_conf["scale"]
        self.width = env_conf["width"]
        self.height = env_conf["height"]

        self.exit = np.array(env_conf["exit"])

        self.doors = env_conf["doors"]
        self.walls = env_conf["walls"]
        self.pallets = env_conf["pallets"]
        self.shelves = env_conf["shelves"]
        self.cash_registers = env_conf["cash_registers"]

        self.model = SocialForceModel(sfm_conf)
        self.agents = self._create_agents(config, self.exit, sfm_conf["desired_speed"])

    def _build_walls(self, walls, door):
        new_walls = []
        for p1, p2 in walls:
            if p1[0] == door["x"] and p2[0] == door["x"]:
                new_walls.append(((p1[0], 0), (p2[0], door["y_min"])))
                new_walls.append(((p1[0], door["y_max"]), (p2[0], p2[1])))
            else:
                new_walls.append((p1, p2))
        return new_walls

    def _create_agents(self, config, goal, speed):
        """
        Create agents based on configuration.
        If 'agents' key exists -> use defined paths,
        otherwise generate random agents as fallback.
        """
        agents = []

        if "agents" in config:
            # Tworzymy agentów z predefiniowanymi ścieżkami
            for agent_conf in config["agents"]:
                # print(agent_conf)

                path = agent_conf.get("path")
                if not path:
                    raise ValueError("Each agent must define a 'path' when using 'agents' config section.")
                start_pos = path[0]
                # print(start_pos)

                agents.append(Agent(position=start_pos, desired_speed=speed, path=path))
        else:
            # Tryb losowy – stary sposób
            n = config["n_agents"]
            for _ in range(n):
                x = np.random.uniform(2, 6)
                y = np.random.uniform(2, 10)
                agents.append(Agent((x, y), goal, speed))
        return agents

    def remove_exited_agents(self):
        # for a in self.agents:
        #     if (a.position[0] > self.door["x"] + 0.5 and
        #             self.door["y_min"] < a.position[1] < self.door["y_max"]):
        #         a.active = False
        pass
