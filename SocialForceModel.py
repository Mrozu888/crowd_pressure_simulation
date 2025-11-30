import numpy as np


class SocialForceModel:
    """
    Implements the Social Force Model for pedestrian dynamics simulation.
    
    Based on the model by Helbing and Molnár, this class computes the forces
    that govern agent movement including goal-directed forces, interpersonal
    repulsion, and wall avoidance forces.
    
    The model combines three main force components:
    1. Goal-directed force: Drives agents toward their destinations
    2. People repulsion force: Maintains personal space between agents
    3. Wall repulsion force: Prevents collisions with boundaries
    4. Damping force: Provides velocity stabilization
    
    Attributes:
        A (float): Strength of agent-agent repulsion force
        B (float): Range of agent-agent repulsion force  
        A_w (float): Strength of agent-wall repulsion force
        B_w (float): Range of agent-wall repulsion force
        desired_speed (float): Preferred movement speed for agents
        relax_time (float): Characteristic reaction time for velocity adjustments
    """
    
    def __init__(self, params):
        """
        Initialize the Social Force Model with physical parameters.
        
        Args:
            params (dict): Dictionary containing force model parameters:
                - A: Agent-agent repulsion strength (default: 2.0)
                - B: Agent-agent repulsion range (default: 0.5)
                - A_w: Agent-wall repulsion strength (default: 10.0) 
                - B_w: Agent-wall repulsion range (default: 0.2)
                - desired_speed: Preferred movement speed (default: 1.2)
                - tau: Relaxation time constant (default: 0.5)
                
        Note:
            Higher A/A_w values create stronger repulsion forces.
            Higher B/B_w values create longer-range repulsion effects.
            Typical desired_speed ≈ 1.2 m/s represents normal walking speed.
        """
        self.A = params.get("A", 1.0)          # Agent-agent repulsion intensity
        self.B = params.get("B", 0.1)          # Agent-agent repulsion range
        self.A_w = params.get("A_w", 10.0)     # Agent-wall repulsion intensity
        self.B_w = params.get("B_w", 0.1)      # Agent-wall repulsion range
        self.desired_speed = params.get("desired_speed", 1.2)  # m/s
        self.relax_time = params.get("tau", 0.5)  # Agent reaction time

    def compute_force(self, agent, agents, walls, cashiers=None):
        """
        Compute the total force acting on an agent from all sources.
        
        Args:
            agent (Agent): The agent for whom forces are being computed
            agents (list): List of all other agents in the environment
            walls (list): List of wall segments as ((x1,y1), (x2,y2)) tuples
            
        Returns:
            np.array: Total 2D force vector [fx, fy] acting on the agent
            
        Force Composition:
            f_goal: Driving force toward the agent's goal
            f_people: Repulsive forces from other agents
            f_walls: Repulsive forces from walls and boundaries  
            f_damping: Velocity damping for numerical stability
            
        Note:
            All forces are summed linearly. The damping force prevents
            velocity oscillations and provides more realistic movement.
        """
        if cashiers is None:
            cashiers = []
        f_goal = self._force_to_goal(agent)
        f_people = self._force_from_people(agent, agents)
        f_walls = self._force_from_walls(agent, walls)
        f_damping = -0.2 * agent.velocity  # Simple motion resistance (friction)
        f_cashiers = self._force_from_cashiers(agent, cashiers)

        total_force = f_goal + f_people + f_walls + f_damping + f_cashiers
        return total_force

    # -------------------
    # Model Components:
    # -------------------

    def _force_to_goal(self, agent):
        """
        Compute the goal-directed driving force.
        
        This force represents the agent's intention to move toward their
        destination at their desired speed. It follows the form:
            F_goal = (v_desired * direction - v_current) / relaxation_time
            
        Args:
            agent (Agent): The agent being evaluated
            
        Returns:
            np.array: 2D goal-directed force vector
            
        Physics Interpretation:
            - desired_vel: The velocity the agent WANTS to have
            - agent.velocity: The velocity the agent CURRENTLY has  
            - relax_time: How quickly the agent can adjust velocity
            
        This is essentially a proportional controller that corrects the
        agent's current velocity toward their desired velocity.
        """
        desired_dir = agent.desired_direction()
        desired_vel = desired_dir * self.desired_speed
        return (desired_vel - agent.velocity) / self.relax_time

    def _force_from_people(self, agent, agents):
        """
        Compute repulsive forces from other agents using Helbing's model.

        ... (reszta docstringa) ...
        """
        force = np.zeros(2)
        for other in agents:
            if other is agent:
                continue  # Skip self

            # --- DODANA LINIA ---
            # Ignoruj agentów, którzy nie są aktywni (czekają na spawn lub wyszli)
            # To jest kluczowe, aby zapobiec "eksplozji" sił w strefie spawnu.
            if not other.active:
                continue
            # --- KONIEC DODANEJ LINII ---

            # Calculate distance and direction to other agent
            d_vec = agent.position - other.position
            dist = np.linalg.norm(d_vec)
            if dist == 0:
                # Jeśli jakimś cudem są w tym samym punkcie, lekko ich rozsuń
                d_vec = np.random.rand(2) * 0.01
                dist = np.linalg.norm(d_vec)

            n_ij = d_vec / dist  # Normalized direction vector

            # Calculate overlap of personal spaces
            overlap = agent.radius + other.radius - dist

            # Exponential repulsion force (social force)
            force += self.A * np.exp(overlap / self.B) * n_ij

            # Physical contact force when agents actually overlap
            if overlap > 0:
                force += 200 * overlap * n_ij  # "Body force" during collision

        return force

    def _force_from_walls(self, agent, walls):
        """
        Compute repulsive forces from wall segments.
        
        For each wall segment, finds the closest point on the wall to the agent
        and applies a repulsive force based on distance. Uses the same
        exponential form as agent-agent repulsion but with different parameters.
        
        Args:
            agent (Agent): The agent experiencing the forces
            walls (list): Wall segments as ((x1,y1), (x2,y2)) tuples
            
        Returns:
            np.array: Cumulative repulsive force from all walls
            
        Algorithm:
            1. For each wall segment, find closest point to agent
            2. Calculate distance to that closest point
            3. Apply exponential repulsion based on distance
            4. Add physical contact force if agent penetrates wall
            
        Note:
            Walls are typically stronger (higher A_w) than agent repulsion
            since people prefer to maintain more distance from fixed obstacles.
        """
        force = np.zeros(2)

        for (p1, p2) in walls:
            # Convert to numpy arrays and get wall vector
            wall_vec = np.array(p2) - np.array(p1)
            wall_length = np.linalg.norm(wall_vec)
            
            if wall_length == 0:
                continue  # Skip zero-length walls
                
            wall_dir = wall_vec / wall_length  # Normalized wall direction
            
            # Project agent position onto wall line
            diff = agent.position - np.array(p1)
            proj = np.dot(diff, wall_dir)
            
            # Clamp projection to wall segment boundaries
            proj = np.clip(proj, 0, wall_length)
            
            # Find closest point on wall segment to agent
            closest_point = np.array(p1) + proj * wall_dir
            
            # Calculate distance vector and magnitude
            d_vec = agent.position - closest_point
            dist = np.linalg.norm(d_vec)
            
            if dist == 0:
                continue  # Agent exactly on wall
                
            n_iw = d_vec / dist  # Normalized direction from wall to agent
            
            # Calculate penetration into wall (positive = inside wall)
            overlap = agent.radius - dist
            
            # Exponential repulsion from wall
            force += self.A_w * np.exp(overlap / self.B_w) * n_iw
            
            # Physical contact force when agent penetrates wall
            if overlap > 0:
                force += 200 * overlap * n_iw  # Contact force
                
        return force
    
    def _force_from_cashiers(self, agent, cashiers):

        total = np.zeros(2, dtype=float)

        for reg in cashiers:
            x, y = reg["pos"]
            w, h = reg["size"]

        # współrzędne środka kasy

        # oblicz najbliższy punkt prostokąta do agenta
            nearest_x = np.clip(agent.position[0], x, x + w)
            nearest_y = np.clip(agent.position[1], y, y + h)
            nearest_point = np.array([nearest_x, nearest_y], dtype=float)

            d_vec = agent.position - nearest_point
            dist = np.linalg.norm(d_vec)

            if dist < 1e-6:
                continue

            n = d_vec / dist
            overlap = agent.radius - dist

        # siła eksp., jak przy ścianach
            force = self.A_w * np.exp(overlap / self.B_w) * n

        # kontakt fizyczny
            if overlap > 0:
                force += 200 * overlap * n

            total += force

        return total
