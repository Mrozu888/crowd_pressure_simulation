import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle, Circle

class SocialForceModel:
    def __init__(self, num_agents=20, room_width=20, room_height=15, door_width=3):
        self.num_agents = num_agents
        self.room_width = room_width
        self.room_height = room_height
        self.door_width = door_width
        self.door_position = room_width / 2  # drzwi na środku prawej ściany
        
        # Parametry modelu
        self.A = 2000  # amplituda siły odpychania
        self.B = 0.08  # zasięg siły odpychania
        self.tau = 0.5  # czas relaksacji
        self.v_desired = 1.5  # pożądana prędkość
        self.dt = 0.05  # krok czasowy
        
        # Inicjalizacja agentów
        self.reset_agents()
    
    def reset_agents(self):
        # Pozycje - losowo w lewej części pomieszczenia
        self.positions = np.zeros((self.num_agents, 2))
        self.positions[:, 0] = np.random.uniform(2, self.room_width/2 - 2, self.num_agents)
        self.positions[:, 1] = np.random.uniform(2, self.room_height - 2, self.num_agents)
        
        # Prędkości - początkowe zerowe
        self.velocities = np.zeros((self.num_agents, 2))
        
        # Cel - drzwi
        self.goals = np.array([[self.room_width, self.room_height/2]] * self.num_agents)
        
        # Promienie agentów
        self.radii = np.random.uniform(0.3, 0.5, self.num_agents)
        
        # Flaga czy agent wyszedł
        self.exited = np.zeros(self.num_agents, dtype=bool)
    
    def social_force(self, i):
        """Oblicza siłę społeczną dla agenta i"""
        total_force = np.zeros(2)
        
        # Siła dążenia do celu
        direction_to_goal = self.goals[i] - self.positions[i]
        distance_to_goal = np.linalg.norm(direction_to_goal)
        
        if distance_to_goal > 0.1:
            desired_direction = direction_to_goal / distance_to_goal
            desired_velocity = self.v_desired * desired_direction
            force_goal = (desired_velocity - self.velocities[i]) / self.tau
            total_force += force_goal
        
        # Siły odpychania od innych agentów
        for j in range(self.num_agents):
            if i != j and not self.exited[j]:
                rij = self.positions[i] - self.positions[j]
                dij = np.linalg.norm(rij)
                
                if dij > 0:
                    nij = rij / dij
                    # Odległość między powierzchniami
                    d_eff = max(dij - self.radii[i] - self.radii[j], 0.01)
                    
                    # Siła odpychania
                    f_rep = self.A * np.exp(-d_eff / self.B) * nij
                    total_force += f_rep
        
        # Siły odpychania od ścian
        total_force += self.wall_force(i)
        
        return total_force
    
    def wall_force(self, i):
        """Oblicza siłę odpychania od ścian"""
        wall_force = np.zeros(2)
        pos = self.positions[i]
        r = self.radii[i]
        
        # Lewa ściana
        if pos[0] - r < 0:
            d = r - pos[0]
            wall_force[0] += self.A * np.exp(-d / self.B)
        
        # Prawa ściana (z wyjątkiem drzwi)
        if pos[0] + r > self.room_width:
            d = pos[0] + r - self.room_width
            # Sprawdź czy agent jest na wysokości drzwi
            door_bottom = self.room_height/2 - self.door_width/2
            door_top = self.room_height/2 + self.door_width/2
            
            if not (door_bottom <= pos[1] <= door_top):
                wall_force[0] -= self.A * np.exp(-d / self.B)
        
        # Dolna ściana
        if pos[1] - r < 0:
            d = r - pos[1]
            wall_force[1] += self.A * np.exp(-d / self.B)
        
        # Górna ściana
        if pos[1] + r > self.room_height:
            d = pos[1] + r - self.room_height
            wall_force[1] -= self.A * np.exp(-d / self.B)
        
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
                if speed > 2 * self.v_desired:
                    self.velocities[i] = 2 * self.v_desired * self.velocities[i] / speed
                
                # Aktualizuj pozycję
                self.positions[i] += self.velocities[i] * self.dt
                
                # Sprawdź czy agent wyszedł przez drzwi
                if (self.positions[i][0] > self.room_width and 
                    abs(self.positions[i][1] - self.room_height/2) < self.door_width/2):
                    self.exited[i] = True
                    # Przenieś agenta poza ekran
                    self.positions[i] = [self.room_width + 5, self.room_height/2]
    
    def get_exited_count(self):
        """Zwraca liczbę agentów, którzy wyszli"""
        return np.sum(self.exited)

class Simulation:
    def __init__(self, model):
        self.model = model
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.setup_plot()
        
    def setup_plot(self):
        self.ax.set_xlim(-1, self.model.room_width + 2)
        self.ax.set_ylim(-1, self.model.room_height + 1)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_title('Symulacja Social Force Model - Ludzie wchodzący do pomieszczenia')
        
        # Narysuj pomieszczenie
        room = Rectangle((0, 0), self.model.room_width, self.model.room_height, 
                        fill=False, linewidth=2, color='black')
        self.ax.add_patch(room)
        
        # Narysuj drzwi
        door_bottom = self.model.room_height/2 - self.model.door_width/2
        door = Rectangle((self.model.room_width, door_bottom), 0.2, self.model.door_width,
                        fill=True, color='brown', alpha=0.7)
        self.ax.add_patch(door)
        
        # Inicjalizacja agentów
        self.agents = []
        for i in range(self.model.num_agents):
            color = 'red' if i % 2 == 0 else 'blue'
            agent = Circle((0, 0), radius=self.model.radii[i], color=color, alpha=0.7)
            self.agents.append(agent)
            self.ax.add_patch(agent)
        
        # Tekst z informacjami
        self.info_text = self.ax.text(0.02, 0.98, '', transform=self.ax.transAxes, 
                                     verticalalignment='top', fontsize=10,
                                     bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    def update_plot(self, frame):
        # Aktualizuj model
        self.model.update()
        
        # Aktualizuj pozycje agentów
        for i, agent in enumerate(self.agents):
            if not self.model.exited[i]:
                agent.center = self.model.positions[i]
                agent.set_alpha(0.7)
            else:
                agent.set_alpha(0.2)  # Przyciemnij agentów, którzy wyszli
        
        # Aktualizuj informacje
        exited_count = self.model.get_exited_count()
        self.info_text.set_text(f'Czas: {frame * self.model.dt:.1f}s\n'
                               f'Wyszło: {exited_count}/{self.model.num_agents}\n'
                               f'Pozostało: {self.model.num_agents - exited_count}')
        
        return self.agents + [self.info_text]
    
    def run(self, frames=1000):
        anim = animation.FuncAnimation(self.fig, self.update_plot, frames=frames,
                                     interval=50, blit=True, repeat=True)
        plt.show()
        return anim

# Przykład użycia
if __name__ == "__main__":
    # Utwórz model
    model = SocialForceModel(num_agents=15, room_width=25, room_height=18, door_width=4)
    
    # Uruchom symulację
    sim = Simulation(model)
    anim = sim.run(frames=500)
    
    # Możesz też zapisać animację (wymaga ffmpeg)
    # anim.save('social_force_simulation.mp4', writer='ffmpeg', fps=20)