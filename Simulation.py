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

    def update(self, on_before_remove=None):
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
        # Przygotowujemy listę aktywnych agentów do obliczeń fizyki
        active_agents = []
        
        for agent in self.env.agents:
            if not getattr(agent, "active", True):
                if self.current_time >= getattr(agent, "spawn_time", 0.0):
                    agent.active = True
                    active_agents.append(agent)
            else:
                active_agents.append(agent)

        # PRZYGOTOWANIE DANYCH DO WEKTORYZACJI
        # Zamiast iterować N razy po liście obiektów wewnątrz modelu,
        # tworzymy macierze numpy raz na klatkę.
        if active_agents:
            agents_pos = np.array([a.position for a in active_agents], dtype=np.float32)
            agents_radii = np.array([a.radius for a in active_agents], dtype=np.float32)
            agents_vel = np.array([a.velocity for a in active_agents], dtype=np.float32)
        else:
            agents_pos = np.empty((0, 2), dtype=np.float32)
            agents_radii = np.empty((0,), dtype=np.float32)
            agents_vel = np.empty((0, 2), dtype=np.float32)

        # UPDATE FIZYKI AGENTÓW 
        # Ściany i półki łączymy raz
        all_walls = self.env.walls + self.env.shelves

        for i, agent in enumerate(active_agents):
            # Obliczamy siłę używając zoptymalizowanej metody wektorowej
            # Przekazujemy macierze wszystkich agentów
            force = self.env.model.compute_force(
                agent,
                agents_pos,   # Macierz pozycji (N, 2)
                agents_radii, # Wektor promieni (N,)
                agents_vel,   # Wektor prędkości (N, 2)
                all_walls,
            )
            agent.update(force, self.dt)

            # Twarde „odbicie” od kas
            if hasattr(self.env, "keep_agent_out_of_cashiers"):
                self.env.keep_agent_out_of_cashiers(agent)
                # Aktualizujemy pozycję w macierzy lokalnej, żeby kolejni agenci widzieli zmianę
                agents_pos[i] = agent.position

        #  LOGIKA KOLEJEK DO KAS 
        if hasattr(self.env, "queue_manager"):
            self.env.queue_manager.update(self.dt)

        # STATYSTYKI (callback przed usunięciem agentów)
        # Przekazujemy czas na koniec kroku (po aktualizacji pozycji/logiki).
        if on_before_remove is not None:
            step_end_time = self.current_time + self.dt
            on_before_remove(self.dt, step_end_time, self.env.agents, self.env)

        # USUWANIE AGENTÓW, KTÓRZY OPUŚCILI SKLEP 
        if hasattr(self.env, "remove_exited_agents"):
            self.env.remove_exited_agents()

        # POSUNIĘCIE CZASU 
        self.current_time += self.dt