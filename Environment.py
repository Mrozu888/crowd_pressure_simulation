# environment.py
import numpy as np
import heapq

from Agent import Agent
from SocialForceModel import SocialForceModel
from path_generation import generate_shopping_path


class Environment:
    def __init__(self, config):
        env_conf = config["environment"]
        sfm_conf = config["sfm"]

        # Ładowanie geometrii
        self.scale = env_conf["scale"]
        self.width = env_conf["width"]
        self.height = env_conf["height"]

        self.walls = env_conf["walls"]
        self.doors = env_conf.get("doors", [])
        self.shelves = env_conf["shelves"]
        self.pallets = env_conf.get("pallets", [])
        self.cash_registers = env_conf["cash_registers"]

        # Konwersja kas na segmenty (dla SocialForce i siatki zajętości)
        self.cash_register_segments = []
        for reg in self.cash_registers:
            self.cash_register_segments += self._rect_to_segments(reg)

        # Inicjalizacja modelu fizycznego
        self.model = SocialForceModel(sfm_conf)

        # Tworzenie agentów
        self.agents = self._create_agents(config, sfm_conf["desired_speed"])

        # Parametry siatki do wyznaczania ścieżek (Dijkstra)
        self.grid_cell_size = 0.25  # rozdzielczość siatki w metrach
        self._build_occupancy_grid()

    # ------------------------------------------------------------------
    # Tworzenie agentów
    # ------------------------------------------------------------------
    def _create_agents(self, config, speed):
        agents = []
        if "agent_generation" not in config:
            return agents

        gen_conf = config["agent_generation"]
        zones_conf = gen_conf["path_zones"]
        path_conf = gen_conf["path_config"]

        n = gen_conf["n_agents"]
        max_spawn = gen_conf["max_spawn_time"]

        for _ in range(n):
            spawn_time = np.random.uniform(0, max_spawn)

            path = generate_shopping_path(zones_conf, path_conf)
            start_pos = path[0]

            agents.append(Agent(
                position=start_pos,
                desired_speed=speed,
                path=path,
                spawn_time=spawn_time
            ))

        return agents

    def remove_exited_agents(self):
        """
        Usuwa z listy agentów tych, którzy dotarli do końca swojej ścieżki.
        Zatrzymuje agentów, którzy dopiero czekają na pojawienie się (spawn).
        """
        before_count = len(self.agents)

        self.agents = [
            agent for agent in self.agents
            if agent.path is not None and agent.path_index < len(agent.path)
        ]

        removed_count = before_count - len(self.agents)
        if removed_count > 0:
            print(f"Usunięto {removed_count} agentów (zakończyli zakupy). Pozostało: {len(self.agents)}")

    # ------------------------------------------------------------------
    # Geometria kas (prostokąt -> segmenty)
    # ------------------------------------------------------------------
    def _rect_to_segments(self, rect):
        """
        Zamienia prostokątną kasę o zadanej pozycji i rozmiarze
        na 4 segmenty (tak jak ściany), aby mogła być używana jako przeszkoda.
        """
        (x, y) = rect["pos"]
        (w, h) = rect["size"]

        p1 = (x, y)
        p2 = (x + w, y)
        p3 = (x + w, y + h)
        p4 = (x, y + h)

        return [
            (p1, p2),
            (p2, p3),
            (p3, p4),
            (p4, p1)
        ]

    # ------------------------------------------------------------------
    # Budowa siatki zajętości i Dijkstra
    # ------------------------------------------------------------------
    def _build_occupancy_grid(self):
        """
        Buduje prostą siatkę zajętości na podstawie ścian, półek i kas.
        occ_grid[ix][iy] = 1 oznacza komórkę zablokowaną (przeszkoda),
        0 oznacza miejsce, po którym agent może chodzić.
        """
        cs = self.grid_cell_size
        nx = int(self.width / cs)
        ny = int(self.height / cs)

        self.occ_grid = [[0 for _ in range(ny)] for _ in range(nx)]

        # Przeszkody: ściany + półki + krawędzie kas
        obstacles = self.walls + self.shelves + self.cash_register_segments
        margin = 0.2  # margines bezpieczeństwa wokół przeszkód

        for ix in range(nx):
            for iy in range(ny):
                x = (ix + 0.5) * cs
                y = (iy + 0.5) * cs
                p = np.array([x, y], dtype=float)

                for (p1, p2) in obstacles:
                    p1 = np.array(p1, dtype=float)
                    p2 = np.array(p2, dtype=float)
                    v = p2 - p1
                    L = np.linalg.norm(v)
                    if L == 0:
                        continue
                    u = v / L
                    t = np.clip(np.dot(p - p1, u), 0.0, L)
                    proj = p1 + t * u
                    dist = np.linalg.norm(p - proj)

                    if dist < margin:
                        self.occ_grid[ix][iy] = 1
                        break

    def _pos_to_ij(self, pos):
        cs = self.grid_cell_size
        i = int(pos[0] / cs)
        j = int(pos[1] / cs)
        return i, j

    def _ij_to_pos(self, i, j):
        cs = self.grid_cell_size
        x = (i + 0.5) * cs
        y = (j + 0.5) * cs
        return (x, y)

    def find_path_dijkstra(self, start, goal):
        """
        Najprostsza wersja Dijkstry na siatce:
        zwraca listę punktów (x,y) od start do goal,
        omijając komórki z occ_grid == 1.
        """
        cs = self.grid_cell_size
        nx = len(self.occ_grid)
        ny = len(self.occ_grid[0]) if nx > 0 else 0

        start_ij = self._pos_to_ij(start)
        goal_ij = self._pos_to_ij(goal)

        def in_bounds(i, j):
            return 0 <= i < nx and 0 <= j < ny

        def neighbors(i, j):
            # ruch 8-kierunkowy
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1),
                           (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                ni, nj = i + di, j + dj
                if in_bounds(ni, nj) and self.occ_grid[ni][nj] == 0:
                    yield ni, nj

        INF = 1e9
        dist = {start_ij: 0.0}
        prev = {}
        pq = [(0.0, start_ij)]

        while pq:
            d, (i, j) = heapq.heappop(pq)
            if (i, j) == goal_ij:
                break
            if d > dist.get((i, j), INF):
                continue

            for ni, nj in neighbors(i, j):
                nd = d + np.hypot(ni - i, nj - j)
                if nd < dist.get((ni, nj), INF):
                    dist[(ni, nj)] = nd
                    prev[(ni, nj)] = (i, j)
                    heapq.heappush(pq, (nd, (ni, nj)))

        if goal_ij not in dist:
            # ścieżka nie istnieje
            return None

        # Rekonstrukcja ścieżki w indeksach siatki
        path_ij = []
        cur = goal_ij
        while cur != start_ij:
            path_ij.append(cur)
            cur = prev[cur]
        path_ij.append(start_ij)
        path_ij.reverse()

        # Konwersja na współrzędne (x, y)
        path_xy = [self._ij_to_pos(i, j) for (i, j) in path_ij]
        return path_xy
