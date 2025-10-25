import numpy as np

class Agent:
    """
    Represents a pedestrian agent in the Social Force Model simulation.
    
    Each agent has physical properties (position, velocity, size) and behavioral
    characteristics (goal, desired speed) that govern their movement through
    the environment. The agent responds to social forces while navigating toward
    its target destination.
    
    Attributes:
        position (np.array): Current 2D position in simulation coordinates [x, y]
        velocity (np.array): Current 2D velocity vector [vx, vy]
        goal (np.array): Target position the agent is trying to reach [x, y]
        desired_speed (float): Preferred movement speed in simulation units/sec
        radius (float): Physical radius of the agent for collision detection
        active (bool): Whether the agent is still participating in simulation
    """
    
    def __init__(self, position, goal, desired_speed, radius=0.3):
        """
        Initialize a new agent with specified properties.
        
        Args:
            position (tuple/list): Starting position as (x, y) coordinates
            goal (tuple/list): Target position as (x, y) coordinates  
            desired_speed (float): Preferred cruising speed in sim units/second
            radius (float, optional): Physical size for collision detection. 
                                    Defaults to 0.3 simulation units.
                                    
        Note:
            The radius of 0.3 units represents approximately 30cm for a typical
            pedestrian, assuming 1 simulation unit = 1 meter.
        """
        self.position = np.array(position, dtype=float)
        self.velocity = np.zeros(2)  # Start with zero velocity
        self.goal = np.array(goal, dtype=float)
        self.desired_speed = desired_speed
        self.radius = radius
        self.active = True  # Whether agent is still in simulation

    def desired_direction(self):
        """
        Calculate the normalized direction vector toward the agent's goal.
        
        Returns:
            np.array: Normalized 2D direction vector [dx, dy] pointing toward goal.
                     Returns zero vector if already at goal position.
                     
        Calculation:
            direction = (goal - position) / ||goal - position||
            
        Note:
            This represents the agent's intended movement direction without
            considering obstacles or other agents. The Social Force Model will
            combine this with other forces to determine actual movement.
        """
        dir_vec = self.goal - self.position
        norm = np.linalg.norm(dir_vec)
        # Normalize (vector to goal with length 1) if not at goal, otherwise return zero vector
        return dir_vec / norm if norm > 0 else np.zeros(2)

    def update(self, force, dt):
        """
        Update agent's state based on applied forces and time step.
        
        Implements Newtonian mechanics:
        - Acceleration = Force (assuming unit mass)
        - Velocity += Acceleration × time
        - Position += Velocity × time
        
        Args:
            force (np.array): Total 2D force vector applied to the agent [fx, fy]
            dt (float): Time step in seconds for numerical integration
            
        Note:
            This method uses the Euler integration method which is simple
            but may accumulate numerical errors over time. More sophisticated
            integrators could be used for improved accuracy.
            
        Example:
            If an agent receives social forces from the environment, this method
            converts those forces into actual movement.
        """
        if not self.active:
            return  # Skip update for inactive (exited) agents
            
        # Apply forces to update velocity (assuming unit mass: a = F/m = F)
        acc = force
        self.velocity += acc * dt
        
        # Update position based on current velocity
        self.position += self.velocity * dt