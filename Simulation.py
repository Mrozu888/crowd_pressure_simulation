import numpy as np
class Simulation:
    """
    Main simulation controller that manages the time evolution of the environment.
    ...
    """

    def __init__(self, environment, config):
        """
        Initialize the simulation with environment and configuration.
        ...
        """
        self.env = environment
        self.dt = config["dt"]  # Integration time step
        self.steps = config["steps"]  # Total simulation duration in steps

        # śledzenie aktualnego czasu symulacji
        self.current_time = 0.0

    def update(self):
        """
        Execute one complete simulation time step.
        ...
        """

        #  Aktywacja agentów 
        for agent in self.env.agents:
            if not agent.active and self.current_time >= agent.spawn_time:
                agent.active = True


        # aktualizacja wszystkich AKTYWNYCH agentów 
        for agent in self.env.agents:
            if not agent.active:
                continue  # Pomiń nieaktywnych

            force = self.env.model.compute_force(
                agent,
                self.env.agents,
                self.env.walls + self.env.shelves,
            )
            agent.update(force, self.dt)

            self.env.keep_agent_out_of_cashiers(agent)

        if hasattr(self.env, "queue_manager"):
            self.env.queue_manager.update(self.dt)

        # Usuń agentów, którzy wyszli
        self.env.remove_exited_agents()

        #  Przesuń czas symulacji 
        self.current_time += self.dt
