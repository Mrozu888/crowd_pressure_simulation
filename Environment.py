import numpy as np
import random  # <-- POTRZEBNY NOWY IMPORT
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

        # --- ZMIANA ---
        # _create_agents jest teraz całkowicie przebudowane
        self.agents = self._create_agents(config, sfm_conf["desired_speed"])
        # --- KONIEC ZMIANY ---

    def _build_walls(self, walls, door):
        # Ta metoda wygląda na nieużywaną w __init__, ale zostawiam ją
        new_walls = []
        for p1, p2 in walls:
            if p1[0] == door["x"] and p2[0] == door["x"]:
                new_walls.append(((p1[0], 0), (p2[0], door["y_min"])))
                new_walls.append(((p1[0], door["y_max"]), (p2[0], p2[1])))
            else:
                new_walls.append((p1, p2))
        return new_walls

    # --- CAŁKOWICIE NOWA METODA POMOCNICZA ---
    def _generate_random_path(self, zones_config, path_config):
        """
        Generuje losową ścieżkę dla agenta na podstawie zdefiniowanych stref.
        """
        path = []

        # 1. Punkt startowy (poza sklepem)
        spawn_zone = zones_config["spawn"]
        start_pos = (np.random.uniform(spawn_zone[0][0], spawn_zone[1][0]),
                     np.random.uniform(spawn_zone[0][1], spawn_zone[1][1]))
        path.append(start_pos)

        # 2. Punkt wejścia (zaraz za drzwiami)
        entrance_first = zones_config["entrance"][0]
        entrance_second = zones_config["entrance"][1]
        path.append(entrance_first)
        path.append(entrance_second)

        # 3. Punkty w alejkach
        n_aisles = random.randint(path_config["min_aisles"], path_config["max_aisles"])
        aisle_x_ranges = zones_config["aisles_x_ranges"]
        aisle_y_range = zones_config["aisle_y_range"]

        # Wybierz n_aisles unikalnych alejek
        chosen_aisle_ranges = random.sample(aisle_x_ranges, min(n_aisles, len(aisle_x_ranges)))

        for x_range in chosen_aisle_ranges:
            x = np.random.uniform(x_range[0], x_range[1])
            y = np.random.uniform(aisle_y_range[0], aisle_y_range[1])
            path.append((x, y))

        # 4. Punkt w strefie przed kasami
        cashier_zone = zones_config["cashier_area"]
        cashier_pos = (np.random.uniform(cashier_zone[0][0], cashier_zone[1][0]),
                       np.random.uniform(cashier_zone[0][1], cashier_zone[1][1]))
        path.append(cashier_pos)

        # 5. Ostateczny cel (wyjście)
        path.append(zones_config["exit_goal"])

        return path

    # --- PRZEBUDOWANA METODA _create_agents ---
    def _create_agents(self, config, speed):
        """
        Tworzy agentów na podstawie konfiguracji generatora.
        """
        agents = []

        if "agent_generation" not in config:
            print("Ostrzeżenie: Brak konfiguracji 'agent_generation'. Nie utworzono agentów.")
            return agents

        gen_conf = config["agent_generation"]
        zones_conf = gen_conf["path_zones"]
        path_conf = gen_conf["path_config"]

        n = gen_conf["n_agents"]
        max_spawn_time = gen_conf["max_spawn_time"]

        for _ in range(n):
            # 1. Wygeneruj losowy czas aktywacji
            spawn_time = np.random.uniform(0, max_spawn_time)

            # 2. Wygeneruj losową ścieżkę
            path = self._generate_random_path(zones_conf, path_conf)

            # 3. Pozycja startowa to pierwszy punkt ścieżki
            start_pos = path[0]

            # 4. Stwórz agenta
            agents.append(Agent(
                position=start_pos,
                desired_speed=speed,
                path=path,
                spawn_time=spawn_time
            ))

        return agents

    def remove_exited_agents(self):
        # Ta funkcja była pusta, ale jeśli agenci mają być usuwani
        # po dotarciu do celu, można to zaimplementować tutaj
        # np. sprawdzając `if not agent.active and agent.path_index == len(agent.path)`
        pass