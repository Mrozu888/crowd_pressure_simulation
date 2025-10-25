import numpy as np
from Agent import Agent
from SocialForceModel import SocialForceModel

class Environment:
    def __init__(self, config):
        env_conf = config["environment"]
        sfm_conf = config["sfm"]

        self.scale = env_conf["scale"]
        self.width = env_conf["width"] / self.scale
        self.height = env_conf["height"] / self.scale
        self.exit = np.array(env_conf["exit"])
        self.door = env_conf["door"]
        self.walls = self._build_walls(env_conf["walls"], self.door)

        self.model = SocialForceModel(sfm_conf)
        self.agents = self._create_agents(config["n_agents"], self.exit, sfm_conf["desired_speed"])

    def _build_walls(self, walls, door):
        """Usuwa fragment ściany odpowiadający drzwiom"""
        new_walls = []
        for p1, p2 in walls:
            if p1[0] == door["x"] and p2[0] == door["x"]:
                # rozdziel prawą ścianę na dwie części nad i pod drzwiami
                new_walls.append(((p1[0], 0), (p2[0], door["y_min"])))
                new_walls.append(((p1[0], door["y_max"]), (p2[0], p2[1])))
            else:
                new_walls.append((p1, p2))
        return new_walls

    def _create_agents(self, n, goal, speed):
        agents = []
        for _ in range(n):
            x = np.random.uniform(2, 6)
            y = np.random.uniform(2, 10)
            agents.append(Agent((x, y), goal, speed))
        return agents

    def remove_exited_agents(self):
        """Usuwa agentów, którzy przeszli przez drzwi"""
        for a in self.agents:
            if a.position[0] > self.door["x"] + 0.5 and self.door["y_min"] < a.position[1] < self.door["y_max"]:
                a.active = False
