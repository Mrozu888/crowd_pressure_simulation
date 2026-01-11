import numpy as np
import random


def generate_shopping_path(zones_config, path_config=None):
    """
    Generuje ścieżkę słownikową: [{'pos': (x,y), 'wait': czas}, ...]
    """
    path = []

    # Helper function - inline is faster usually, but func is cleaner
    # Zmieniamy na tuple zamiast słownika od razu jeśli to możliwe,
    # ale zachowujemy format słownika zgodnie z prośbą o brak zmian w logice.

    # 1. Spawn Point
    base_spawn = zones_config["spawn_point"]
    # Używamy random.uniform zamiast np.random.uniform dla skalarnych wartości (jest szybsze w czystym Pythonie)
    rand_x = base_spawn[0] + random.uniform(-1, 1)
    rand_y = base_spawn[1] + random.uniform(-1, 1)

    path.append({'pos': (rand_x, rand_y), 'wait': 0.0})

    # 2. Wejście
    entrances = zones_config.get("entrance_points", [])
    if isinstance(entrances, list):
        for entry in entrances:
            path.append({'pos': tuple(entry), 'wait': 0.0})
    elif isinstance(entrances, tuple):
        path.append({'pos': entrances, 'wait': 0.0})

    # 3. Punkty Zakupowe (POI)
    possible_points = zones_config["points_of_interest"]
    selected_targets = []

    for poi in possible_points:
        # Szybki check
        if random.random() < poi["prob"]:
            pos = poi["pos"]
            px = pos[0] + random.uniform(-0.3, 0.3)
            py = pos[1] + random.uniform(-0.3, 0.3)

            wait_time = random.uniform(2.0, 5.0)
            selected_targets.append({'pos': (px, py), 'wait': wait_time})

    # 4. Sortowanie (kluczowa logika zachowana)
    # Sortujemy tylko jeśli mamy więcej niż 1 punkt, oszczędza wywołanie
    if len(selected_targets) > 1:
        selected_targets.sort(key=lambda p: p['pos'][0])

    path.extend(selected_targets)

    return path