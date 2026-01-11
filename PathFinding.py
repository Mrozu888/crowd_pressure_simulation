import numpy as np
import heapq


class GridMap:
    def __init__(self, width, height, walls, shelves, grid_size=0.25, obstacle_buffer=0.35):
        self.grid_size = grid_size
        self.cols = int(np.ceil(width / grid_size))
        self.rows = int(np.ceil(height / grid_size))
        # Używamy int8 dla oszczędności pamięci, jeśli mapa jest duża
        self.grid = np.zeros((self.cols, self.rows), dtype=np.int8)

        # Pre-kalkulacja bufora w jednostkach siatki
        buffer_cells = int(np.ceil(obstacle_buffer / grid_size))

        all_obstacles = walls + shelves

        # Optymalizacja: wektoryzacja nie jest tu łatwa bez zmiany formatu danych, 
        # ale pętla jest wykonywana tylko raz przy inicjalizacji.
        for ((x1, y1), (x2, y2)) in all_obstacles:
            # Zamiana na indeksy siatki
            c1 = int(min(x1, x2) / grid_size)
            c2 = int(max(x1, x2) / grid_size)
            r1 = int(min(y1, y2) / grid_size)
            r2 = int(max(y1, y2) / grid_size)

            # Dodanie bufora
            c_min = max(0, c1 - buffer_cells)
            c_max = min(self.cols - 1, c2 + buffer_cells)
            r_min = max(0, r1 - buffer_cells)
            r_max = min(self.rows - 1, r2 + buffer_cells)

            # Wypełnianie wycinka tablicy (slice) - to jest bardzo szybkie w numpy
            self.grid[c_min:c_max + 1, r_min:r_max + 1] = 1

    def to_grid(self, pos):
        c = int(pos[0] / self.grid_size)
        r = int(pos[1] / self.grid_size)
        # Szybki clamp bez wywoływania funkcji min/max
        if c < 0:
            c = 0
        elif c >= self.cols:
            c = self.cols - 1
        if r < 0:
            r = 0
        elif r >= self.rows:
            r = self.rows - 1
        return (c, r)

    def to_world(self, grid_pos):
        return (grid_pos[0] * self.grid_size + self.grid_size / 2,
                grid_pos[1] * self.grid_size + self.grid_size / 2)

    def is_walkable(self, pos_grid):
        c, r = pos_grid
        # Szybsze sprawdzenie bez if-ów zagnieżdżonych (short-circuit evaluation)
        return 0 <= c < self.cols and 0 <= r < self.rows and self.grid[c, r] == 0

    def line_of_sight(self, start, end):
        """Sprawdza czy między dwoma punktami siatki jest czysta linia (Bresenham)"""
        x0, y0 = start
        x1, y1 = end

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0

        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1

        if dx > dy:
            err = dx / 2.0
            while x != x1:
                if not self.is_walkable((x, y)): return False
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                if not self.is_walkable((x, y)): return False
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy

        return self.is_walkable((x, y))


# Definicja ruchów poza pętlą dla wydajności
# (dx, dy, koszt)
NEIGHBORS = [
    (0, 1, 1.0), (0, -1, 1.0), (1, 0, 1.0), (-1, 0, 1.0),
    (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)
]


def heuristic(a, b):
    """Octile distance - szybsze i dokładniejsze dla siatki z ruchem na skos niż Euklides"""
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return 1.0 * (dx + dy) + (1.414 - 2.0) * min(dx, dy)


def simplify_path(grid_map, path_grid):
    """
    Kluczowa optymalizacja dla Social Force Model.
    Redukuje ścieżkę z np. 100 punktów do 5-10 kluczowych zakrętów.
    """
    if len(path_grid) < 3:
        return [grid_map.to_world(p) for p in path_grid]

    smoothed_path = [path_grid[0]]
    current_idx = 0

    while current_idx < len(path_grid) - 1:
        # Szukamy najdalszego punktu, który 'widzimy' z obecnego
        check_idx = len(path_grid) - 1
        while check_idx > current_idx + 1:
            if grid_map.line_of_sight(smoothed_path[-1], path_grid[check_idx]):
                break
            check_idx -= 1

        smoothed_path.append(path_grid[check_idx])
        current_idx = check_idx

    return [grid_map.to_world(p) for p in smoothed_path]


def a_star_search(grid_map, start_world, end_world):
    start_node = grid_map.to_grid(start_world)
    end_node = grid_map.to_grid(end_world)

    # Walidacja start/stop
    if not grid_map.is_walkable(start_node):
        start_node = find_nearest_walkable(grid_map, start_node, max_radius=6)  # Zmniejszony radius dla wydajności
        if start_node is None: return None

    if not grid_map.is_walkable(end_node):
        end_node = find_nearest_walkable(grid_map, end_node, max_radius=6)
        if end_node is None: return None

    open_set = []
    # (f_score, node)
    heapq.heappush(open_set, (0, start_node))

    came_from = {}
    g_score = {start_node: 0}

    iterations = 0
    max_iterations = 3500  # Zmniejszony limit, żeby szybciej odpuścić trudne przypadki

    while open_set:
        iterations += 1
        if iterations > max_iterations:
            # print("DEBUG: A* timeout") 
            return None

        current = heapq.heappop(open_set)[1]

        if current == end_node:
            # Odtwarzanie ścieżki
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start_node)
            path.reverse()

            # TU JEST KLUCZOWA ZMIANA: Zwracamy uproszczoną ścieżkę
            return simplify_path(grid_map, path)

        for dx, dy, cost in NEIGHBORS:
            neighbor = (current[0] + dx, current[1] + dy)

            # Sprawdzenie is_walkable jest najdroższe, robimy je tylko jak trzeba
            if not grid_map.is_walkable(neighbor):
                continue

            tentative_g_score = g_score[current] + cost

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, end_node)
                heapq.heappush(open_set, (f_score, neighbor))

    return None


def find_nearest_walkable(grid_map, start_node, max_radius=10):
    if grid_map.is_walkable(start_node):
        return start_node

    x, y = start_node
    cols, rows = grid_map.cols, grid_map.rows

    for r in range(1, max_radius + 1):
        # Sprawdzanie obwodu kwadratu
        for i in range(-r, r + 1):
            # Sprawdź górę i dół
            if 0 <= x + i < cols:
                if 0 <= y - r < rows and grid_map.grid[x + i, y - r] == 0: return (x + i, y - r)
                if 0 <= y + r < rows and grid_map.grid[x + i, y + r] == 0: return (x + i, y + r)

            # Sprawdź boki (z wyłączeniem rogów, bo już sprawdzone wyżej)
            if i != -r and i != r and 0 <= y + i < rows:
                if 0 <= x - r < cols and grid_map.grid[x - r, y + i] == 0: return (x - r, y + i)
                if 0 <= x + r < cols and grid_map.grid[x + r, y + i] == 0: return (x + r, y + i)
    return None