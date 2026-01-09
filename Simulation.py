import random
import numpy as np


class Simulation:
    """
    Główny kontroler symulacji:
    - ciągłe generowanie agentów (spawn_rate),
    - update fizyki agentów (SocialForceModel),
    - logika kolejek do kas,
    - usuwanie agentów, którzy wyszli.
    """

    def __init__(self, environment, config):
        self.env = environment
        self.dt = config["dt"]
        self.steps = config.get("steps", None)
        self.current_time = 0.0
        gen_conf = config["agent_generation"]
        self.spawn_rate = gen_conf.get("spawn_rate", 0.2)
        self.time_until_next_spawn = 0.0

    def update(self):
        """
        Jeden krok symulacji:
        1) ewentualny spawn nowego agenta,
        2) update wszystkich aktywnych agentów,
        3) update kolejek,
        4) usunięcie agentów, którzy wyszli.
        """
        if self.spawn_rate > 0:
            self.time_until_next_spawn -= self.dt
            if self.time_until_next_spawn <= 0:
                self.env.spawn_agent()
                base_interval = 1.0 / self.spawn_rate
                self.time_until_next_spawn = random.uniform(
                    base_interval * 0.8,
                    base_interval * 1.2,
                )

        for agent in self.env.agents:
            if not getattr(agent, "active", True) and \
               self.current_time >= getattr(agent, "spawn_time", 0.0):
                agent.active = True

        # --- OPTIMIZATION ---
        # Update the spatial grid with the current agent positions
        self.env.spatial_grid.update(self.env.agents)
        # --- END OPTIMIZATION ---

        for agent in self.env.agents:
            if not getattr(agent, "active", True):
                continue

            # --- OPTIMIZATION ---
            # Get only the neighbors from the spatial grid instead of all agents
            agent_search_radius = self.env.model.B * 2
            neighbors = self.env.spatial_grid.get_neighbors(agent, agent_search_radius)

            # Get nearby walls from the wall grid
            wall_search_radius = self.env.model.B_w * 2
            nearby_walls = self.env.wall_grid.get_nearby_walls(agent, wall_search_radius)
            # --- END OPTIMIZATION ---

            force = self.env.model.compute_force(
                agent,
                neighbors,
                nearby_walls,
            )
            agent.update(force, self.dt)

            if hasattr(self.env, "keep_agent_out_of_cashiers"):
                self.env.keep_agent_out_of_cashiers(agent)

        if hasattr(self.env, "queue_manager"):
            self.env.queue_manager.update(self.dt)

        if hasattr(self.env, "remove_exited_agents"):
            self.env.remove_exited_agents()

        self.current_time += self.dt
