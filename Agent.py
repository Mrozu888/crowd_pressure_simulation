import numpy as np

class Agent:
    def __init__(self, position, goal, desired_speed, radius=0.3):
        self.position = np.array(position, dtype=float)
        self.velocity = np.zeros(2)
        self.goal = np.array(goal, dtype=float)
        self.desired_speed = desired_speed
        self.radius = radius
        self.active = True  # czy agent wciąż w symulacji

    def desired_direction(self):
        dir_vec = self.goal - self.position
        norm = np.linalg.norm(dir_vec)
        return dir_vec / norm if norm > 0 else np.zeros(2)

    def update(self, force, dt):
        if not self.active:
            return
        acc = force
        self.velocity += acc * dt
        self.position += self.velocity * dt
