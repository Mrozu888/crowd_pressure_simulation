class Simulation:
    """
    Main simulation controller that manages the time evolution of the environment.
    
    This class orchestrates the entire simulation loop, updating all agents
    according to the Social Force Model and managing agent lifecycle. It handles
    the temporal progression of the simulation from initialization to completion.
    
    The simulation follows a discrete-time update scheme where each time step:
    1. Computes forces for all active agents
    2. Updates agent positions and velocities
    3. Removes agents that have exited the environment
    
    Attributes:
        env (Environment): The simulation environment containing agents and obstacles
        dt (float): Time step size for numerical integration (in seconds)
        steps (int): Total number of simulation steps to execute
    """
    
    def __init__(self, environment, config):
        """
        Initialize the simulation with environment and configuration.
        
        Args:
            environment (Environment): Pre-configured environment with agents, 
                                     walls, and physics model
            config (dict): Simulation parameters including:
                - dt: Time step size for numerical integration
                - steps: Maximum number of simulation steps to run
                
        Note:
            The time step (dt) is critical for simulation stability. Typical
            values range from 0.01 to 0.05 seconds. Smaller values improve
            accuracy but increase computational cost.
        """
        self.env = environment
        self.dt = config["dt"]  # Integration time step
        self.steps = config["steps"]  # Total simulation duration in steps

    def update(self):
        """
        Execute one complete simulation time step.
        
        This method advances the simulation by one time increment (dt):
        
        Process Flow:
        1. For each ACTIVE agent:
           - Compute total force from goals, other agents, and walls
           - Update agent position and velocity using Euler integration
        2. Remove agents that have successfully exited through the door
        3. Environment state is now advanced by dt seconds
        
        Agent Processing:
        - Only active agents are updated (exited agents are skipped)
        - Force computation considers all agents and walls
        - Position/velocity updates use simple Euler integration
        - Exit checking happens after all agents have moved
        
        Note:
            This method should be called repeatedly in a loop to run the
            complete simulation. Each call represents one frame of simulation.
        """
        # Step 1: Update all active agents
        for agent in self.env.agents:
            # print("tu",agent.position, agent.velocity)
            if not agent.active:
                continue  # Skip inactive (exited) agents
                
            # Compute total force acting on this agent from all sources
            force = self.env.model.compute_force(agent, self.env.agents, self.env.walls+self.env.shelves)
            # print("force: ",force)
            # Apply force to update agent's position and velocity
            agent.update(force, self.dt)
        
        # Step 2: Check for and remove agents that have exited
        self.env.remove_exited_agents()