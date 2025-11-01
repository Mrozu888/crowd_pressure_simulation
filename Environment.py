import numpy as np
from Agent import Agent
from SocialForceModel import SocialForceModel

class Environment:
    """
    Main simulation environment for the Social Force Model.
    
    This class represents the physical space where agents navigate,
    including walls, doors, and other environmental features. It manages agent
    creation, movement physics via the Social Force Model, and exit conditions.
    
    The environment uses a scaled coordinate system where simulation units
    are converted to display pixels using the scale factor.
    
    Attributes:
        scale (float): Conversion factor from simulation units to pixels
        width (float): Environment width in simulation units
        height (float): Environment height in simulation units
        exit (np.array): Target exit position that agents aim to reach
        door (dict): Door configuration with position and dimensions
        walls (list): List of wall segments as ((x1,y1), (x2,y2)) tuples
        model (SocialForceModel): Physics model controlling agent movement
        agents (list): List of Agent objects representing pedestrians
    """
    
    def __init__(self, config):
        """
        Initialize the environment from configuration data.
        
        Args:
            config (dict): Configuration dictionary containing:
                - environment: Environment dimensions and features
                - sfm: Social Force Model parameters
                - n_agents: Number of agents to create
                
        The initialization process:
        1. Extracts environment configuration (scale, dimensions, exit, door)
        2. Builds wall geometry with door openings
        3. Initializes the Social Force Model
        4. Creates the specified number of agents
        """
        env_conf = config["environment"]
        sfm_conf = config["sfm"]

        # Environment geometry and scaling
        self.scale = env_conf["scale"]
        self.width = env_conf["width"] / self.scale  # Convert to simulation units
        self.height = env_conf["height"] / self.scale  # Convert to simulation units
        self.exit = np.array(env_conf["exit"])  # Target position for agents
        self.door = env_conf["door"]  # Door configuration dictionary
        self.walls = self._build_walls(env_conf["walls"], self.door)  # Build walls with door openings

        # Initialize physics model and create agents
        self.model = SocialForceModel(sfm_conf)
        self.agents = self._create_agents(config["n_agents"], self.exit, sfm_conf["desired_speed"])

    def _build_walls(self, walls, door):
        """
        Construct wall segments with door openings.
        
        This method processes the wall definitions and creates openings where
        doors are located. Specifically, it splits vertical walls at the door
        position to create passages.
        
        Args:
            walls (list): Original wall segments as ((x1,y1), (x2,y2)) tuples
            door (dict): Door configuration with x, y_min, y_max coordinates
            
        Returns:
            list: Modified wall segments with door openings
            
        Note:
            Currently only handles vertical walls (same x-coordinate for both points).
            Horizontal walls and other orientations would need additional logic.
        """
        new_walls = []
        for p1, p2 in walls:
            # Check if this is a vertical wall at the door's x-position
            if p1[0] == door["x"] and p2[0] == door["x"]:
                # Split the wall into two segments: above and below the door
                # Top segment: from top of environment to top of door
                new_walls.append(((p1[0], 0), (p2[0], door["y_min"])))
                # Bottom segment: from bottom of door to bottom of environment
                new_walls.append(((p1[0], door["y_max"]), (p2[0], p2[1])))
            else:
                # Keep walls that aren't at the door position unchanged
                new_walls.append((p1, p2))
        return new_walls

    def _create_agents(self, n, goal, speed):
        """
        Create and initialize agents at random positions.
        
        Args:
            n (int): Number of agents to create
            goal (np.array): Target position that agents will move toward
            speed (float): Desired movement speed for agents
            
        Returns:
            list: List of initialized Agent objects
            
        Note:
            Agents are randomly positioned in the area x=[2,6], y=[2,10]
            to avoid spawning too close to walls or the door.
        """
        agents = []
        for _ in range(n):
            # Random position within safe spawning area
            x = np.random.uniform(2, 6)
            y = np.random.uniform(2, 10)
            agents.append(Agent((x, y), goal, speed))
        return agents

    def remove_exited_agents(self):
        """
        Deactivate agents that have successfully exited through the door.
        
        Exit conditions:
        - Agent's x-position is beyond the door (door_x + 0.5 buffer)
        - Agent's y-position is within the door's vertical range
        - Agent is still active
        
        This method marks agents as inactive rather than removing them from
        the list, allowing the visualization to handle inactive agents appropriately.
        """
        for a in self.agents:
            # Check if agent has passed through the door opening
            if (a.position[0] > self.door["x"] + 0.5 and
                self.door["y_min"] < a.position[1] < self.door["y_max"]):
                a.active = False  # Mark as exited/inactive
