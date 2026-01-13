import numpy as np


class SocialForceModel:
    """
    Implements the Social Force Model for pedestrian dynamics simulation.
    Optimized with NumPy vectorization.
    """
    
    def __init__(self, params):
        self.A = params.get("A", 2.0)
        self.B = params.get("B", 0.5)
        self.A_w = params.get("A_w", 10.0)
        self.B_w = params.get("B_w", 0.2)
        self.desired_speed = params.get("desired_speed", 1.2)
        self.relax_time = params.get("tau", 0.5)
        
        # Współczynnik tarcia ślizgowego (kappa)
        # W oryginale Helbinga wartości są rzędu 2.4e5, ale przy naszych jednostkach
        # i dt=0.05, bezpieczniej zacząć od mniejszej wartości, by nie wystrzelić agentów.
        self.kappa = params.get("kappa", 6.0)

    def compute_force(self, agent, agents_pos, agents_radii, agents_vel, walls, cashiers=None):
        """
        Compute the total force acting on an agent.
        
        Args:
            agent: The agent object (target).
            agents_pos (np.ndarray): Array of shape (N, 2) positions.
            agents_radii (np.ndarray): Array of shape (N,) radii.
            agents_vel (np.ndarray): Array of shape (N, 2) velocities (NEW).
            walls: List of wall segments.
        """
        # Jeśli agent stoi przy kasie -> zero sił
        if getattr(agent, "is_waiting", False):
            return np.zeros(2, dtype=float)

        f_goal = self._force_to_goal(agent)
        
        # Wektoryzowana siła od ludzi (teraz z tarciem)
        f_people = self._force_from_people_vectorized(agent, agents_pos, agents_radii, agents_vel)
        
        # Siła od ścian (teraz z tarciem)
        f_walls = self._force_from_walls(agent, walls)
        
        f_damping = -0.2 * agent.velocity

        total_force = f_goal + f_people + f_walls + f_damping
        return total_force

    def _force_to_goal(self, agent):
        desired_dir = agent.desired_direction()
        desired_vel = desired_dir * self.desired_speed
        return (desired_vel - agent.velocity) / self.relax_time

    def _force_from_people_vectorized(self, agent, all_pos, all_radii, all_vel):
        """
        Calculates repulsive forces AND sliding friction using vectorized NumPy operations.
        """
        if len(all_pos) == 0:
            return np.zeros(2)

        # 1. Wektory różnic i dystanse
        deltas = agent.position - all_pos
        dists = np.linalg.norm(deltas, axis=1)
        
        # Filtrowanie (pomijamy siebie i zbyt odległych)
        valid_mask = (dists > 0.001) & (dists < 3.0)
        
        if not np.any(valid_mask):
            return np.zeros(2)

        valid_deltas = deltas[valid_mask]
        valid_dists = dists[valid_mask]
        valid_radii = all_radii[valid_mask]
        valid_vels = all_vel[valid_mask] # Prędkości sąsiadów

        # 2. Wektory normalne n_ij (od sąsiada do agenta)
        n_ij = valid_deltas / valid_dists[:, np.newaxis]

        # 3. Overlap
        overlaps = (agent.radius + valid_radii) - valid_dists

        # 4. Siła wykładnicza (Social Force)
        repulsion = self.A * np.exp(overlaps / self.B)[:, np.newaxis] * n_ij

        # 5. Siły fizyczne (Body Force + Sliding Friction) - tylko przy kontakcie
        contact_mask = overlaps > 0
        
        if np.any(contact_mask):
            # --- Body Force (Compression) ---
            # k * overlap * n_ij
            contact_overlaps = overlaps[contact_mask]
            contact_n_ij = n_ij[contact_mask]
            
            compression_force = (200.0 * contact_overlaps[:, np.newaxis]) * contact_n_ij
            
            # --- Sliding Friction ---
            # kappa * overlap * (delta_v dot t_ij) * t_ij
            
            # Wektor styczny t_ij (prostopadły do n_ij)
            # Jeśli n = (nx, ny), to t = (-ny, nx)
            contact_t_ij = np.stack([-contact_n_ij[:, 1], contact_n_ij[:, 0]], axis=1)
            
            # Względna prędkość: v_j - v_i (sąsiad - ja)
            # Uwaga: valid_vels to prędkości sąsiadów
            contact_vels = valid_vels[contact_mask]
            rel_vel = contact_vels - agent.velocity
            
            # Rzut prędkości względnej na styczną
            # (dot product wierszami)
            tangential_vel = np.sum(rel_vel * contact_t_ij, axis=1)
            
            # Siła tarcia
            friction_mag = self.kappa * contact_overlaps * tangential_vel
            friction_force = friction_mag[:, np.newaxis] * contact_t_ij
            
            # Dodajemy obie siły fizyczne do akumulatora
            # Tworzymy macierz zer o kształcie repulsion i wstawiamy wyniki
            phys_force = np.zeros_like(repulsion)
            phys_force[contact_mask] = compression_force + friction_force
            
            repulsion += phys_force

        # Suma wszystkich sił
        total_force = np.sum(repulsion, axis=0)
        
        return total_force

    def _force_from_walls(self, agent, walls):
        force = np.zeros(2)
        
        for (p1, p2) in walls:
            wall_vec = np.array(p2) - np.array(p1)
            wall_length = np.linalg.norm(wall_vec)
            if wall_length == 0: continue
                
            # Wektor styczny ściany (znormalizowany)
            wall_dir = wall_vec / wall_length
            
            diff = agent.position - np.array(p1)
            proj = np.dot(diff, wall_dir)
            proj = np.clip(proj, 0, wall_length)
            
            closest_point = np.array(p1) + proj * wall_dir
            d_vec = agent.position - closest_point
            dist = np.linalg.norm(d_vec)
            
            if dist == 0: continue
            if dist > 1.0: continue 
                
            # Wektor normalny od ściany do agenta
            n_iw = d_vec / dist
            overlap = agent.radius - dist
            
            # 1. Repulsion (Exponential)
            force += self.A_w * np.exp(overlap / self.B_w) * n_iw
            
            # 2. Physical Forces (Compression + Friction)
            if overlap > 0:
                # Compression
                force += 200 * overlap * n_iw
                
                # Sliding Friction
                # Względna prędkość (ściana stoi, więc to po prostu prędkość agenta)
                # Rzutujemy prędkość agenta na styczną ściany
                tangential_vel = np.dot(agent.velocity, wall_dir)
                
                # Siła tarcia działa przeciwnie do ruchu wzdłuż ściany
                # F_fric = -kappa * overlap * (v * t) * t
                force -= self.kappa * overlap * tangential_vel * wall_dir
                
        return force