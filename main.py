import os
import pygame

from Config import CONFIG
from Environment import Environment
from Simulation import Simulation
from Visualization import Visualization

from stats import StatsGeometry, StatsManager, StatsWriter, RealDataSeries, StatsHUD


def _load_real_data_from_config():
    rd_conf = CONFIG.get("real_data", {}) if isinstance(CONFIG, dict) else {}
    if not rd_conf or not rd_conf.get("enabled", False):
        return None

    csv_path = rd_conf.get("csv_path", "")
    if not csv_path:
        return None
    if not os.path.isfile(csv_path):
        return None

    time_col = rd_conf.get("time_col", "time_s")
    column_map = rd_conf.get(
        "column_map",
        {
            "queue_len": "queue_len",
            "entries_per_min": "entries_per_min",
            "exits_per_min": "exits_per_min",
            "inside": "inside",
            "density_store": "density_store",
        },
    )

    try:
        return RealDataSeries.load_csv(csv_path, time_col=time_col, column_map=column_map)
    except Exception:
        return None


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

    real_data = _load_real_data_from_config()
    hud = StatsHUD(font=font, small_font=small_font, real_data=real_data)

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
                    elif event.key in (pygame.K_F1, pygame.K_g, pygame.K_h, pygame.K_r):
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
            hud.draw(vis.screen, vis, stats, sim.current_time)

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
