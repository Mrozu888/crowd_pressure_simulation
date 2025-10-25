import pygame
import numpy as np
import sys
import random

class SocialForceModel:
    def __init__(self, num_agents=30, room_width=800, room_height=600, door_width=80):
        self.num_agents = num_agents
        self.room_width = room_width
        self.room_height = room_height
        self.door_width = door_width
        self.door_position = room_height // 2  # drzwi na środku prawej ściany
        
        # Parametry modelu
        self.A = 2000  # amplituda siły odpychania
        self.B = 8    # zasięg siły odpychania
        self.tau = 0.5  # czas relaksacji
        self.v_desired = 2.0  # pożądana prędkość
        self.dt = 0.1  # krok czasowy
        
        # Inicjalizacja agentów
        self.reset_agents()
    
    def reset_agents(self):
        # Pozycje - losowo w lewej części pomieszczenia
        self.positions = np.zeros((self.num_agents, 2))
        self.positions[:, 0] = np.random.uniform(50, self.room_width/2 - 50, self.num_agents)
        self.positions[:, 1] = np.random.uniform(50, self.room_height - 50, self.num_agents)
        
        # Prędkości - początkowe zerowe
        self.velocities = np.zeros((self.num_agents, 2))
        
        # Cel - drzwi
        self.goals = np.array([[self.room_width, self.room_height/2]] * self.num_agents)
        
        # Promienie agentów
        self.radii = np.random.uniform(8, 15, self.num_agents)
        
        # Masy agentów (do obliczeń fizycznych)
        self.masses = np.ones(self.num_agents)
        
        # Flaga czy agent wyszedł
        self.exited = np.zeros(self.num_agents, dtype=bool)
        
        # Kolory agentów
        self.colors = []
        for i in range(self.num_agents):
            self.colors.append((random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))
    
    def social_force(self, i):
        """Oblicza siłę społeczną dla agenta i"""
        if self.exited[i]:
            return np.zeros(2)
            
        total_force = np.zeros(2)
        
        # Siła dążenia do celu
        direction_to_goal = self.goals[i] - self.positions[i]
        distance_to_goal = np.linalg.norm(direction_to_goal)
        
        if distance_to_goal > 5:
            desired_direction = direction_to_goal / distance_to_goal
            desired_velocity = self.v_desired * desired_direction
            force_goal = (desired_velocity - self.velocities[i]) / self.tau
            total_force += force_goal
        
        # Siły odpychania od innych agentów
        for j in range(self.num_agents):
            if i != j and not self.exited[j]:
                rij = self.positions[i] - self.positions[j]
                dij = np.linalg.norm(rij)
                
                if dij > 0 and dij < 100:  # Ograniczenie zasięgu oddziaływania
                    nij = rij / dij
                    # Odległość między powierzchniami
                    d_eff = max(dij - self.radii[i] - self.radii[j], 0.1)
                    
                    # Siła odpychania
                    f_rep = self.A * np.exp(-d_eff / self.B) * nij
                    total_force += f_rep
        
        # Siły odpychania od ścian
        total_force += self.wall_force(i)
        
        return total_force
    
    def wall_force(self, i):
        """Oblicza siłę odpychania od ścian"""
        if self.exited[i]:
            return np.zeros(2)
            
        wall_force = np.zeros(2)
        pos = self.positions[i]
        r = self.radii[i]
        
        # Lewa ściana
        if pos[0] - r < 0:
            d = r - pos[0]
            wall_force[0] += self.A * 0.1 * np.exp(-d / self.B)
        
        # Prawa ściana (z wyjątkiem drzwi)
        if pos[0] + r > self.room_width:
            d = pos[0] + r - self.room_width
            door_bottom = self.door_position - self.door_width/2
            door_top = self.door_position + self.door_width/2
            
            if not (door_bottom <= pos[1] <= door_top):
                wall_force[0] -= self.A * 0.1 * np.exp(-d / self.B)
        
        # Dolna ściana
        if pos[1] - r < 0:
            d = r - pos[1]
            wall_force[1] += self.A * 0.1 * np.exp(-d / self.B)
        
        # Górna ściana
        if pos[1] + r > self.room_height:
            d = pos[1] + r - self.room_height
            wall_force[1] -= self.A * 0.1 * np.exp(-d / self.B)
        
        return wall_force
    
    def update(self):
        """Aktualizuje pozycje i prędkości agentów"""
        for i in range(self.num_agents):
            if not self.exited[i]:
                # Oblicz siłę
                force = self.social_force(i)
                
                # Aktualizuj prędkość (z ograniczeniem)
                self.velocities[i] += force * self.dt
                speed = np.linalg.norm(self.velocities[i])
                max_speed = 3.0
                if speed > max_speed:
                    self.velocities[i] = max_speed * self.velocities[i] / speed
                
                # Aktualizuj pozycję
                self.positions[i] += self.velocities[i] * self.dt
                
                # Sprawdź czy agent wyszedł przez drzwi
                door_bottom = self.door_position - self.door_width/2
                door_top = self.door_position + self.door_width/2
                
                if (self.positions[i][0] > self.room_width - 10 and 
                    door_bottom <= self.positions[i][1] <= door_top):
                    self.exited[i] = True
                    # Przenieś agenta poza ekran
                    self.positions[i] = [self.room_width + 100, self.door_position]
    
    def get_exited_count(self):
        """Zwraca liczbę agentów, którzy wyszli"""
        return np.sum(self.exited)