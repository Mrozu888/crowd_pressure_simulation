# path_generation.py
import numpy as np
import random


def generate_shopping_path(zones_config, path_config):
    """
    Generuje kompleksową ścieżkę zakupową dla agenta.
    """
    path = []

    # 1. Punkt startowy
    spawn_zone = zones_config["spawn"]
    start_pos = (np.random.uniform(spawn_zone[0][0], spawn_zone[1][0]),
                 np.random.uniform(spawn_zone[0][1], spawn_zone[1][1]))
    path.append(start_pos)

    # 2. Wejście
    for entry in zones_config["entrance"]:
        path.append(entry)

    # 3. Konfiguracja alejek
    aisle_x_ranges = zones_config["aisles_x_ranges"]
    aisle_y_range = zones_config["aisle_y_range"]
    aisle_top_y = zones_config["aisle_top_y"]
    aisle_bottom_y = zones_config["aisle_bottom_y"]

    # Cel przy kasach
    cashier_zone = zones_config["cashier_area"]
    cashier_pos = (np.random.uniform(cashier_zone[0][0], cashier_zone[1][0]),
                   np.random.uniform(cashier_zone[0][1], cashier_zone[1][1]))
    cashier_pos_np = np.array(cashier_pos)

    # 4. Wybór i sortowanie alejek
    n_aisles = random.randint(path_config["min_aisles"], path_config["max_aisles"])
    chosen_aisle_ranges = random.sample(aisle_x_ranges, min(n_aisles, len(aisle_x_ranges)))

    # Sortowanie (od lewej do prawej), żeby chodzili logicznie
    chosen_aisle_ranges.sort(key=lambda r: r[0])

    # 5. Generowanie punktów dla każdej alejki
    # Używamy enumerate, aby wiedzieć, czy to ostatnia alejka
    for i, x_range in enumerate(chosen_aisle_ranges):
        current_pos_np = np.array(path[-1])

        # A. Punkt docelowy wewnątrz alejki (losowy)
        x_target = np.random.uniform(x_range[0], x_range[1])
        y_target = np.random.uniform(aisle_y_range[0], aisle_y_range[1])
        P_target = (x_target, y_target)
        P_target_np = np.array(P_target)

        # B. Punkty nawigacyjne alejki (góra i dół)
        x_center = (x_range[0] + x_range[1]) / 2.0
        P_top_np = np.array([x_center, aisle_top_y])
        P_bottom_np = np.array([x_center, aisle_bottom_y])

        # --- WYBÓR WEJŚCIA (P_entry) ---
        # Wchodzimy tam, gdzie mamy bliżej z poprzedniej pozycji
        dist_top = np.linalg.norm(current_pos_np - P_top_np)
        dist_bottom = np.linalg.norm(current_pos_np - P_bottom_np)

        if dist_top < dist_bottom:
            P_entry = (P_top_np[0], P_top_np[1])
        else:
            P_entry = (P_bottom_np[0], P_bottom_np[1])

        # --- WYBÓR WYJŚCIA (P_exit) - POPRAWIONA LOGIKA ---

        # Krok 1: Ustal "Następny Cel Strategiczny"
        is_last_aisle = (i == len(chosen_aisle_ranges) - 1)

        if is_last_aisle:
            # Jeśli to ostatnia alejka -> idziemy do kas
            next_goal_np = cashier_pos_np
        else:
            # Jeśli jest kolejna alejka -> idziemy w stronę jej środka
            next_range = chosen_aisle_ranges[i + 1]
            next_x = (next_range[0] + next_range[1]) / 2.0
            # Y bierzemy jako środek sklepu, żeby nie faworyzować góry/dołu,
            # tylko sprawdzić, które wyjście z obecnej alejki jest wygodniejsze.
            # (Albo po prostu Y obecnego celu w alejce, co promuje "przepływ")
            next_y = (aisle_top_y + aisle_bottom_y) / 2.0
            next_goal_np = np.array([next_x, next_y])

        # Krok 2: Oblicz całkowity dystans dla obu opcji wyjścia
        # Opcja A: Jestem w alejce -> idę górą -> idę do następnego celu
        dist_via_top = np.linalg.norm(P_target_np - P_top_np) + \
                       np.linalg.norm(P_top_np - next_goal_np)

        # Opcja B: Jestem w alejce -> idę dołem -> idę do następnego celu
        dist_via_bot = np.linalg.norm(P_target_np - P_bottom_np) + \
                       np.linalg.norm(P_bottom_np - next_goal_np)

        # Krok 3: Wybierz szybszą trasę
        if dist_via_top < dist_via_bot:
            P_exit = (P_top_np[0], P_top_np[1])
        else:
            P_exit = (P_bottom_np[0], P_bottom_np[1])

        # Dodajemy punkty do ścieżki
        path.append(P_entry)
        path.append(P_target)
        path.append(P_exit)

    # 6. Kasy i wyjście
    path.append(cashier_pos)

    # 2. Wejście
    for exit in zones_config["exits"]:
        path.append(exit)

    return path