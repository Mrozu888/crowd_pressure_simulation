# pathfinding.py
import numpy as np
import heapq


class GridMap:
    def __init__(self, width, height, walls, shelves, grid_size=0.5):
        """
        grid_size: wielkość jednej kratki w metrach (np. 0.5m).
        Im mniejsza, tym dokładniejsza ścieżka, ale wolniejsze obliczenia.
        """
        self.grid_size = grid_size
        self.cols = int(np.ceil(width / grid_size))
        self.rows = int(np.ceil(height / grid_size))
        self.grid = np.zeros((self.cols, self.rows), dtype=int)

        # Oznacz przeszkody na siatce (1 = zajęte, 0 = wolne)
        obstacles = walls + shelves
        for obj in obstacles:
            # Zakładam format przeszkody: ((x_min, y_min), (x_max, y_max))
            # Musisz dostosować to do swojego formatu danych w configu!
            (x_min, y_min), (x_max, y_max) = obj

            i_min = int(x_min / grid_size)
            i_max = int(x_max / grid_size)
            j_min = int(y_min / grid_size)
            j_max = int(y_max / grid_size)

            # Wypełniamy siatkę jedynkami tam gdzie są regały
            self.grid[i_min:i_max + 1, j_min:j_max + 1] = 1

    def to_grid(self, pos):
        """Konwertuje (x, y) świata na (col, row) siatki"""
        return (int(pos[0] / self.grid_size), int(pos[1] / self.grid_size))

    def to_world(self, grid_pos):
        """Konwertuje (col, row) siatki na środek kratki w świecie (x, y)"""
        return (grid_pos[0] * self.grid_size + self.grid_size / 2,
                grid_pos[1] * self.grid_size + self.grid_size / 2)

    def is_walkable(self, pos_grid):
        c, r = pos_grid
        if 0 <= c < self.cols and 0 <= r < self.rows:
            return self.grid[c][r] == 0
        return False


def a_star_search(grid_map, start_world, end_world):
    start_node = grid_map.to_grid(start_world)
    end_node = grid_map.to_grid(end_world)

    # Jeśli cel jest w ścianie, A* nie zadziała. Zwracamy cel bezpośrednio (SFM sobie poradzi lub agent stanie)
    if not grid_map.is_walkable(end_node):
        return [end_world]

    open_set = []
    heapq.heappush(open_set, (0, start_node))

    came_from = {}
    g_score = {start_node: 0}

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == end_node:
            path = []
            while current in came_from:
                path.append(grid_map.to_world(current))
                current = came_from[current]
            path.reverse()
            return path

        # Sprawdzamy sąsiadów (góra, dół, lewo, prawo)
        neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        # Możesz dodać skosy: (1,1), (-1,-1) itd. dla płynniejszego ruchu

        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)

            if grid_map.is_walkable(neighbor):
                tentative_g_score = g_score[current] + 1  # Koszt ruchu = 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    # Heurystyka: dystans Manhattan lub Euklidesowy
                    f_score = tentative_g_score + (
                                (neighbor[0] - end_node[0]) ** 2 + (neighbor[1] - end_node[1]) ** 2) ** 0.5
                    heapq.heappush(open_set, (f_score, neighbor))

    # Fallback: jeśli nie znaleziono drogi, idź na przełaj
    return [end_world]