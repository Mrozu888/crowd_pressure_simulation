# pathfinding.py
import numpy as np
import heapq


# ... (Klasa GridMap bez zmian) ...
class GridMap:
    def __init__(self, width, height, walls, shelves, grid_size=0.25, obstacle_buffer=0.35):
        # ... (bez zmian) ...
        self.grid_size = grid_size
        self.cols = int(np.ceil(width / grid_size))
        self.rows = int(np.ceil(height / grid_size))
        self.grid = np.zeros((self.cols, self.rows), dtype=int)

        # Łączymy wszystkie przeszkody
        all_obstacles = walls + shelves

        for obj in all_obstacles:
            ((x1, y1), (x2, y2)) = obj
            min_x, max_x = min(x1, x2), max(x1, x2)
            min_y, max_y = min(y1, y2), max(y1, y2)

            inf_min_x = min_x - obstacle_buffer
            inf_max_x = max_x + obstacle_buffer
            inf_min_y = min_y - obstacle_buffer
            inf_max_y = max_y + obstacle_buffer

            i_min = int(np.floor(inf_min_x / grid_size))
            i_max = int(np.ceil(inf_max_x / grid_size))
            j_min = int(np.floor(inf_min_y / grid_size))
            j_max = int(np.ceil(inf_max_y / grid_size))

            i_min = max(0, i_min)
            j_min = max(0, j_min)
            i_max = min(self.cols - 1, i_max)
            j_max = min(self.rows - 1, j_max)

            self.grid[i_min:i_max + 1, j_min:j_max + 1] = 1

    def to_grid(self, pos):
        c = int(pos[0] / self.grid_size)
        r = int(pos[1] / self.grid_size)
        c = max(0, min(c, self.cols - 1))
        r = max(0, min(r, self.rows - 1))
        return (c, r)

    def to_world(self, grid_pos):
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

    # Zwiększamy promień poszukiwań z 5 na 10 (ok. 2.5 metra), żeby na pewno znaleźć wyjście
    if not grid_map.is_walkable(start_node):
        start_node = find_nearest_walkable(grid_map, start_node, max_radius=10)
        if start_node is None:
            print(f"BŁĄD A*: Start zablokowany {start_world}")
            return None  # Zwracamy None zamiast linii prostej

    if not grid_map.is_walkable(end_node):
        end_node = find_nearest_walkable(grid_map, end_node, max_radius=10)
        if end_node is None:
            print(f"BŁĄD A*: Cel zablokowany {end_world}")
            return None  # Zwracamy None zamiast linii prostej

    open_set = []
    heapq.heappush(open_set, (0, start_node))

    came_from = {}
    g_score = {start_node: 0}

    # Limit iteracji, żeby nie wisiało w nieskończoność przy braku drogi
    iterations = 0
    max_iterations = 5000

    while open_set:
        iterations += 1
        if iterations > max_iterations:
            print("BŁĄD A*: Przekroczono limit obliczeń (brak drogi?)")
            return None

        current = heapq.heappop(open_set)[1]

        if current == end_node:
            path = []
            while current in came_from:
                path.append(grid_map.to_world(current))
                current = came_from[current]
            path.reverse()
            return path

        neighbors = [
            (0, 1), (0, -1), (1, 0), (-1, 0),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]

        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)
            move_cost = 1.414 if dx != 0 and dy != 0 else 1.0

            if grid_map.is_walkable(neighbor):
                tentative_g_score = g_score[current] + move_cost

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    dist = ((neighbor[0] - end_node[0]) ** 2 + (neighbor[1] - end_node[1]) ** 2) ** 0.5
                    f_score = tentative_g_score + dist
                    heapq.heappush(open_set, (f_score, neighbor))

    # Jeśli pętla się skończyła i nie znaleziono trasy:
    print("BŁĄD A*: Nie znaleziono ścieżki (zamknięta przestrzeń)")
    return None  # Zwracamy None!


def find_nearest_walkable(grid_map, start_node, max_radius=10):
    if grid_map.is_walkable(start_node):
        return start_node
    x, y = start_node
    for r in range(1, max_radius + 1):
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if abs(dx) == r or abs(dy) == r:
                    node = (x + dx, y + dy)
                    if grid_map.is_walkable(node):
                        return node
    return None