import numpy as np
import random


def generate_shopping_path(zones_config, path_config=None):
    """
    Generuje ścieżkę słownikową: [{'pos': (x,y), 'wait': czas}, ...]
    """
    path = []

    # Funkcja pomocnicza
    def make_point(x, y, wait=0.0):
        return {'pos': (x, y), 'wait': wait}

    # --- 1. PROSTY SPAWN ---
    base_spawn = zones_config["spawn_point"]
    rand_x = base_spawn[0] + np.random.uniform(-1, 1)
    rand_y = base_spawn[1] + np.random.uniform(-1, 1)

    # Zabezpieczenie mapy (opcjonalne, zależne od configu)
    # rand_x = max(0.1, rand_x) ...

    path.append(make_point(rand_x, rand_y, 0.0))

    # --- 2. Wejście ---
    entrances = zones_config.get("entrance_points", [])
    if isinstance(entrances, list):
        for entry in entrances:
            path.append(make_point(entry[0], entry[1], 0.0))
    elif isinstance(entrances, tuple):
        path.append(make_point(entrances[0], entrances[1], 0.0))

    # --- 3. Punkty Zakupowe (POI) z CZASEM ---
    possible_points = zones_config["points_of_interest"]
    selected_targets = []

    for poi in possible_points:
        if random.random() < poi["prob"]:
            px = poi["pos"][0] + np.random.uniform(-0.3, 0.3)
            py = poi["pos"][1] + np.random.uniform(-0.3, 0.3)

            # --- LOSOWANIE CZASU CZEKANIA ---
            # Np. 2 do 5 sekund stania przy półce
            wait_time = random.uniform(2.0, 5.0)

            selected_targets.append(make_point(px, py, wait_time))

    # --- 4. Sortowanie ---
    selected_targets.sort(key=lambda p: p['pos'][0])  # Sortujemy po X z 'pos'
    path.extend(selected_targets)

    # --- 5. Kasa (z czasem) ---
    cashier = zones_config["cashier_point"]
    cx = cashier[0] + np.random.uniform(-0.4, 0.4)
    cy = cashier[1] + np.random.uniform(-0.4, 0.4)

    # Przy kasie dłużej (3-7s)
    cashier_wait = random.uniform(3.0, 7.0)
    path.append(make_point(cx, cy, cashier_wait))

    # --- 6. Wyjście ---
    ex = zones_config["exit_point"]
    path.append(make_point(ex[0], ex[1], 0.0))

    return path