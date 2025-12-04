import numpy as np
import random


def generate_shopping_path(zones_config, path_config=None):
    """
    Generuje ścieżkę słownikową: [{'pos': (x,y), 'wait': czas}, ...]
    """
    path = []

    def make_point(x, y, wait=0.0):
        return {'pos': (x, y), 'wait': wait}

    # PROSTY SPAWN 
    base_spawn = zones_config["spawn_point"]
    rand_x = base_spawn[0] + np.random.uniform(-1, 1)
    rand_y = base_spawn[1] + np.random.uniform(-1, 1)

    path.append(make_point(rand_x, rand_y, 0.0))

    #  Wejście 
    entrances = zones_config.get("entrance_points", [])
    if isinstance(entrances, list):
        for entry in entrances:
            path.append(make_point(entry[0], entry[1], 0.0))
    elif isinstance(entrances, tuple):
        path.append(make_point(entrances[0], entrances[1], 0.0))

    # Punkty Zakupowe (POI) z CZASEM 
    possible_points = zones_config["points_of_interest"]
    selected_targets = []

    for poi in possible_points:
        if random.random() < poi["prob"]:
            px = poi["pos"][0] + np.random.uniform(-0.3, 0.3)
            py = poi["pos"][1] + np.random.uniform(-0.3, 0.3)

            #  LOSOWANIE CZASU CZEKANIA 
            # Np. 2 do 5 sekund stania przy półce
            wait_time = random.uniform(2.0, 5.0)

            selected_targets.append(make_point(px, py, wait_time))

    #  Sortowanie 
    selected_targets.sort(key=lambda p: p['pos'][0]) 
    path.extend(selected_targets)


    return path