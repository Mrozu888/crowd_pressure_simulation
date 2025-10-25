import numpy as np

class SocialForceModel:
    def __init__(self, params):
        self.A = params.get("A", 2.0)          # intensywność odpychania agent-agent
        self.B = params.get("B", 0.5)          # zakres odpychania agent-agent
        self.A_w = params.get("A_w", 10.0)     # intensywność odpychania agent-ściana
        self.B_w = params.get("B_w", 0.2)      # zakres odpychania agent-ściana
        self.desired_speed = params.get("desired_speed", 1.2)
        self.relax_time = params.get("tau", 0.5)  # czas reakcji agenta

    def compute_force(self, agent, agents, walls):
        """
        Oblicza całkowitą siłę działającą na agenta
        """
        f_goal = self._force_to_goal(agent)
        f_people = self._force_from_people(agent, agents)
        f_walls = self._force_from_walls(agent, walls)
        f_damping = -0.2 * agent.velocity  # prosty opór ruchu (tarcie)

        total_force = f_goal + f_people + f_walls + f_damping
        return total_force

    # -------------------
    # Składowe modelu:
    # -------------------

    def _force_to_goal(self, agent):
        """
        Siła dążenia do celu: (v_desired * e_i - v_i) / tau
        """
        desired_dir = agent.desired_direction()
        desired_vel = desired_dir * self.desired_speed
        return (desired_vel - agent.velocity) / self.relax_time

    def _force_from_people(self, agent, agents):
        """
        Odpychanie od innych agentów wg modelu Helbinga
        """
        force = np.zeros(2)
        for other in agents:
            if other is agent:
                continue
            d_vec = agent.position - other.position
            dist = np.linalg.norm(d_vec)
            if dist == 0:
                continue
            n_ij = d_vec / dist
            overlap = agent.radius + other.radius - dist
            # Odpychanie i siła fizycznego kontaktu
            force += self.A * np.exp(overlap / self.B) * n_ij
            if overlap > 0:
                force += 200 * overlap * n_ij  # „siła ciała” przy kolizji
        return force

    def _force_from_walls(self, agent, walls):
        """
        Siła odpychania od ścian (segmenty linii)
        """
        force = np.zeros(2)
        for (p1, p2) in walls:
            # wektor od ściany do agenta
            wall_vec = np.array(p2) - np.array(p1)
            wall_dir = wall_vec / np.linalg.norm(wall_vec)
            # projekcja pozycji agenta na linię ściany
            diff = agent.position - np.array(p1)
            proj = np.dot(diff, wall_dir)
            proj = np.clip(proj, 0, np.linalg.norm(wall_vec))
            closest_point = np.array(p1) + proj * wall_dir
            d_vec = agent.position - closest_point
            dist = np.linalg.norm(d_vec)
            if dist == 0:
                continue
            n_iw = d_vec / dist
            overlap = agent.radius - dist
            # Odpychanie eksponencjalne + kontakt
            force += self.A_w * np.exp(overlap / self.B_w) * n_iw
            if overlap > 0:
                force += 200 * overlap * n_iw  # siła kontaktu
        return force
