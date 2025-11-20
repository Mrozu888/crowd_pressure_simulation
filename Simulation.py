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
        self.dt = config["dt"]      # Integration time step
        self.steps = config["steps"]  # Total simulation duration in steps

        # --- parametry wykrywania "utknięcia" agenta ---
        self.stuck_speed_threshold = 0.05   # m/s - poniżej tej prędkości uznajemy, że prawie stoi
        self.stuck_time_threshold = 0.2     # s - ile czasu musi "stać", żeby uznać utknięcie

        # licznik czasu utknięcia dla każdego agenta
        for a in self.env.agents:
            a.stuck_time = 0.0

        # --- ZMIANA ---
        # Dodajemy śledzenie aktualnego czasu symulacji
        self.current_time = 0.0
        # --- KONIEC ZMIANY ---

    def update(self):
        """
        Execute one complete simulation time step.
        ...
        """

        # --- KROK 1: Aktywacja agentów ---
        # Sprawdź agentów, którzy czekają na swój czas aktywacji
        for agent in self.env.agents:
            if not agent.active and self.current_time >= agent.spawn_time:
                agent.active = True

        # --- KROK 2: Aktualizacja aktywnych agentów ---
        for agent in self.env.agents:
            if not agent.active:
                continue  # Pomiń nieaktywnych (czekających na spawn lub tych, którzy wyszli)

            # ----------------- WYKRYWANIE UTKNIĘCIA -----------------
            speed = np.linalg.norm(agent.velocity)

            if speed < self.stuck_speed_threshold:
                agent.stuck_time += self.dt
            else:
                agent.stuck_time = 0.0

            # Jeśli agent "stoi" zbyt długo i ma zdefiniowany cel -> przelicz ścieżkę Dijkstrą
            if agent.stuck_time > self.stuck_time_threshold and agent.goal is not None:
                # pozostała część oryginalnej ścieżki od aktualnego waypointu
                remaining = None
                if getattr(agent, "path", None) is not None and agent.path_index is not None:
                    remaining = agent.path[agent.path_index:]

                # nowa ścieżka na siatce od aktualnej pozycji do aktualnego celu
                new_subpath_xy = self.env.find_path_dijkstra(
                    start=agent.position,
                    goal=agent.goal
                )

                if new_subpath_xy is not None and len(new_subpath_xy) > 1:
                    # pomijamy pierwszy punkt (to prawie identyczna bieżąca pozycja)
                    new_path = [np.array(p, dtype=float) for p in new_subpath_xy[1:]]

                    # dołączamy resztę oryginalnych waypointów (po obecnym celu)
                    if remaining is not None and len(remaining) > 1:
                        new_path.extend(remaining[1:])

                    # podmieniamy ścieżkę agenta
                    agent.path = new_path
                    agent.path_index = 0
                    agent.goal = agent.path[0]
                    agent.stuck_time = 0.0  # zresetuj licznik utknięcia

            # ----------------- LICZENIE SIŁ I RUCH -----------------
            # Ściany, półki i kasy traktujemy jako przeszkody
            obstacles = self.env.walls + self.env.shelves + self.env.cash_register_segments
            force = self.env.model.compute_force(agent, self.env.agents, obstacles)

            agent.update(force, self.dt)

        # --- KROK 3: Usuń agentów, którzy zakończyli ścieżkę ---
        self.env.remove_exited_agents()

        # --- KROK 4: Przesuń czas symulacji ---
        self.current_time += self.dt
