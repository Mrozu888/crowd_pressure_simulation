import pygame

class Visualization:
    """
    A PyGame-based visualization system for the Social Force Model simulation.
    
    This class handles all graphical rendering of the simulation environment,
    including walls, doors, and agents. It provides real-time visual feedback
    of agent movements and interactions within the simulated space.
    
    Attributes:
        env: Reference to the simulation environment containing all entities
        scale: Scaling factor for converting simulation coordinates to pixels
        screen: PyGame surface object representing the display window
    """
    
    def __init__(self, env):
        """
        Initialize the visualization system.
        
        Args:
            env: The simulation environment object containing:
                - width: Environment width in simulation units
                - height: Environment height in simulation units  
                - scale: Base scaling factor for coordinate conversion
                - walls: List of wall segments as ((x1,y1), (x2,y2)) tuples
                - door: Dictionary containing door position and dimensions
                - agents: List of agent objects with position and radius
                
        Note:
            The display window size is calculated as (env.width * scale, env.height * scale)
            to maintain consistent scaling across all rendered elements.
        """
        self.env = env
        self.scale = env.scale
        self.screen = pygame.display.set_mode(
            (int(env.width * self.scale), int(env.height * self.scale))
        )
        pygame.display.set_caption("Social Force Model Simulation")

    def draw(self):
        """
        Render the complete simulation frame with all visual elements.
        
        Drawing order (back to front):
        1. Background (light gray)
        2. Walls (black lines)
        3. Door (green vertical line)
        4. Agents (blue circles)
        
        Rendering process:
        - All coordinates are scaled from simulation units to pixels
        - Only active agents are rendered
        - Display is updated via pygame.display.flip() after drawing
        """
        # Clear screen with light gray background
        self.screen.fill((240, 240, 240))

        # Draw walls as black line segments
        # Walls are defined as pairs of points (p1, p2) in simulation coordinates
        for (p1, p2) in self.env.walls:
            x1, y1 = int(p1[0] * self.scale), int(p1[1] * self.scale)
            x2, y2 = int(p2[0] * self.scale), int(p2[1] * self.scale)
            pygame.draw.line(self.screen, (0, 0, 0), (x1, y1), (x2, y2), 4) # 4 - Line thickness

        # Draw door as a green vertical line
        # Door position and dimensions are defined in the environment
        door = self.env.door
        pygame.draw.line(
            self.screen,
            (0, 200, 0),  # Green color
            (int(door["x"] * self.scale), int(door["y_min"] * self.scale)),
            (int(door["x"] * self.scale), int(door["y_max"] * self.scale)),
            4,  # Line thickness
        )

        # Draw agents as blue circles
        # Each agent has position, radius, and active status
        for a in self.env.agents:
            if not a.active:
                continue  # Skip inactive agents (those who exited)
            x, y = int(a.position[0] * self.scale), int(a.position[1] * self.scale)
            pygame.draw.circle(self.screen, (50, 100, 255), (x, y), int(a.radius * self.scale))

        # Update the display with the newly drawn frame
        pygame.display.flip()