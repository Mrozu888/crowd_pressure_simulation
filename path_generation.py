import numpy as np
import random


def generate_shopping_path(zones_config, path_config=None):
    """
    Prosta generacja ścieżki: Spawn +/- 0.5m -> Wejście -> Zakupy -> Kasa.
    """
    path = []

    # --- 1. PROSTY SPAWN (X +/- 0.5, Y +/- 0.5) ---
    base_spawn = zones_config["spawn_point"]


    # Prosta matematyka: bierzemy punkt i przesuwamy go losowo
    rand_x = base_spawn[0] + np.random.uniform(-1, 1)
    rand_y = base_spawn[1] + np.random.uniform(-1, 1)

    path.append((rand_x, rand_y))

    # --- 2. Wejście (Entrance) ---
    # Muszą przejść przez drzwi
    entrances = zones_config.get("entrance_points", [])

    # Obsługa listy punktów wejściowych
    if isinstance(entrances, list):
        for entry in entrances:
            path.append(entry)
    elif isinstance(entrances, tuple):
        path.append(entrances)

    # --- 3. Punkty Zakupowe (POI) ---
    possible_points = zones_config["points_of_interest"]
    selected_targets = []

    for poi in possible_points:
        if random.random() < poi["prob"]:
            # Też prosty losowy rozrzut przy półce
            px = poi["pos"][0] + np.random.uniform(-0.3, 0.3)
            py = poi["pos"][1] + np.random.uniform(-0.3, 0.3)
            selected_targets.append((px, py))

    # --- 4. Sortowanie (żeby chodzili po kolei) ---
    selected_targets.sort(key=lambda p: p[0])
    path.extend(selected_targets)

    # --- 5. Kasa i Wyjście ---
    cashier = zones_config["cashier_point"]
    cx = cashier[0] + np.random.uniform(-0.4, 0.4)
    cy = cashier[1] + np.random.uniform(-0.4, 0.4)
    path.append((cx, cy))

    path.append(zones_config["exit_point"])

    return path