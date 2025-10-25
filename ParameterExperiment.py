import pygame
import numpy as np
import sys
import random

class ParameterExperiment:
    @staticmethod
    def create_dense_crowd():
        """Tworzy symulację z gęstym tłumem"""
        return SocialForceModel(num_agents=50, room_width=800, room_height=600, door_width=60)
    
    @staticmethod
    def create_wide_door():
        """Tworzy symulację z szerokimi drzwiami"""
        return SocialForceModel(num_agents=30, room_width=800, room_height=600, door_width=150)
    
    @staticmethod
    def create_panic_situation():
        """Tworzy symulację sytuacji paniki (większe prędkości)"""
        model = SocialForceModel(num_agents=40, room_width=800, room_height=600, door_width=80)
        model.v_desired = 3.0
        model.A = 3000  # Silniejsze odpychanie
        return model