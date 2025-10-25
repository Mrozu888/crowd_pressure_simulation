class Simulation:
    def __init__(self, environment, config):
        self.env = environment
        self.dt = config["dt"]
        self.steps = config["steps"]

    def update(self):
        for agent in self.env.agents:
            if not agent.active:
                continue
            force = self.env.model.compute_force(agent, self.env.agents, self.env.walls)
            agent.update(force, self.dt)
        self.env.remove_exited_agents()
