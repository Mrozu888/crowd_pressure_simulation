import pygame

from Config2 import CONFIG
from Environment import Environment
from Simulation import Simulation
from Visualization import Visualization

from stats import StatsGeometry, StatsManager, StatsWriter, StatsHUD


def main():
    pygame.init()
    pygame.font.init()

    font = pygame.font.SysFont(None, 24)
    small_font = pygame.font.SysFont(None, 20)

    clock = pygame.time.Clock()

    env = Environment(CONFIG)
    sim = Simulation(env, CONFIG)
    vis = Visualization(env)

    # Stats (CSV + heatmap + live HUD)
    writer = StatsWriter()
    geom = StatsGeometry.from_environment(env)
    stats = StatsManager(geom, writer)
    hud = StatsHUD(font=font, small_font=small_font)

    running = True
    paused = False
    target_fps = 30

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        paused = not paused

                    # HUD toggles
                    elif event.key in (pygame.K_F1, pygame.K_g, pygame.K_h):
                        hud.handle_key(event.key)

                    # Speed control
                    elif event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
                        target_fps = min(300, target_fps + 10)
                        print(f"Prędkość zwiększona: {target_fps} FPS")
                    elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                        target_fps = max(10, target_fps - 10)
                        print(f"Prędkość zmniejszona: {target_fps} FPS")

            if not paused:
                sim.update(on_before_remove=stats.update)

            # Draw scene without flipping; we will overlay HUD and then flip once.
            vis.draw(flip=False)

            # HUD overlays (stats + charts + hotspots)
            hud.draw(vis.screen, stats, vis=vis)

            # FPS label
            fps_text = f"Speed (FPS): {target_fps}"
            if paused:
                fps_text += " [PAUZA]"
            text_surface = font.render(fps_text, True, (0, 0, 0))
            vis.screen.blit(text_surface, (10, 10))

            pygame.display.flip()
            clock.tick(target_fps)

    finally:
        try:
            stats.close()
            print("Stats saved to:", writer.base_dir)
        except Exception:
            pass
        pygame.quit()


if __name__ == "__main__":
    main()