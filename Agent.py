import numpy as np
from PathFinding import a_star_search  # <--- Upewnij się, że masz ten import!


class Agent:
    def __init__(self, position, waypoints, grid_map, desired_speed=1.3, radius=0.2, spawn_time=0.0):

        self.position = np.array(position, dtype=np.float32)
        self.velocity = np.zeros(2)
        self.desired_speed = desired_speed
        self.radius = radius

        self.spawn_time = spawn_time
        # Agent jest aktywny od razu tylko jeśli spawn_time <= 0
        self.active = (self.spawn_time <= 0.0)

        # Referencje niezbędne do planowania
        self.grid_map = grid_map
        self.waypoints = waypoints  # Lista celów strategicznych [{'pos':(x,y), 'wait':t}, ...]
        self.waypoint_index = 0  # Który cel strategiczny teraz realizujemy

        # Ścieżka lokalna (A*) do aktualnego waypointa
        self.local_path = []
        self.local_path_index = 0

        # Aktualny cel fizyczny (mikro-krok)
        self.goal = None

        # Zmienne czekania
        self.is_waiting = False
        self.wait_timer = 0.0

        self.id = np.random.randint(1000, 9999)  # ID do debugowania

        # Jeśli agent startuje od razu (spawn_time=0), planujemy pierwszy ruch
        if self.active:
            self._plan_next_segment()

    def _plan_next_segment(self):
        """
        Oblicza ścieżkę A* z aktualnej pozycji do następnego Waypointa.
        """
        # Czy skończyliśmy wszystkie cele?
        if self.waypoint_index >= len(self.waypoints) - 1:
            # print(f"Agent {self.id}: Koniec zakupów.")
            self.active = False
            self.goal = None
            return

        # Celem jest następny punkt na liście zakupów
        target_node = self.waypoints[self.waypoint_index + 1]
        target_pos = target_node['pos']

        # Szukamy ścieżki A* (tylko na ten krótki odcinek!)
        path_segment = a_star_search(self.grid_map, self.position, target_pos)

        if path_segment is None or len(path_segment) < 1:
            print(f"⚠️ Agent {self.id}: Zablokowany w drodze do {target_pos}. Pomijam cel.")
            self.waypoint_index += 1
            self._plan_next_segment()
            return

        # Zapisujemy nową lokalną ścieżkę
        self.local_path = [np.array(p, dtype=float) for p in path_segment]
        self.local_path_index = 0

        # Ustawiamy pierwszy mikro-cel
        if len(self.local_path) > 0:
            self.goal = self.local_path[0]

    def desired_direction(self):
        if self.goal is None or not self.active or self.is_waiting:
            return np.zeros(2)

        dir_vec = self.goal - self.position
        norm = np.linalg.norm(dir_vec)
        return dir_vec / norm if norm > 1e-6 else np.zeros(2)

    def advance_path(self, threshold=0.5):
        """Sprawdza dotarcie do celu i zarządza logiką przechodzenia dalej."""
        if not self.active or self.is_waiting or self.goal is None:
            return

        dist = np.linalg.norm(self.goal - self.position)

        if dist < threshold:
            # 1. Przesuwamy się po ścieżce lokalnej (A*)
            self.local_path_index += 1

            if self.local_path_index < len(self.local_path):
                # Idziemy do kolejnego punktu ze ścieżki A*
                self.goal = self.local_path[self.local_path_index]
            else:
                # 2. Dotarliśmy do końca odcinka A* (czyli do Waypointa)
                # Sprawdzamy czy trzeba tu czekać
                target_node = self.waypoints[self.waypoint_index + 1]
                wait_time = target_node.get('wait', 0.0)

                if wait_time > 0:
                    self.is_waiting = True
                    self.wait_timer = wait_time
                else:
                    self._finish_waypoint()

    def _finish_waypoint(self):
        """Zalicza aktualny Waypoint i planuje drogę do następnego."""
        self.waypoint_index += 1
        self._plan_next_segment()

    def update(self, force, dt):
        # 1. Obsługa opóźnionego spawnu
        if not self.active and self.spawn_time > 0:
            self.spawn_time -= dt
            if self.spawn_time <= 0:
                self.active = True
                self._plan_next_segment()
            return

        if not self.active:
            return

        # 2. Logika czekania
        if self.is_waiting:
            self.wait_timer -= dt
            self.velocity *= 0.8  # Hamowanie
            self.position += self.velocity * dt

            if self.wait_timer <= 0:
                self.is_waiting = False
                self._finish_waypoint()  # Koniec czekania -> planujemy dalej
            return

        # 3. Logika ruchu fizycznego
        acc = force
        self.velocity += acc * dt
        self.position += self.velocity * dt

        self.advance_path()

    # --- Property dla kompatybilności z Visualization.py ---
    @property
    def path(self):
        """
        Zwraca aktualną lokalną ścieżkę w formacie oczekiwanym przez wizualizację.
        Visualization.py spodziewa się listy słowników [{'pos': ...}].
        """
        if not self.local_path:
            return []
        return [{'pos': p} for p in self.local_path]

    @property
    def path_index(self):
        """
        Visualization.py używa tego do rysowania zielonej kropki.
        """
        return self.local_path_index