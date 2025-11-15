import numpy as np


class Agent:
    """
    Represents a pedestrian agent in the Social Force Model simulation.
    Now supports following a multi-point path and delayed spawning.
    """

    def __init__(self, position, goal=None, desired_speed=1.3, radius=0.2, path=None, spawn_time=0.0):
        """
        Initialize a new agent with specified properties.

        Args:
            position (tuple/list): Starting position as (x, y)
            goal (tuple/list, optional): Single final target position
            desired_speed (float): Preferred cruising speed
            radius (float, optional): Agent's physical radius
            path (list of tuples, optional): Sequence of waypoints [(x1,y1), (x2,y2), ...]
            spawn_time (float, optional): Simulation time (in seconds) when the agent should become active.
        """
        self.position = np.array(position, dtype=np.float32)
        # print(self.position) # Usunąłem printy dla czytelności
        self.velocity = np.zeros(2)
        self.desired_speed = desired_speed
        self.radius = radius

        # --- ZMIANY ---
        self.spawn_time = spawn_time
        # Agent jest aktywny tylko jeśli jego czas spawnu już minął (lub jest równy 0)
        self.active = (self.spawn_time <= 0.0)
        # --- KONIEC ZMIAN ---

        # If path provided, use it; otherwise, treat goal as single endpoint
        if path is not None:
            self.path = [np.array(p, dtype=float) for p in path]
            self.path_index = 0
            # Ustawiamy pierwszy cel, nawet jeśli agent jest nieaktywny.
            # Metoda desired_direction() i tak zwróci zero, jeśli self.active == False
            self.goal = self.path[0]
        else:
            self.path = None
            self.path_index = None
            self.goal = np.array(goal, dtype=float) if goal is not None else None

    def desired_direction(self):
        """Return normalized direction toward the current goal or waypoint."""
        # --- ZMIANA ---
        # Agent nie ma celu, jeśli jest nieaktywny
        if self.goal is None or not self.active:
            # --- KONIEC ZMIANY ---
            return np.zeros(2)

        dir_vec = self.goal - self.position
        norm = np.linalg.norm(dir_vec)
        return dir_vec / norm if norm > 1e-6 else np.zeros(2)

    def advance_path(self, threshold=0.2):
        """
        Check if agent reached current waypoint and move to next one.
        If at end of path, deactivate the agent.
        """
        if self.path is None or not self.active:
            return

        # Distance to current goal
        dist = np.linalg.norm(self.goal - self.position)

        # If reached current waypoint
        if dist < threshold:
            self.path_index += 1
            if self.path_index < len(self.path):
                self.goal = self.path[self.path_index]
            else:
                self.active = False  # Path complete
                self.goal = None

    def update(self, force, dt):
        """Update agent’s velocity and position under given force and timestep."""
        if not self.active:
            return

        acc = force  # assuming unit mass
        self.velocity += acc * dt
        self.position += self.velocity * dt

        # After moving, check if we reached current waypoint
        self.advance_path()