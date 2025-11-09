CONFIG = {
    "dt": 0.05,
    "steps": 10000,
    "n_agents": 3,  # może być ignorowane, jeśli "agents" istnieje

    "environment": {
        "scale": 40,  # każda jednostka = 40 pikseli → scena 800x600
        "width": 20,  # jednostki symulacji
        "height": 15,
        "exit": [17, 7.5],  # środek drzwi
        "walls": [
            ((0, 0), (20, 0)),     # dolna ściana
            ((0, 0), (0, 13)),     # lewa ściana
            ((0, 14.5), (0, 15)),     # lewa ściana
            ((20, 0), (20, 15)),   # prawa ściana
            ((0, 15), (20, 15)),   # górna ściana
        ],
        "doors": [
            ((0, 13), (0, 14.5)),     # dolna ściana
            # ((0, 0), (0, 15)),
        ],
        "shelves": [
            ((2, 2), (2, 10)),
            ((2.5, 2), (2.5, 10)),
        ],
        "pallets": [
            {"pos": (1, 1), "size": (1, 1)},
        ],
        "cash_registers": [
            {"pos": (3, 4), "size": (1, 1)},
        ]
    },

    "sfm": {
        "A": 2.0,
        "B": 0.8,
        "A_w": 10.0,
        "B_w": 0.2,
        "desired_speed": 1.3,
        "tau": 0.5,
    },

    "agents": [
        {"path": [(-1, 15), (1, 14), (1, 1), (19, 1), (17, 7.5)]},
        {"path": [(-1.5, 14), (1, 14),(1, 10), (1, 12), (17, 7.5)]},
        {"path": [(-2, 14.5), (1, 14), (17, 7.5)]}
    ]
}
