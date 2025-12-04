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
    Główna pętla symulacji z kontrolą prędkości.
    """

    # Inicjalizacja PyGame
    pygame.init()

    # Inicjalizacja czcionki do wyświetlania prędkości
    pygame.font.init()
    font = pygame.font.SysFont('Arial', 24)

    clock = pygame.time.Clock()

    # Inicjalizacja komponentów
    env = Environment(CONFIG)
    sim = Simulation(env, CONFIG)

    # NEW: statistics setup
    geom = StatsGeometry()
    writer = StatsCSVWriter(".")
    stats = StatsManager(geom, writer, covid_dist=CONFIG.get("covid_dist", 1.7))
    hud_font = pygame.font.SysFont("consolas", 14)
    hud = StatsHUD(stats, font=hud_font, pos=(10, 40))

    # Visualization now optionally receives stats manager
    vis = Visualization(env, stats)

    running = True
    paused = False

    # Domyślna prędkość (klatki na sekundę)
    # Standardowo 60. Im więcej, tym szybciej symulacja "płynie".
    target_fps = 60

    print("Symulacja uruchomiona.")
    print("Sterowanie:")
    print("  ESC   - Wyjście")
    print("  SPACJA- Pauza")
    print("  + / - - Przyspiesz / Zwolnij")

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                # Pauza
                elif event.key == pygame.K_SPACE:
                    paused = not paused

                # Przyspieszanie (Klawisz '=' to standardowy plus, K_KP_PLUS to numeryczny)
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
                    target_fps += 10
                    if target_fps > 300:
                        target_fps = 300  # Limit max
                    print(f"Prędkość zwiększona: {target_fps} FPS")

                # Zwalnianie
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    target_fps -= 10
                    if target_fps < 10:
                        target_fps = 10  # Limit min
                    print(f"Prędkość zmniejszona: {target_fps} FPS")

        if not paused:
            # Aktualizacja symulacji
            sim.update()

            # NEW: statistics update (dt zgodne z konfiguracją symulacji)
            dt = CONFIG.get("simulation", {}).get("dt", 0.033)
            stats.update(dt, env.agents)

        # Rysowanie sceny (otoczenie + agenci)
        vis.draw()

        # Rysowanie informacji o prędkości na ekranie
        fps_text = f"Speed (FPS): {target_fps}"
        if paused:
            fps_text += " [PAUZA]"

        # Tworzenie napisu (kolor czarny)
        text_surface = font.render(fps_text, True, (0, 0, 0))
        # Wyświetlenie w lewym górnym rogu (10, 10)
        vis.screen.blit(text_surface, (10, 10))

        # NEW: HUD ze statystykami (na tym samym ekranie)
        hud.draw(vis.screen)

        # Konieczne odświeżenie ekranu po dodaniu napisu/HUD
        pygame.display.flip()

        # --------------------
        # 4. KONTROLA CZASU
        # --------------------
        # Tutaj używamy naszej zmiennej target_fps
        clock.tick(target_fps)

    # Zamknięcie plików statystyk
    stats.close()
    pygame.quit()


if __name__ == "__main__":
    main()
