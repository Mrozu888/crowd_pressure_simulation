import pygame

class Visualization:
    def __init__(self, env):
        self.env = env
        self.scale = env.scale
        self.screen = pygame.display.set_mode(
            (int(env.width * self.scale), int(env.height * self.scale))
        )
        pygame.display.set_caption("Symulacja Social Force - Sklep")

    def draw(self):
        self.screen.fill((240, 240, 240))

        # Rysuj ściany
        for (p1, p2) in self.env.walls:
            x1, y1 = int(p1[0] * self.scale), int(p1[1] * self.scale)
            x2, y2 = int(p2[0] * self.scale), int(p2[1] * self.scale)
            pygame.draw.line(self.screen, (0, 0, 0), (x1, y1), (x2, y2), 4)

        # Rysuj drzwi
        door = self.env.door
        pygame.draw.line(
            self.screen,
            (0, 200, 0),
            (int(door["x"] * self.scale), int(door["y_min"] * self.scale)),
            (int(door["x"] * self.scale), int(door["y_max"] * self.scale)),
            4,
        )

        # Rysuj agentów
        for a in self.env.agents:
            if not a.active:
                continue
            x, y = int(a.position[0] * self.scale), int(a.position[1] * self.scale)
            pygame.draw.circle(self.screen, (50, 100, 255), (x, y), int(a.radius * self.scale))

        pygame.display.flip()
