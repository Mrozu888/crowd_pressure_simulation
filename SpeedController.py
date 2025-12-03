# import pygame

# class SpeedController:
#     """
#     Obsługuje przyciski przyspieszania animacji (x1, x2, x3, x4)
#     oraz pozwala na dostosowanie wartości dt w czasie rzeczywistym.
#     """

#     def __init__(self, simulation):
#         self.simulation = simulation
#         self.speed_levels = [1, 2, 3, 4]       # mnożniki prędkości
#         self.current_index = 0                 # domyślnie x1

#     def handle_event(self, event):
#         """
#         Obsługa kliknięć klawiszy 1–4.
#         """

#         if event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_1:
#                 self.current_index = 0
#             elif event.key == pygame.K_2:
#                 self.current_index = 1
#             elif event.key == pygame.K_3:
#                 self.current_index = 2
#             elif event.key == pygame.K_4:
#                 self.current_index = 3

#             # aktualizujemy dt
#             multiplier = self.speed_levels[self.current_index]
#             self.simulation.speed_multiplier = multiplier

#     def draw_ui(self, screen):
#         """
#         Prosty UI z informacją o aktualnej prędkości.
#         """
#         font = pygame.font.SysFont("arial", 20)
#         text = font.render(f"Speed: x{self.simulation.speed_multiplier}", True, (0,0,0))
#         screen.blit(text, (20, 20))
