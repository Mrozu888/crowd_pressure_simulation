import numpy as np


# Zakładam, że klasy Environment, Agent itp. są importowane, jeśli są w osobnych plikach


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

        # --- ZMIANA ---
        # Dodajemy śledzenie aktualnego czasu symulacji
        self.current_time = 0.0
        # --- KONIEC ZMIANY ---

    def update(self):
        """
        Execute one complete simulation time step.
        ...
        """

        # --- NOWY KROK 1: Aktywacja agentów ---
        # Sprawdź agentów, którzy czekają na swój czas aktywacji
        for agent in self.env.agents:
            if not agent.active and self.current_time >= agent.spawn_time:
                agent.active = True
        # --- KONIEC NOWEGO KROKU ---

        # Krok 2: Zaktualizuj wszystkich AKTYWNYCH agentów (były krok 1)
        for agent in self.env.agents:
            if not agent.active:
                continue  # Pomiń nieaktywnych

            force = self.env.model.compute_force(
                agent,
                self.env.agents,
                self.env.walls + self.env.shelves,
            )
            agent.update(force, self.dt)

            # TWARDY KOLIDER NA KASACH – BEZ SIŁ
            self.env.keep_agent_out_of_cashiers(agent)

        if hasattr(self.env, "queue_manager"):
            self.env.queue_manager.update(self.dt)

        # Krok 3: Usuń agentów, którzy wyszli (były krok 2)
        self.env.remove_exited_agents()

        # --- NOWY KROK 4: Przesuń czas symulacji ---
        self.current_time += self.dt
        # --- KONIEC NOWEGO KROKU ---