CONFIG = {
    "dt": 0.05,
    "steps": 10000,

    "environment": {
        "scale": 40,
        "width": 20,
        "height": 15,
        "walls": [
            ((0, 0), (20, 0)),
            ((0, 0), (0, 13)),
            ((0, 14.5), (0, 16.5)),
            ((20, 0), (20, 15)),
            ((0, 15), (20, 15)),
            ((0, 12.5), (1.25, 12.5)),
            ((2.5, 12.5), (4.5, 12.5)),
            ((4.5, 12.5), (4.5, 13.5)),
            ((4.5, 15), (4.5, 14.5)),
        ],
        "doors": [
            ((0, 13), (0, 14.5)),
        ],
        # Twoje półki (bez zmian)
        "shelves": [
            ((14.75, 12), (14.75, 14.85)),
            ((15, 12), (15, 14.85)),
            ((14.75, 14.85), (15, 14.85)),
            ((14.75, 12), (15, 12)),
            ((15, 14.6), (16, 14.6)),
            ((15, 14.85), (16, 14.85)),
            ((16, 14.85), (16, 12)),
            ((16.25, 14.85), (16.25, 12)),
            ((16, 12), (16.25, 12)),
            ((16, 14.85), (16.25, 14.85)),
            ((0.5, 0), (0.5, 12)),
            ((0, 12), (0.5, 12)),
            ((0.5, 0.5), (19, 0.5)),
            ((19, 0), (19, 12)),
            ((2.25, 11), (2.25, 2)),
            ((3.25, 11), (3.25, 2)),
            ((2.25, 11), (3.25, 11)),
            ((2.25, 2), (3.25, 2)),
            ((4.25, 11), (4.25, 6.5)),
            ((4.25, 11), (4.75, 11)),
            ((4.75, 11), (4.75, 6.5)),
            ((4.25, 6.5), (4.75, 6.5)),
            ((4.25, 5.5), (4.25, 2)),
            ((4.25, 2), (4.75, 2)),
            ((4.75, 2), (4.75, 5.5)),
            ((4.25, 5.5), (4.75, 5.5)),
            ((6.25, 11), (6.25, 2)),
            ((6.75, 11), (6.75, 2)),
            ((6.25, 11), (6.75, 11)),
            ((6.25, 2), (6.75, 2)),
            ((8.25, 11), (8.25, 2)),
            ((8.75, 11), (8.75, 2)),
            ((8.25, 11), (8.75, 11)),
            ((8.25, 2), (8.75, 2)),
            ((10.25, 11), (10.25, 2)),
            ((10.75, 11), (10.75, 2)),
            ((10.25, 11), (10.75, 11)),
            ((10.25, 2), (10.75, 2)),
            ((12.25, 11), (12.25, 2)),
            ((12.75, 11), (12.75, 2)),
            ((12.25, 11), (12.75, 11)),
            ((12.25, 2), (12.75, 2)),
            ((14.25, 11), (14.25, 2)),
            ((14.75, 11), (14.75, 2)),
            ((14.25, 11), (14.75, 11)),
            ((14.25, 2), (14.75, 2)),
            ((16.25, 11), (16.25, 2)),
            ((17.25, 11), (17.25, 2)),
            ((16.25, 11), (17.25, 11)),
            ((16.25, 2), (17.25, 2)),
            ((16, 12), (20, 12)),
        ],
        "pallets": [],
         "cash_registers": [
        {"pos": (5.5, 12), "size": (0.6, 1.5)},
        {"pos": (7, 12), "size": (0.6, 1.5)},
        {"pos": (8.5, 12), "size": (0.6, 1.5)},
        {"pos": (9.25, 12.25), "size": (0.6, 0.6)},
        {"pos": (9.25, 13), "size": (0.6, 0.6)},
        #{"pos": (9.75, 14.35), "size": (0.6, 0.6)},
        #{"pos": (10.75, 14.35), "size": (0.6, 0.6)},
        #{"pos": (12.5, 14.35), "size": (0.6, 0.6)},
        {"pos": (11.25, 12.25), "size": (0.6, 0.6)},
        {"pos": (11.25, 13), "size": (0.6, 0.6)},
        {"pos": (12, 12.25), "size": (0.6, 0.6)},
        {"pos": (12, 13), "size": (0.6, 0.6)},
        {"pos": (14, 12), "size": (0.6, 0.6)},
        {"pos": (14, 12.75), "size": (0.6, 0.6)},
        {"pos": (14, 13.5), "size": (0.6, 0.6)},
        {"pos": (14, 14.25), "size": (0.6, 0.6)},
    ],
        "cash_payment": [
            # (5.3, 13),
            # (6.8, 13),
            # (8.3, 13),
            # # ###
            # (10, 12.75),
            # (10, 13.4),
            # (11.1, 12.75),
            # (11.1, 13.4),
            # ###
            #(10.1, 14.25),
            #(11, 14.25),
            # ###
            #(12.75, 12.7),
            #(12.75, 13.4),
            ###
            (13.85, 12.35),
            (13.85, 13.1),
            #(13.85, 13.8),
            #(13.85, 14.6),
        ],


    },

    "sfm": {
        "A": 2.0,
        "B": 0.8,
        "A_w": 10.0,
        "B_w": 0.1,
        "desired_speed": 1.3,
        "tau": 0.5,
    },

    "agent_generation": {
        "spawn_rate": 0.35,
        "n_agents": 20,
        "max_spawn_time": 30.0,

        # Stałe punkty infrastruktury
        "spawn_point": (-1.5, 14.0),     # Punkt startu poza sklepem
        "entrance_points": [(1.7, 12.5)],   # Punkt zaraz po wejściu
        #"cashier_point": (13.5, 13.5),   # Punkt przy kasie
        #"exit_point": (10, 14.0),       # Punkt wyjścia
        "exit_sequence": [
            (4.5, 14.0),
            (0.0, 14.0)
        ],
        # Lista punktów zakupowych do wylosowania
        # "pos": (x, y) - gdzie agent ma podejść
        # "prob": 0.0-1.0 - szansa, że agent wybierze ten punkt
        "points_of_interest": [
            # --- ALEJA 1 (X ≈ 1.5) ---
            {"name": "Aleja1_Północ", "pos": (1.5, 10.0), "prob": 0.2},
            {"name": "Aleja1_Środek", "pos": (1.5, 6.0), "prob": 0.2},
            {"name": "Aleja1_Południe", "pos": (1.5, 3.0), "prob": 0.2},
            {"name": "Aleja1_Południe", "pos": (1.5, 9.0), "prob": 0.2},

            # --- ALEJA 2 (X ≈ 3.75) ---
            {"name": "Aleja2_Północ", "pos": (3.75, 10.0), "prob": 0.15},
            {"name": "Aleja2_Środek", "pos": (3.75, 6.0), "prob": 0.1},
            {"name": "Aleja2_Południe", "pos": (3.75, 3.0), "prob": 0.2},

            # --- ALEJA 3 (X ≈ 5.5) ---
            {"name": "Aleja3_Północ", "pos": (5.5, 10.0), "prob": 0.3},
            {"name": "Aleja3_Środek", "pos": (5.5, 8.0), "prob": 0.3},
            {"name": "Aleja3_Południe", "pos": (5.5, 4.0), "prob": 0.3},

            # --- ALEJA 4 (X ≈ 7.5) ---
            {"name": "Aleja4_Północ", "pos": (7.5, 10.0), "prob": 0.35},
            {"name": "Aleja4_Środek", "pos": (7.5, 5.0), "prob": 0.35},
            {"name": "Aleja4_Południe", "pos": (7.5, 3.0), "prob": 0.35},

            # --- ALEJA 5 (X ≈ 9.5) ---
            {"name": "Aleja5_Północ", "pos": (9.5, 10.0), "prob": 0.2},
            {"name": "Aleja5_Środek", "pos": (9.5, 6.0), "prob": 0.3},
            {"name": "Aleja5_Południe", "pos": (9.5, 3.0), "prob": 0.4},

            # --- ALEJA 6 (X ≈ 11.5) ---
            {"name": "Aleja6_Północ", "pos": (11.5, 10.0), "prob": 0.35},
            {"name": "Aleja6_Środek", "pos": (11.5, 6.0), "prob": 0.4},
            {"name": "Aleja6_Południe", "pos": (11.5, 3.0), "prob": 0.1},

            # --- ALEJA 7 (X ≈ 13.5) ---
            {"name": "Aleja7_Północ", "pos": (13.5, 10.0), "prob": 0.35},
            {"name": "Aleja7_Środek", "pos": (13.5, 6.0), "prob": 0.35},
            {"name": "Aleja7_Południe", "pos": (13.5, 3.0), "prob": 0.35},

            # --- ALEJA 8 (X ≈ 15.5) ---
            {"name": "Aleja8_Północ", "pos": (15.5, 10.0), "prob": 0.3},
            {"name": "Aleja8_Środek", "pos": (15.5, 6.0), "prob": 0.5},
            {"name": "Aleja8_Południe", "pos": (15.5, 3.0), "prob": 0.3},

            # --- ALEJA 9 (X ≈ 18) ---
            {"name": "Aleja9_Północ", "pos": (18.0, 10.0), "prob": 0.4},
            {"name": "Aleja9_Środek", "pos": (18.0, 6.0), "prob": 0.25},
            {"name": "Aleja9_Południe", "pos": (18.0, 8.0), "prob": 0.3},
            {"name": "Aleja9_Południe", "pos": (18.0, 4.5), "prob": 0.25},
            {"name": "Aleja9_Południe", "pos": (18.0, 11.0), "prob": 0.5},

            # --- ŚCIANA POŁUDNIOWA (PRZY MIĘSIE) ---
            {"name": "Mięso1", "pos": (3.0, 1.25), "prob": 0.2},
            {"name": "Mięso2", "pos": (6.0, 1.25), "prob": 0.2},
            {"name": "Mięso3", "pos": (9.0, 1.25), "prob": 0.2},
            {"name": "Mięso4", "pos": (12.0, 1.25), "prob": 0.2},
            {"name": "Mięso5", "pos": (15.0, 1.25), "prob": 0.2},
            {"name": "Mięso6", "pos": (18.0, 1.25), "prob": 0.2},


            {"name": "Mięso6", "pos": (15.0, 13.25), "prob": 0.7},
        ]
    }
,

    # Optional: real-world measurements for live comparison in HUD.
    # Enable and provide a CSV with at least: time_s, entries_per_min, exits_per_min, queue_len
    "real_data": {
        "enabled": False,
        "csv_path": "real_data/observations.csv",
        "time_col": "time_s",
        "column_map": {
            "queue_len": "queue_len",
            "entries_per_min": "entries_per_min",
            "exits_per_min": "exits_per_min",
            "inside": "inside",
            "density_store": "density_store"
        }
    }
}