import numpy as np


class Agent:

    def __init__(self, position, goal=None, desired_speed=1.3, radius=0.15, path=None, spawn_time=0.0):

        self.position = np.array(position, dtype=np.float32)
        self.velocity = np.zeros(2)
        self.desired_speed = desired_speed
        self.radius = radius

        self.spawn_time = spawn_time
        self.active = (self.spawn_time <= 0.0)

        self.is_waiting = False
        self.wait_timer = 0.0
        self.finished_path = False 
        self.exited = False     
        if path is not None:
            # path to teraz lista słowników [{'pos': (x,y), 'wait': czas}, ...]
            self.path = path
            self.path_index = 0
            # Cel to współrzędne pierwszego punktu
            self.goal = np.array(self.path[0]['pos'], dtype=float)
        else:
            self.path = None
            self.path_index = None
            self.goal = np.array(goal, dtype=float) if goal is not None else None

    def desired_direction(self):
        """Return normalized direction toward the current goal or waypoint."""
        # Jeśli nie ma celu, nieaktywny LUB CZEKA -> nie ciągnij nigdzie
        if self.goal is None or not self.active or self.is_waiting:
            return np.zeros(2)

        dir_vec = self.goal - self.position
        norm = np.linalg.norm(dir_vec)
        return dir_vec / norm if norm > 1e-6 else np.zeros(2)

    def advance_path(self, threshold=0.2):  # Zwiększyłem lekko threshold
        """
        Check if agent reached current waypoint and move to next one.
        Handles waiting time.
        """
        if self.path is None or not self.active or self.goal is None:
            return

        # Jeśli aktualnie czeka, nie sprawdzamy dystansu (logika czasu jest w update)
        if self.is_waiting:
            return

        dist = np.linalg.norm(self.goal - self.position)

        if dist < threshold:
            # Sprawdzamy, czy ten punkt wymaga czekania
            current_node = self.path[self.path_index]
            wait_time = current_node.get('wait', 0.0)

            if wait_time > 0:
                # Rozpoczynamy czekanie
                self.is_waiting = True
                self.wait_timer = wait_time
                # NIE zwiększamy path_index, zrobimy to jak czas minie
            else:
                # Brak czekania, idziemy dalej
                self._next_waypoint()

    def _next_waypoint(self):
        """Przełącza na kolejny punkt ścieżki"""
        self.path_index += 1
        if self.path_index < len(self.path):
            self.goal = np.array(self.path[self.path_index]['pos'], dtype=float)
            self.is_waiting = False
        else:
            self.finished_path = True
            self.goal = None

    def update(self, force, dt):
        """Update agent’s velocity and position under given force and timestep."""
        if not self.active:
            return

        # LOGIKA CZEKANIA 
        if self.is_waiting:
            self.wait_timer -= dt

            # Wygaszamy prędkość (tarcie), żeby agent stanął w miejscu
            self.velocity *= 0.8
            self.position += self.velocity * dt

            if self.wait_timer <= 0:
                self.is_waiting = False
                self._next_waypoint()  # Czas minął, idziemy dalej

            return  # Nie aplikujemy sił SFM podczas czekania

        acc = force
        self.velocity += acc * dt
        self.position += self.velocity * dt

        self.advance_path()