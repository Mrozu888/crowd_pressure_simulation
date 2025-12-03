import pygame
from Config import CONFIG
from Environment import Environment
from Simulation import Simulation
from Visualization import Visualization

# NEW: statistics imports
from stats.geometry import StatsGeometry
from stats.manager import StatsManager
from stats.writer import StatsCSVWriter
from stats.hud import StatsHUD


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

    # NEW: statistics setup
    geom = StatsGeometry()
    writer = StatsCSVWriter(".")
    stats = StatsManager(geom, writer, covid_dist=CONFIG.get("covid_dist", 1.7))
    hud_font = pygame.font.SysFont("consolas", 14)
    hud = StatsHUD(stats, font=hud_font, pos=(10, 10))

    # NOTE: pass 'stats' into Visualization so it can color agents by crowding
    vis = Visualization(env, stats)       # Visual rendering system

    
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

        # NEW: statistics update.
        dt = CONFIG.get("simulation", {}).get("dt", 0.033)
        stats.update(dt, env.agents)

        # --------------------
        # RENDERING PHASE
        # --------------------
        vis.draw()    # Render current simulation state to screen
                      # - Draws walls, doors, and agents
                      # - Updates display

        # NEW: HUD overlay (draw on the same screen)
        try:
            surface = vis.screen
            hud.draw(surface)
            pygame.display.flip()
        except AttributeError:
            # If Visualization already calls display.flip() internally and does
            # not expose 'screen', integrate HUD drawing inside Visualization.
            pass

        # --------------------
        # FRAME RATE CONTROL
        # --------------------
        clock.tick(30)  # Maintain 30 FPS (33.3ms per frame)
                        # This regulates simulation speed for consistent visualization

    # Cleanup PyGame resources when simulation ends
    stats.close()
    pygame.quit()

if __name__ == "__main__":
    """
    Application entry point when run as a script.
    
    This conditional ensures the main() function is only called when the file
    is executed directly, not when imported as a module.
    """
    main()
