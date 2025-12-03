import pygame
from Config import CONFIG
from Environment import Environment
from Simulation import Simulation
from Visualization import Visualization


def main():
    """
    Main entry point for the Social Force Model simulation application.
    
    This function initializes and runs the complete simulation loop, integrating:
    - Environment setup and agent initialization
    - Physics simulation using the Social Force Model
    - Real-time visualization using PyGame
    - User interaction and frame rate control
    
    The main loop follows the classic game architecture pattern:
    Initialize → Process Input → Update → Render → Repeat
    """
    
    # Initialize PyGame and create clock for frame rate control
    pygame.init()
    clock = pygame.time.Clock()

    # Initialize core simulation components
    env = Environment(CONFIG)      # Physical environment with agents and obstacles
    sim = Simulation(env, CONFIG)  # Simulation controller for time evolution
    vis = Visualization(env)       # Visual rendering system
    # Main simulation loop control flag
    running = True
    
    # ======================
    # MAIN SIMULATION LOOP
    # ======================
    while running:
        # ----------------------
        # INPUT PROCESSING PHASE
        # ----------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Exit when window close button is clicked
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False  # Quit on ESC key
        # --------------------
        # SIMULATION UPDATE PHASE
        # --------------------
        sim.update()  # Advance simulation by one time step
                      # - Updates agent positions and velocities
                      # - Applies social forces
                      # - Removes exited agents

        # --------------------
        # RENDERING PHASE
        # --------------------
        vis.draw()    # Render current simulation state to screen
                      # - Draws walls, doors, and agents
                      # - Updates display
        # --------------------
        # FRAME RATE CONTROL
        # --------------------
        clock.tick(30)  # Maintain 30 FPS (33.3ms per frame)
                        # This regulates simulation speed for consistent visualization

    # Cleanup PyGame resources when simulation ends
    pygame.quit()

if __name__ == "__main__":
    """
    Application entry point when run as a script.
    
    This conditional ensures the main() function is only called when the file
    is executed directly, not when imported as a module.
    """
    main()