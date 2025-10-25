import pygame
import numpy as np
import sys
import random
from pygame.locals import *
from SocialForceModel import SocialForceModel
from ParameterExperiment import ParameterExperiment
from Simulation import Simulation

# Główna funkcja
def main():
    # Wybierz typ eksperymentu
    experiment_type = "normal"  # Można zmienić na "dense", "wide_door", "panic"
    
    if experiment_type == "dense":
        model = ParameterExperiment.create_dense_crowd()
    elif experiment_type == "wide_door":
        model = ParameterExperiment.create_wide_door()
    elif experiment_type == "panic":
        model = ParameterExperiment.create_panic_situation()
    else:
        model = SocialForceModel(num_agents=35, room_width=800, room_height=600, door_width=80)
    
    # Uruchom symulację
    simulation = Simulation(model)
    simulation.run()

if __name__ == "__main__":
    main()