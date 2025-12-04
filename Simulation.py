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

        # jeśli masz w Config "steps" z dawnej wersji, możesz go zignorować
        self.steps = config.get("steps", None)

        # Aktualny czas symulacji
        self.current_time = 0.0

        # Konfiguracja spawnowania (jak w master)
        gen_conf = config["agent_generation"]
        self.spawn_rate = gen_conf.get("spawn_rate", 0.2)  # agenci / sekundę

        # Timer ile zostało do kolejnego spawnu
        self.time_until_next_spawn = 0.0

    def update(self):
        """
        Jeden krok symulacji:
        1) ewentualny spawn nowego agenta,
        2) update wszystkich aktywnych agentów,
        3) update kolejek,
        4) usunięcie agentów, którzy wyszli.
        """

        #  CIĄGŁE GENEROWANIE NOWYCH AGENTÓW 
        if self.spawn_rate > 0:
            self.time_until_next_spawn -= self.dt

            if self.time_until_next_spawn <= 0:
                # Czas na nowego agenta
                self.env.spawn_agent()

                # Wyznacz losowy odstęp do kolejnego spawnu (jak w master)
                base_interval = 1.0 / self.spawn_rate
                self.time_until_next_spawn = random.uniform(
                    base_interval * 0.8,
                    base_interval * 1.2,
                )

        #  AKTYWACJA AGENTÓW Z OPÓŹNIENIEM 
        for agent in self.env.agents:
            if not getattr(agent, "active", True) and \
               self.current_time >= getattr(agent, "spawn_time", 0.0):
                agent.active = True

        # UPDATE FIZYKI AGENTÓW 
        for agent in self.env.agents:
            if not getattr(agent, "active", True):
                continue  # Pomiń nieaktywnych

            force = self.env.model.compute_force(
                agent,
                self.env.agents,
                self.env.walls + self.env.shelves,
            )
            agent.update(force, self.dt)

            # Twarde „odbicie” od kas
            if hasattr(self.env, "keep_agent_out_of_cashiers"):
                self.env.keep_agent_out_of_cashiers(agent)

        #  LOGIKA KOLEJEK DO KAS 
        if hasattr(self.env, "queue_manager"):
            self.env.queue_manager.update(self.dt)

        # USUWANIE AGENTÓW, KTÓRZY OPUŚCILI SKLEP 
        if hasattr(self.env, "remove_exited_agents"):
            self.env.remove_exited_agents()

        # POSUNIĘCIE CZASU 
        self.current_time += self.dt
