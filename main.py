import pygame
from Config import CONFIG
from Environment import Environment
from Simulation import Simulation
from Visualization import Visualization

def main():
    pygame.init()
    clock = pygame.time.Clock()

    env = Environment(CONFIG)
    sim = Simulation(env, CONFIG)
    vis = Visualization(env)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        sim.update()
        vis.draw()

        clock.tick(30)  # FPS

    pygame.quit()

if __name__ == "__main__":
    main()
