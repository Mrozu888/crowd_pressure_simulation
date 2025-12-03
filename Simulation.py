import numpy as np
import random


class Simulation:
    def __init__(self, environment, config):
        self.env = environment
        self.dt = config["dt"]

        # Pobieramy ustawienia spawnowania
        gen_conf = config["agent_generation"]
        self.spawn_rate = gen_conf.get("spawn_rate", 0.5)  # Domyślnie 0.5 agenta/sek

        # Timer do odliczania czasu do kolejnego spawnu
        self.time_until_next_spawn = 0.0

    def update(self):
        """
        Jeden krok symulacji.
        """

        # --- 1. OBSŁUGA GENEROWANIA NOWYCH AGENTÓW (CIĄGŁA) ---
        self.time_until_next_spawn -= self.dt

        if self.time_until_next_spawn <= 0:
            # Czas na nowego agenta!
            self.env.spawn_agent()

            # Resetujemy timer. Aby było naturalnie, losujemy czas do następnego.
            # Średni czas to 1 / spawn_rate.
            # Dodajemy trochę losowości (np. +/- 20%)
            base_interval = 1.0 / self.spawn_rate
            self.time_until_next_spawn = random.uniform(base_interval * 0.8, base_interval * 1.2)

        # --- 2. UPDATE AGENTÓW ---
        for agent in self.env.agents:
            force = self.env.model.compute_force(agent, self.env.agents, self.env.walls + self.env.shelves)
            agent.update(force, self.dt)

        # --- 3. USUWANIE ---
        self.env.remove_exited_agents()