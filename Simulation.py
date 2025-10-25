import pygame
import numpy as np
import sys
import random
from pygame.locals import *

class Simulation:
    def __init__(self, model):
        self.model = model
        self.screen_width = model.room_width
        self.screen_height = model.room_height
        
        # Inicjalizacja Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Social Force Model - Symulacja Evakuacji')
        
        # Czcionka dla tekstu
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Clock do kontroli FPS
        self.clock = pygame.time.Clock()
        
        # Kolory
        self.BACKGROUND = (240, 240, 240)
        self.WALL_COLOR = (50, 50, 50)
        self.DOOR_COLOR = (139, 69, 19)  # brązowy
        self.TEXT_COLOR = (0, 0, 0)
        self.STATS_BG = (255, 255, 255, 200)
    
    def draw_room(self):
        """Rysuje pomieszczenie i drzwi"""
        # Tło
        self.screen.fill(self.BACKGROUND)
        
        # Kontur pomieszczenia
        pygame.draw.rect(self.screen, self.WALL_COLOR, (0, 0, self.screen_width, self.screen_height), 4)
        
        # Drzwi (przerwa w prawej ścianie)
        door_top = self.model.door_position - self.model.door_width/2
        pygame.draw.line(self.screen, self.WALL_COLOR, 
                        (self.screen_width, 0), (self.screen_width, door_top), 4)
        pygame.draw.line(self.screen, self.WALL_COLOR,
                        (self.screen_width, door_top + self.model.door_width),
                        (self.screen_width, self.screen_height), 4)
        
        # Oznaczenie drzwi
        pygame.draw.rect(self.screen, self.DOOR_COLOR,
                        (self.screen_width - 20, door_top, 20, self.model.door_width))
    
    def draw_agents(self):
        """Rysuje wszystkich agentów"""
        for i in range(self.model.num_agents):
            if not self.model.exited[i]:
                pos = self.model.positions[i]
                radius = self.model.radii[i]
                color = self.model.colors[i]
                
                # Rysuj agenta
                pygame.draw.circle(self.screen, color, (int(pos[0]), int(pos[1])), int(radius))
                
                # Rysuj kierunek ruchu (mała kropka z przodu)
                if np.linalg.norm(self.model.velocities[i]) > 0.1:
                    direction = self.model.velocities[i] / np.linalg.norm(self.model.velocities[i])
                    front_pos = pos + direction * radius * 0.7
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                    (int(front_pos[0]), int(front_pos[1])), int(radius * 0.3))
    
    def draw_stats(self):
        """Rysuje statystyki symulacji"""
        exited_count = self.model.get_exited_count()
        remaining_count = self.model.num_agents - exited_count
        
        # Tło dla statystyk
        stats_rect = pygame.Rect(10, 10, 250, 80)
        pygame.draw.rect(self.screen, self.STATS_BG, stats_rect)
        pygame.draw.rect(self.screen, self.TEXT_COLOR, stats_rect, 1)
        
        # Tekst statystyk
        stats_text = [
            f"Wyszło: {exited_count}/{self.model.num_agents}",
            f"Pozostało: {remaining_count}",
            f"Procent: {exited_count/self.model.num_agents*100:.1f}%"
        ]
        
        for i, text in enumerate(stats_text):
            text_surface = self.small_font.render(text, True, self.TEXT_COLOR)
            self.screen.blit(text_surface, (20, 20 + i * 20))
    
    def draw_instructions(self):
        """Rysuje instrukcje sterowania"""
        instructions = [
            "SPACJA - restart symulacji",
            "R - reset pozycji agentów",
            "ESC - wyjście"
        ]
        
        for i, text in enumerate(instructions):
            text_surface = self.small_font.render(text, True, self.TEXT_COLOR)
            self.screen.blit(text_surface, (10, self.screen_height - 80 + i * 20))
    
    def handle_events(self):
        """Obsługa zdarzeń Pygame"""
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return False
                elif event.key == K_SPACE:
                    self.model.reset_agents()
                elif event.key == K_r:
                    self.model.reset_agents()
        return True
    
    def run(self):
        """Główna pętla symulacji"""
        running = True
        
        while running:
            running = self.handle_events()
            
            # Aktualizuj model
            self.model.update()
            
            # Rysowanie
            self.draw_room()
            self.draw_agents()
            self.draw_stats()
            self.draw_instructions()
            
            # Aktualizacja ekranu
            pygame.display.flip()
            
            # Kontrola FPS
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()