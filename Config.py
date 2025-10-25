CONFIG = {
    "dt": 0.05,
    "steps": 10000,
    "n_agents": 20,

    "environment": {
        "scale": 50,     # przeliczenie z metrów na piksele (1m = 50px)
        "width": 20 * 50,   # 10m * 50px
        "height": 15 * 50,  # 10m * 50px
        "exit": [16, 6], # pozycja drzwi w metrach
        "walls": [
            ((0, 0), (16, 0)),   # dolna ściana
            ((0, 0), (0, 12)),   # lewa ściana
            ((16, 0), (16, 12)), # prawa ściana
            ((0, 12), (16, 12)), # górna ściana
        ],
        "door": {
            "y_min": 5,
            "y_max": 7,   # otwór w prawej ścianie
            "x": 16
        }
    },

    "sfm": {
        "A": 2.0,
        "B": 0.5,
        "A_w": 10.0,
        "B_w": 0.2,
        "desired_speed": 1.3,
        "tau": 0.5
    }
}
