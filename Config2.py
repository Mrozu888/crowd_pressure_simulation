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
            #aleja z alkoholami (poszerzona)
            ((14.75, 12), (14.75, 14.85)),
            ((15, 12), (15, 14.85)),
            ((14.75, 14.85), (15, 14.85)),
            ((14.75, 12), (15, 12)),
            ((15, 14.6), (16.75, 14.6)),
            ((15, 14.85), (17.0,14.85)),
            ((16.75, 12), (16.75, 14.85)),
            ((17, 12), (17, 14.85)),
            ((16.75, 12), (17, 12)),
           
            
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
            ((17, 12), (20, 12)), #sciana prawo dol (kolo alkoholu)
            #((18, 12), (20, 12)), 
        ],

        "shelves_type": [
            {
                "name": "ALKOHOLE",
                "rect": {
                    "pos": (14.75, 0.15),
                    "size": (2.25, 2.85)
                },
                "color": (160, 60, 60)
            },
            {
                "name": "PIECZYWO",
                "rect": {
                    "pos": (0.0, 3.0),
                    "size": (0.5, 9.0)
                },
                "color": (220, 200, 120)
            },
             {
                "name": "MIĘSO/WĘDLINY",
                "rect": {
                    "pos": (0.0, 12.0),
                    "size": (0.5, 3.0)
                },
                "color": (100, 0, 120)
            },
            {
                "name": "MIĘSO/WĘDLINY",
                "rect": {
                    "pos": (0.0, 14.5),
                    "size": (3.0, 0.5)
                },
                "color": (100, 0, 120)
            },
            {
                "name": "PRODUKTY CHŁODZONE",
                "rect": {
                    "pos": (3.0, 14.5),
                    "size": (16.0, 0.5)
                },
                "color": (100, 0, 200)
            },
            {
                "name": "NABIAŁ/WĘDLINY",
                "rect": {
                    "pos": (19.0, 3.0),
                    "size": (1.0, 12.0)
                },
                "color": (100, 0, 0)
            },
            {
                "name": "PRZEKĄSKI/ NAPOJE",
                "rect": {
                    "pos": (16.25, 4),
                    "size": (1.0, 9.0)
                },
                "color": (100, 100, 100)
            },
            {
                "name": "CHEMIA/ NAPOJE",
                "rect": {
                    "pos": (14.25, 4),
                    "size": (0.5, 9.0)
                },
                "color": (150, 200, 50)
            },
            {
                "name": "KONSERWY/DŻEMY",
                "rect": {
                    "pos": (12.25, 4),
                    "size": (0.5, 9.0)
                },
                "color": (50, 50, 100)
            },
            {
                "name": "MAKARONY/ORZECHY/KASZE",
                "rect": {
                    "pos": (10.25, 4),
                    "size": (0.5, 9.0)
                },
                "color": (200, 200, 0)
            },
            {
                "name": "INNE",
                "rect": {
                    "pos": (8.25, 4),
                    "size": (0.5, 9.0)
                },
                "color": (200, 0, 0)
            },
        
            {
                "name": "SŁODYCZE / CIASTKA",
                "rect": {
                    "pos": (6.25, 4),
                    "size": (0.5, 9.0)
                },
                "color": (0, 0, 100)
            },
            {
                "name": "HERBTYNA/ KAWA /CUKIERKI",
                "rect": {
                    "pos": (4.25, 9.5),
                    "size": (0.5, 3.5)
                },
                "color": (150, 170, 20)
            },
            {
                "name": "HERBTYNA/ KAWA /CUKIERKI",
                "rect": {
                    "pos": (4.25, 4),
                    "size": (0.5, 4.5)
                },
                "color": (150, 170, 20)
            },
            {
                "name": "WARZYWA / OWOCE",
                "rect": {
                    "pos": (2.25, 4),
                    "size": (1.0, 9.0)
                },
                "color": (0, 50, 50)
            },
        ],

        "pallets": [],
        "cash_registers": [
        {"pos": (5.5, 12), "size": (0.6, 1.5)},
        {"pos": (7, 12), "size": (0.6, 1.5)},
        {"pos": (8.5, 12), "size": (0.6, 1.5)},
        {"pos": (9.25, 11.85), "size": (0.6, 0.6)},
        {"pos": (9.25, 12.60), "size": (0.6, 0.6)},
        # {"pos": (9.75, 14.35), "size": (0.6, 0.6)},
        # {"pos": (10.75, 14.35), "size": (0.6, 0.6)},
        # {"pos": (12.5, 14.35), "size": (0.6, 0.6)},
        {"pos": (11.25, 11.85), "size": (0.6, 0.6)},
        {"pos": (11.25, 12.60), "size": (0.6, 0.6)},
        {"pos": (12, 11.85), "size": (0.6, 0.6)},
        {"pos": (12, 12.60), "size": (0.6, 0.6)},
        {"pos": (14, 12), "size": (0.6, 0.6)},
        {"pos": (14, 12.75), "size": (0.6, 0.6)},
        {"pos": (14, 13.5), "size": (0.6, 0.6)},
        {"pos": (14, 14.25), "size": (0.6, 0.6)},
    ],
        "cash_payment": [
            (5.3, 13),
            (6.8, 13),
            (8.3, 13),
            # ###
            (10, 12.3),
            (10, 13.0),
            (11.1, 12.3),
            (11.1, 13.0),
            ###
            # (10.1, 14.25),
            # (11, 14.25),
            # (12.8, 14.25),
            ###
            (12.75, 12.3),
            (12.75, 13.0),
            ##
            (13.85, 12.35),
            (13.85, 13.1),
            (13.85, 13.8),
            (13.85, 14.6),
        ],


    },

    "sfm": {
#         A (float): Strength of agent-agent repulsion force
#         B (float): Range of agent-agent repulsion force
#         A_w (float): Strength of agent-wall repulsion force
#         B_w (float): Range of agent-wall repulsion force
#         desired_speed (float): Preferred movement speed for agents
#         relax_time (float): Characteristic reaction time for velocity adjustments
        "A": 1.5,
        "B": 0.4,
        "A_w": 10.0,
        "B_w": 0.08,
        "desired_speed": 1.2,
        "tau": 0.6,
    },

    "agent_generation": {
        "spawn_rate": 0.45,
        # "n_agents": 20,
        # "max_spawn_time": 30.0,

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
    # --- ALEJA 1 (X ≈ 1.5) - Np. Warzywa/Owoce (Częste, ale szybkie zakupy) ---
    {"name": "A1_Wejście_Promocja", "pos": (1.5, 2.0), "prob": 0.2},
    {"name": "A1_Dół",              "pos": (1.5, 4.0), "prob": 0.15},
    {"name": "A1_Środek_Dół",       "pos": (1.5, 5.5), "prob": 0.10},
    {"name": "A1_Środek_Góra",      "pos": (1.5, 7.5), "prob": 0.12},
    {"name": "A1_Góra",             "pos": (1.5, 9.5), "prob": 0.15},
    {"name": "A1_Szczyt",           "pos": (1.5, 11.0), "prob": 0.08},

    # --- ALEJA 2 (X ≈ 3.75) - Np. Chemia (Rzadziej wybierane) ---
    {"name": "A2_Dół",              "pos": (3.75, 2.5), "prob": 0.05},
    {"name": "A2_Środek_Dół",       "pos": (3.75, 4.5), "prob": 0.06},
    {"name": "A2_Środek",           "pos": (3.75, 6.5), "prob": 0.04},
    {"name": "A2_Środek_Góra",      "pos": (3.75, 8.5), "prob": 0.07},
    {"name": "A2_Szczyt",           "pos": (3.75, 10.5), "prob": 0.05},

    # --- ALEJA 3 (X ≈ 5.5) - Np. Słodycze/Przekąski (Impulsowe) ---
    {"name": "A3_Dół_Promocja",     "pos": (5.5, 2.0), "prob": 0.18},
    {"name": "A3_Dół",              "pos": (5.5, 4.0), "prob": 0.12},
    {"name": "A3_Środek",           "pos": (5.5, 6.5), "prob": 0.15},
    {"name": "A3_Góra",             "pos": (5.5, 9.0), "prob": 0.10},
    {"name": "A3_Szczyt",           "pos": (5.5, 11.0), "prob": 0.08},

    # --- ALEJA 4 (X ≈ 7.5) - Np. Makarony/Kasze (Standard) ---
    {"name": "A4_Dół",              "pos": (7.5, 3.0), "prob": 0.10},
    {"name": "A4_Środek_Dół",       "pos": (7.5, 5.0), "prob": 0.18},
    {"name": "A4_Środek_Góra",      "pos": (7.5, 7.5), "prob": 0.15},
    {"name": "A4_Góra",             "pos": (7.5, 9.5), "prob": 0.11},

    # --- ALEJA 5 (X ≈ 9.5) - Np. Napoje/Soki (Ciężkie, więc rzadziej na początku) ---
    {"name": "A5_Dół",              "pos": (9.5, 2.5), "prob": 0.18},
    {"name": "A5_Środek",           "pos": (9.5, 6.0), "prob": 0.15},
    {"name": "A5_Góra",             "pos": (9.5, 9.0), "prob": 0.12},
    {"name": "A5_Szczyt",           "pos": (9.5, 11.0), "prob": 0.17},

    # --- ALEJA 6 (X ≈ 11.5) - Np. Kawa/Herbata ---
    {"name": "A6_Dół",              "pos": (11.5, 3.0), "prob": 0.14},
    {"name": "A6_Środek_Dół",       "pos": (11.5, 5.5), "prob": 0.29},
    {"name": "A6_Środek_Góra",      "pos": (11.5, 8.0), "prob": 0.11},
    {"name": "A6_Szczyt",           "pos": (11.5, 10.5), "prob": 0.13},

    # --- ALEJA 7 (X ≈ 13.5) - Np. Konserwy/Dżemy ---
    {"name": "A7_Dół",              "pos": (13.5, 2.5), "prob": 0.17},
    {"name": "A7_Środek",           "pos": (13.5, 6.0), "prob": 0.16},
    {"name": "A7_Środek",           "pos": (13.5, 6.0), "prob": 0.13},
    {"name": "A7_Góra",             "pos": (13.5, 9.5), "prob": 0.18},

    # --- ALEJA 8 (X ≈ 15.5) - Np. Pieczywo (BARDZO POPULARNE - Hotspot) ---
    {"name": "A8_Pieczywo_Dół",     "pos": (15.5, 2.5), "prob": 0.35}, # Duża szansa
    {"name": "A8_Pieczywo_Środek",  "pos": (15.5, 5.0), "prob": 0.20},
    {"name": "A8_Bułki_Góra",       "pos": (15.5, 8.0), "prob": 0.30},
    {"name": "A8_Szczyt",           "pos": (15.5, 10.5), "prob": 0.10},

    # --- ALEJA 9 (X ≈ 18) - Np. Nabiał/Mleko (BARDZO POPULARNE - Hotspot) ---
    {"name": "A9_Jogurty",          "pos": (18.0, 2.0), "prob": 0.18},
    {"name": "A9_Sery",             "pos": (18.0, 4.5), "prob": 0.22},
    {"name": "A9_Mleko_Środek",     "pos": (18.0, 7.0), "prob": 0.20},
    {"name": "A9_Jajka",            "pos": (18.0, 9.5), "prob": 0.25},
    {"name": "A9_Masło_Szczyt",     "pos": (18.0, 11.5), "prob": 0.10},

    # --- ŚCIANA POŁUDNIOWA - Mięso/Wędliny/Lada ---
    {"name": "Lada_Mięsna_1",       "pos": (3.0, 1.25), "prob": 0.12},
    {"name": "Lada_Mięsna_2",       "pos": (5.0, 1.25), "prob": 0.10},
    {"name": "Lada_Sery_Waga",      "pos": (8.0, 1.25), "prob": 0.15},
    {"name": "Lada_Ryby",           "pos": (11.0, 1.25), "prob": 0.08},
    {"name": "Lodówka_Mrożonki_1",  "pos": (14.0, 1.25), "prob": 0.18},
    {"name": "Lodówka_Mrożonki_2",  "pos": (17.0, 1.25), "prob": 0.18},

    # --- alkohole
    {"name": "ALKOHOLE",       "pos": (15.0, 14.25), "prob": 0.25},
    {"name": "WINA",       "pos": (16.5, 14.25), "prob": 0.25},
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