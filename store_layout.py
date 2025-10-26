# import matplotlib.pyplot as plt
# from matplotlib.patches import Rectangle, Patch
# from typing import List, Tuple

# # ================== SCENE ==================
# ORIG_W = 22.5
# STORE_X, STORE_Y = 0.0, -4.0
# STORE_W, STORE_H = 25.5, 27.85          # store width/height (top-down view)
# SCALE_X = STORE_W / ORIG_W
# WALL_LW = 2.0

# # clearances/thickness
# WALL_GAP      = 0.03                    # small gap to “press” fixtures to walls
# DIVIDER_THICK = 0.06                    # thickness for dividers/partitions

# # ================== STYLE ==================
# STYLE = {
#     "Shelves":   dict(ec="#355C7D", fc="#A8D0E6", lw=1.6, alpha=0.35, hatch="///"),
#     "Fridge":    dict(ec="#2E7D32", fc="#B9F6CA", lw=1.6, alpha=0.35, hatch="xx"),
#     "Cashier":   dict(ec="#C62828", fc="#FFCDD2", lw=1.6, alpha=0.40, hatch=""),
#     "Divider":   dict(ec="#616161", fc="#E0E0E0", lw=1.4, alpha=0.90, hatch=""),
#     "Vestibule": dict(ec="#6D4C41", fc="#FFE0B2", lw=2.0, alpha=0.25, hatch=""),
#     "Wall":      dict(ec="#000000", fc="none",    lw=WALL_LW, alpha=1.00, hatch=""),
# }

# FIG_FACE = "#FAFAFA"
# AX_FACE  = "#FFFFFF"
# GRID_C   = "#E0E0E0"

# # ================== BASE LAYOUT ==================
# SHELVES_BASE = [
#     (0.5,  -0.2, 0.8, 24.0),  # left wall shelves (will be pressed to the wall)
#     (3.5,   3.4, 0.7, 15.0),
#     (5.8,   3.4, 0.6,  7.0),
#     (8.5,   3.4, 0.7, 15.0),
#     (10.7,  3.4, 0.6, 15.0),
#     (12.8,  3.4, 0.8, 15.0),
#     (14.7,  3.4, 1.0, 15.0),
#     (17.0,  3.4, 0.9, 15.0),

#     # small separators near front (custom shelves/low walls)
#     (19.53, -3.8, 0.4, 5.3),
#     (18.00, -3.8, 0.4, 5.3),
#     (18.45, -3.8, 1.1, 0.42),
# ]
# FRIDGES_BASE = [
#     (0.9,  22.6, 23.1, 0.7),   # top long fridge (pressed to top wall)
#     (20.9,  1.6,  1.2, 22.2),  # right tall fridge (pressed to right wall)
# ]
# CASHIERS_BASE = [
#     (6.0,  -1.5, 1.0, 3.0),
#     (8.3,  -1.5, 1.0, 3.0),
#     (10.835, -1.5, 1.0, 3.0),
# ]

# # dividers (x before width scaling, y, height)
# DIVIDERS_BASE = [
#     (5.8,  -1.75, 3.2),
#     (7.99, -1.75, 3.2),
#     (11.8, -1.75, 3.0),
# ]

# # ================== VESTIBULE (FLUSH TO LEFT/BOTTOM WALLS) ==================
# VEST_X, VEST_Y = STORE_X, STORE_Y
# VEST_W, VEST_H = 5.5, 3.4
# LEFT_DOOR_Y  = (-2.8, -1.3)                        # street ↔ vestibule (left outer wall)
# TOP_DOOR_IN  = (VEST_X + 1.8, VEST_X + 3.0)        # vestibule ↔ store (top of vestibule)
# RIGHT_DOOR_Y = (-2.6, -1.7)                        # store exit to vestibule (right vestibule wall)

# # ================== SMALL CASHIERS — MANUAL PLACEMENT ==================
# CW, CH = 0.9, 0.9
# DW     = DIVIDER_THICK

# # manual coordinates (X, Y, W, H)
# SMALL_CASHIERS = [
#     # bottom row
#     (13.9667, -3.70, CW, CH),
#     (15.4667, -3.70, CW, CH),
#     (17.3667, -3.70, CW, CH),
#     (19.0000, -3.70, CW, CH),
#     # left column
#     (13.7567, -1.50, CW, CH),
#     (13.7567, -0.20, CW, CH),
#     # center 2×2 block
#     (15.7000, -1.50, CW, CH),
#     (15.7000, -0.20, CW, CH),
#     (17.0567, -1.50, CW, CH),
#     (17.0567, -0.20, CW, CH),
#     # right column
#     (19.0000, -2.30, CW, CH),
#     (19.0000, -1.00, CW, CH),
#     (19.0000,  0.30, CW, CH),
# ]

# SMALL_DIVIDERS = [
#     (13.4000, -1.50, DW, 2.20),  # left of the 2-cashier column
#     (16.7500, -1.50, DW, 2.20),  # center between the 2×2 block
#     (20.2000, -3.90, DW, 5.50),  # right side near right column
# ]

# # ================== UTILITIES ==================
# def tr_x(x: float) -> float:
#     return STORE_X + (x - STORE_X) * SCALE_X

# def add_rect(ax, x, y, w, h, label=None, rot_if_tall=True, lw=None, z=2, fs=8):
#     sty = STYLE.get(label, {})
#     ec  = sty.get("ec", "black")
#     fc  = sty.get("fc", "none")
#     _lw = lw if lw is not None else sty.get("lw", 1.5)
#     alpha = sty.get("alpha", 1.0)
#     hatch = sty.get("hatch", "")
#     ax.add_patch(Rectangle((x, y), w, h, linewidth=_lw, edgecolor=ec,
#                            facecolor=fc, zorder=z, alpha=alpha, hatch=hatch))
#     if label:
#         ax.text(x + w/2, y + h/2, label, ha="center", va="center", fontsize=fs,
#                 rotation=(90 if (rot_if_tall and h > w) else 0), zorder=z + 1, color="#222222")

# def seg(ax, x1, y1, x2, y2, lw, z=0, kind="Wall"):
#     ec = STYLE[kind]["ec"]
#     _lw = STYLE[kind]["lw"] if lw is None else lw
#     ax.plot([x1, x2], [y1, y2], color=ec, linewidth=_lw, zorder=z, solid_capstyle="butt")

# def wall_with_gaps(ax, x1, y1, x2, y2, gaps: List[Tuple[float, float]],
#                    lw=WALL_LW, z=0):
#     if abs(y1 - y2) < 1e-9:  # horizontal
#         xs, xe = min(x1, x2), max(x1, x2); cur = xs
#         for a, b in sorted(gaps):
#             a = max(a, xs); b = min(b, xe)
#             if a > cur: seg(ax, cur, y1, a, y1, lw, z, "Wall")
#             cur = max(cur, b)
#         if cur < xe: seg(ax, cur, y1, xe, y1, lw, z, "Wall")
#     else:                     # vertical
#         ys, ye = min(y1, y2), max(y1, y2); cur = ys
#         for a, b in sorted(gaps):
#             a = max(a, ys); b = min(b, ye)
#             if a > cur: seg(ax, x1, cur, x1, a, lw, z, "Wall")
#             cur = max(cur, b)
#         if cur < ye: seg(ax, x1, cur, x1, ye, lw, z, "Wall")

# def draw_outer_walls(ax):
#     x, y, w, h = STORE_X, STORE_Y, STORE_W, STORE_H
#     wall_with_gaps(ax, x,   y,   x,   y + h, gaps=[LEFT_DOOR_Y], lw=WALL_LW, z=0)
#     wall_with_gaps(ax, x+w, y,   x+w, y + h, gaps=[],            lw=WALL_LW, z=0)
#     wall_with_gaps(ax, x,   y+h, x+w, y + h, gaps=[],            lw=WALL_LW, z=0)
#     wall_with_gaps(ax, x,   y,   x+w, y,     gaps=[],            lw=WALL_LW, z=0)

# def draw_vestibule_rect(ax):
#     x, y, w, h = VEST_X, VEST_Y, VEST_W, VEST_H
#     wall_with_gaps(ax, x,     y,   x,     y + h, gaps=[LEFT_DOOR_Y],  lw=3.0, z=1)
#     wall_with_gaps(ax, x + w, y,   x + w, y + h, gaps=[RIGHT_DOOR_Y], lw=3.0, z=1)
#     wall_with_gaps(ax, x,     y+h, x + w, y + h, gaps=[TOP_DOOR_IN],  lw=3.0, z=1)
#     wall_with_gaps(ax, x,     y,   x + w, y,     gaps=[],             lw=3.0, z=1)
#     add_rect(ax, x, y, w, h, label="Vestibule", rot_if_tall=False, lw=1.0, z=0, fs=0)

# # bare wall segments
# def add_horizontal_wall_segment(ax, y: float, x0: float, x1: float,
#                                 lw: float = WALL_LW, z: int = 1):
#     if x1 < x0: x0, x1 = x1, x0
#     seg(ax, x0, y, x1, y, lw, z, "Wall")

# def add_vertical_wall_segment(ax, x: float, y0: float, y1: float,
#                               lw: float = WALL_LW, z: int = 1):
#     if y1 < y0: y0, y1 = y1, y0
#     seg(ax, x, y0, x, y1, lw, z, "Wall")

# def draw_small_cashiers_manual(ax):
#     for x, y, w, h in SMALL_CASHIERS:
#         add_rect(ax, x, y, w, h, "Cashier", rot_if_tall=False, fs=7)
#     for x, y, w, h in SMALL_DIVIDERS:
#         add_rect(ax, x, y, w, h, "Divider", rot_if_tall=False, lw=2.0)

# def legend_patch(kind: str, label: str) -> Patch:
#     s = STYLE[kind]
#     return Patch(facecolor=s.get("fc", "none"),
#                  edgecolor=s.get("ec", "black"),
#                  hatch=s.get("hatch", ""),
#                  alpha=s.get("alpha", 1.0),
#                  label=label)

# # ================== MAIN RENDER ==================
# def draw_layout():
#     fig, ax = plt.subplots(figsize=(12, 7))
#     fig.set_facecolor(FIG_FACE)
#     ax.set_facecolor(AX_FACE)
#     ax.set_aspect('equal')
#     ax.set_xlabel('X (m)')
#     ax.set_ylabel('Y (m)')
#     ax.grid(True, which="both", color=GRID_C, linewidth=0.8, alpha=0.7)
#     ax.set_axisbelow(True)
#     ax.format_coord = lambda x, y: f"x={x:.2f}, y={y:.2f}"

#     # Ctrl + wheel zoom to cursor
#     ctrl = {'p': False}
#     def on_key_press(e):
#         if e.key == 'control': ctrl['p'] = True
#     def on_key_release(e):
#         if e.key == 'control': ctrl['p'] = False
#     def on_scroll(e):
#         if not ctrl['p'] or e.inaxes is None or e.xdata is None: return
#         s = 1.1 if e.button == 'down' else (1/1.1)
#         xmin, xmax = ax.get_xlim(); ymin, ymax = ax.get_ylim()
#         x0, y0 = e.xdata, e.ydata
#         ax.set_xlim(x0 - (x0 - xmin)*s, x0 + (xmax - x0)*s)
#         ax.set_ylim(y0 - (y0 - ymin)*s, y0 + (ymax - y0)*s)
#         e.canvas.draw_idle()
#     fig.canvas.mpl_connect('key_press_event', on_key_press)
#     fig.canvas.mpl_connect('key_release_event', on_key_release)
#     fig.canvas.mpl_connect('scroll_event', on_scroll)

#     # outer walls and vestibule
#     draw_outer_walls(ax)
#     draw_vestibule_rect(ax)

#     # shelves (first left pressed to wall)
#     for i, (x, y, w, h) in enumerate(SHELVES_BASE):
#         xx = STORE_X + WALL_GAP if i == 0 else tr_x(x)
#         add_rect(ax, xx, y, w, h, "Shelves", z=2)

#     # fridges (pressed to top/right walls)
#     top_w, top_h = FRIDGES_BASE[0][2], FRIDGES_BASE[0][3]
#     add_rect(ax, tr_x(FRIDGES_BASE[0][0]),
#              STORE_Y + STORE_H - top_h - WALL_GAP,
#              top_w, top_h, "Fridge", z=2)
#     r_w, r_h = FRIDGES_BASE[1][2], FRIDGES_BASE[1][3]
#     add_rect(ax, STORE_X + STORE_W - r_w - WALL_GAP,
#              FRIDGES_BASE[1][1], r_w, r_h, "Fridge", z=2)

#     # main cashiers
#     for x, y, w, h in CASHIERS_BASE:
#         add_rect(ax, tr_x(x), y, w, h, "Cashier", rot_if_tall=False, z=2)

#     # small cashiers (manual)
#     draw_small_cashiers_manual(ax)

#     # dividers
#     for x0, y0, h in DIVIDERS_BASE:
#         add_rect(ax, tr_x(x0), y0, DIVIDER_THICK, h, "Divider", rot_if_tall=False, lw=2.0, z=2)

#     # example extra horizontal wall segment (adjust or remove)
#     add_horizontal_wall_segment(ax, y=1.6, x0=STORE_X + 22.5, x1=STORE_X + 24.27, lw=2.5, z=1)

#     # legend
#     ax.legend(
#         handles=[
#             legend_patch("Shelves", "Shelves"),
#             legend_patch("Fridge", "Fridge"),
#             legend_patch("Cashier", "Cashier"),
#             legend_patch("Divider", "Divider"),
#             legend_patch("Vestibule", "Vestibule"),
#         ],
#         loc="upper left", frameon=True, framealpha=0.9
#     )

#     # view and window
#     ax.set_xlim(STORE_X, STORE_X + STORE_W)
#     ax.set_ylim(STORE_Y, STORE_Y + STORE_H)
#     mng = plt.get_current_fig_manager()
#     for attr in ("state", "showMaximized", "full_screen_toggle"):
#         try:
#             if attr == "state": mng.window.state("zoomed")
#             elif attr == "showMaximized": mng.window.showMaximized()
#             else: mng.full_screen_toggle()
#             break
#         except Exception:
#             pass
#     fig.subplots_adjust(left=0.07, right=0.995, bottom=0.08, top=0.98)
#     plt.show()

# if __name__ == '__main__':
#     draw_layout()



import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from typing import List, Tuple

# ================== SCENE ==================
ORIG_W = 22.5
STORE_X, STORE_Y = 0.0, -4.0
STORE_W, STORE_H = 25.5, 27.85          # store width/height (top-down view)
SCALE_X = STORE_W / ORIG_W
WALL_LW = 2.0

# clearances/thickness
WALL_GAP      = 0.03                    # small gap to “press” fixtures to walls
DIVIDER_THICK = 0.06                    # thickness for dividers/partitions

# ================== STYLE ==================
STYLE = {
    "Shelves":   dict(ec="#355C7D", fc="#A8D0E6", lw=1.6, alpha=0.35, hatch="///"),
    "Fridge":    dict(ec="#2E7D32", fc="#B9F6CA", lw=1.6, alpha=0.35, hatch="xx"),
    "Cashier":   dict(ec="#C62828", fc="#FFCDD2", lw=1.6, alpha=0.40, hatch=""),
    "Divider":   dict(ec="#616161", fc="#E0E0E0", lw=1.4, alpha=0.90, hatch=""),
    "Vestibule": dict(ec="#6D4C41", fc="#FFE0B2", lw=2.0, alpha=0.25, hatch=""),
    "Wall":      dict(ec="#000000", fc="none",    lw=WALL_LW, alpha=1.00, hatch=""),
}

FIG_FACE = "#FAFAFA"
AX_FACE  = "#FFFFFF"
GRID_C   = "#E0E0E0"

# ================== BASE LAYOUT ==================
SHELVES_BASE = [
    (0.5,  -0.2, 0.8, 24.0),  # left wall shelves (will be pressed to the wall)
    (3.5,   3.4, 0.7, 15.0),
    (5.8,   3.4, 0.6,  7.0),
    (8.5,   3.4, 0.7, 15.0),
    (10.7,  3.4, 0.6, 15.0),
    (12.8,  3.4, 0.8, 15.0),
    (14.7,  3.4, 1.0, 15.0),
    (17.0,  3.4, 0.9, 15.0),

    # small separators near front (custom shelves/low walls)
    (19.53, -3.8, 0.4, 5.3),
    (18.00, -3.8, 0.4, 5.3),
    (18.45, -3.8, 1.1, 0.42),
]
FRIDGES_BASE = [
    (0.9,  22.6, 23.1, 0.7),   # top long fridge (pressed to top wall)
    (20.9,  1.6,  1.2, 22.2),  # right tall fridge (pressed to right wall)
]
CASHIERS_BASE = [
    (6.0,  -1.5, 1.0, 3.0),
    (8.3,  -1.5, 1.0, 3.0),
    (10.835, -1.5, 1.0, 3.0),
]

# dividers (x before width scaling, y, height)
DIVIDERS_BASE = [
    (5.8,  -1.75, 3.2),
    (7.99, -1.75, 3.2),
    (11.8, -1.75, 3.0),
]

# ================== VESTIBULE (FLUSH TO LEFT/BOTTOM WALLS) ==================
VEST_X, VEST_Y = STORE_X, STORE_Y
VEST_W, VEST_H = 5.5, 3.4
LEFT_DOOR_Y  = (-2.8, -1.3)                        # street ↔ vestibule (left outer wall)
TOP_DOOR_IN  = (VEST_X + 1.8, VEST_X + 3.0)        # vestibule ↔ store (top of vestibule)
RIGHT_DOOR_Y = (-2.6, -1.7)                        # store exit to vestibule (right vestibule wall)

# ================== SMALL CASHIERS — MANUAL PLACEMENT ==================
CW, CH = 0.9, 0.9
DW     = DIVIDER_THICK

# manual coordinates (X, Y, W, H)
SMALL_CASHIERS = [
    # bottom row
    (13.9667, -3.70, CW, CH),
    (15.4667, -3.70, CW, CH),
    (17.3667, -3.70, CW, CH),
    (19.0000, -3.70, CW, CH),
    # left column
    (13.7567, -1.50, CW, CH),
    (13.7567, -0.20, CW, CH),
    # center 2×2 block
    (15.7000, -1.50, CW, CH),
    (15.7000, -0.20, CW, CH),
    (17.0567, -1.50, CW, CH),
    (17.0567, -0.20, CW, CH),
    # right column
    (19.0000, -2.30, CW, CH),
    (19.0000, -1.00, CW, CH),
    (19.0000,  0.30, CW, CH),
]

SMALL_DIVIDERS = [
    (13.4000, -1.50, DW, 2.20),  # left of the 2-cashier column
    (16.7500, -1.50, DW, 2.20),  # center between the 2×2 block
    (20.2000, -3.90, DW, 5.50),  # right side near right column
]

# ================== UTILITIES ==================
def tr_x(x: float) -> float:
    return STORE_X + (x - STORE_X) * SCALE_X

def add_rect(ax, x, y, w, h, label=None, rot_if_tall=True, lw=None, z=2, fs=8):
    sty = STYLE.get(label, {})
    ec  = sty.get("ec", "black")
    fc  = sty.get("fc", "none")
    _lw = lw if lw is not None else sty.get("lw", 1.5)
    alpha = sty.get("alpha", 1.0)
    hatch = sty.get("hatch", "")
    ax.add_patch(Rectangle((x, y), w, h, linewidth=_lw, edgecolor=ec,
                           facecolor=fc, zorder=z, alpha=alpha, hatch=hatch))
    # draw text for everything EXCEPT dividers
    if label and label != "Divider":
        ax.text(x + w/2, y + h/2, label, ha="center", va="center", fontsize=fs,
                rotation=(90 if (rot_if_tall and h > w) else 0),
                zorder=z + 1, color="#222222")

def seg(ax, x1, y1, x2, y2, lw, z=0, kind="Wall"):
    ec = STYLE[kind]["ec"]
    _lw = STYLE[kind]["lw"] if lw is None else lw
    ax.plot([x1, x2], [y1, y2], color=ec, linewidth=_lw, zorder=z, solid_capstyle="butt")

def wall_with_gaps(ax, x1, y1, x2, y2, gaps: List[Tuple[float, float]],
                   lw=WALL_LW, z=0):
    if abs(y1 - y2) < 1e-9:  # horizontal
        xs, xe = min(x1, x2), max(x1, x2); cur = xs
        for a, b in sorted(gaps):
            a = max(a, xs); b = min(b, xe)
            if a > cur: seg(ax, cur, y1, a, y1, lw, z, "Wall")
            cur = max(cur, b)
        if cur < xe: seg(ax, cur, y1, xe, y1, lw, z, "Wall")
    else:                     # vertical
        ys, ye = min(y1, y2), max(y1, y2); cur = ys
        for a, b in sorted(gaps):
            a = max(a, ys); b = min(b, ye)
            if a > cur: seg(ax, x1, cur, x1, a, lw, z, "Wall")
            cur = max(cur, b)
        if cur < ye: seg(ax, x1, cur, x1, ye, lw, z, "Wall")

def draw_outer_walls(ax):
    x, y, w, h = STORE_X, STORE_Y, STORE_W, STORE_H
    wall_with_gaps(ax, x,   y,   x,   y + h, gaps=[LEFT_DOOR_Y], lw=WALL_LW, z=0)
    wall_with_gaps(ax, x+w, y,   x+w, y + h, gaps=[],            lw=WALL_LW, z=0)
    wall_with_gaps(ax, x,   y+h, x+w, y + h, gaps=[],            lw=WALL_LW, z=0)
    wall_with_gaps(ax, x,   y,   x+w, y,     gaps=[],            lw=WALL_LW, z=0)

def draw_vestibule_rect(ax):
    x, y, w, h = VEST_X, VEST_Y, VEST_W, VEST_H
    wall_with_gaps(ax, x,     y,   x,     y + h, gaps=[LEFT_DOOR_Y],  lw=3.0, z=1)
    wall_with_gaps(ax, x + w, y,   x + w, y + h, gaps=[RIGHT_DOOR_Y], lw=3.0, z=1)
    wall_with_gaps(ax, x,     y+h, x + w, y + h, gaps=[TOP_DOOR_IN],  lw=3.0, z=1)
    wall_with_gaps(ax, x,     y,   x + w, y,     gaps=[],             lw=3.0, z=1)
    add_rect(ax, x, y, w, h, label="Vestibule", rot_if_tall=False, lw=1.0, z=0, fs=0)

# bare wall segments
def add_horizontal_wall_segment(ax, y: float, x0: float, x1: float,
                                lw: float = WALL_LW, z: int = 1):
    if x1 < x0: x0, x1 = x1, x0
    seg(ax, x0, y, x1, y, lw, z, "Wall")

def add_vertical_wall_segment(ax, x: float, y0: float, y1: float,
                              lw: float = WALL_LW, z: int = 1):
    if y1 < y0: y0, y1 = y1, y0
    seg(ax, x, y0, x, y1, lw, z, "Wall")

def draw_small_cashiers_manual(ax):
    for x, y, w, h in SMALL_CASHIERS:
        add_rect(ax, x, y, w, h, "Cashier", rot_if_tall=False, fs=7)
    for x, y, w, h in SMALL_DIVIDERS:
        # no label for dividers
        add_rect(ax, x, y, w, h, None, rot_if_tall=False, lw=STYLE["Divider"]["lw"])

def legend_patch(kind: str, label: str) -> Patch:
    s = STYLE[kind]
    return Patch(facecolor=s.get("fc", "none"),
                 edgecolor=s.get("ec", "black"),
                 hatch=s.get("hatch", ""),
                 alpha=s.get("alpha", 1.0),
                 label=label)

# ================== MAIN RENDER ==================
def draw_layout():
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.set_facecolor(FIG_FACE)
    ax.set_facecolor(AX_FACE)
    ax.set_aspect('equal')
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.grid(True, which="both", color=GRID_C, linewidth=0.8, alpha=0.7)
    ax.set_axisbelow(True)
    ax.format_coord = lambda x, y: f"x={x:.2f}, y={y:.2f}"

    # Ctrl + wheel zoom to cursor
    ctrl = {'p': False}
    def on_key_press(e):
        if e.key == 'control': ctrl['p'] = True
    def on_key_release(e):
        if e.key == 'control': ctrl['p'] = False
    def on_scroll(e):
        if not ctrl['p'] or e.inaxes is None or e.xdata is None: return
        s = 1.1 if e.button == 'down' else (1/1.1)
        xmin, xmax = ax.get_xlim(); ymin, ymax = ax.get_ylim()
        x0, y0 = e.xdata, e.ydata
        ax.set_xlim(x0 - (x0 - xmin)*s, x0 + (xmax - x0)*s)
        ax.set_ylim(y0 - (y0 - ymin)*s, y0 + (ymax - y0)*s)
        e.canvas.draw_idle()
    fig.canvas.mpl_connect('key_press_event', on_key_press)
    fig.canvas.mpl_connect('key_release_event', on_key_release)
    fig.canvas.mpl_connect('scroll_event', on_scroll)

    # outer walls and vestibule
    draw_outer_walls(ax)
    draw_vestibule_rect(ax)

    # shelves (first left pressed to wall)
    for i, (x, y, w, h) in enumerate(SHELVES_BASE):
        xx = STORE_X + WALL_GAP if i == 0 else tr_x(x)
        add_rect(ax, xx, y, w, h, "Shelves", z=2)

    # fridges (pressed to top/right walls)
    top_w, top_h = FRIDGES_BASE[0][2], FRIDGES_BASE[0][3]
    add_rect(ax, tr_x(FRIDGES_BASE[0][0]),
             STORE_Y + STORE_H - top_h - WALL_GAP,
             top_w, top_h, "Fridge", z=2)
    r_w, r_h = FRIDGES_BASE[1][2], FRIDGES_BASE[1][3]
    add_rect(ax, STORE_X + STORE_W - r_w - WALL_GAP,
             FRIDGES_BASE[1][1], r_w, r_h, "Fridge", z=2)

    # main cashiers
    for x, y, w, h in CASHIERS_BASE:
        add_rect(ax, tr_x(x), y, w, h, "Cashier", rot_if_tall=False, z=2)

    # small cashiers (manual)
    draw_small_cashiers_manual(ax)

    # vertical/horizontal dividers (no labels)
    for x0, y0, h in DIVIDERS_BASE:
        add_rect(ax, tr_x(x0), y0, DIVIDER_THICK, h, None, rot_if_tall=False,
                 lw=STYLE["Divider"]["lw"], z=2)

    # example extra horizontal wall segment (adjust or remove)
    add_horizontal_wall_segment(ax, y=1.6, x0=STORE_X + 22.5, x1=STORE_X + 24.27, lw=2.5, z=1)

    # legend
    ax.legend(
        handles=[
            legend_patch("Shelves", "Shelves"),
            legend_patch("Fridge", "Fridge"),
            legend_patch("Cashier", "Cashier"),
            legend_patch("Vestibule", "Vestibule"),
        ],
        loc="upper left", frameon=True, framealpha=0.9
    )

    # view and window
    ax.set_xlim(STORE_X, STORE_X + STORE_W)
    ax.set_ylim(STORE_Y, STORE_Y + STORE_H)
    mng = plt.get_current_fig_manager()
    for attr in ("state", "showMaximized", "full_screen_toggle"):
        try:
            if attr == "state": mng.window.state("zoomed")
            elif attr == "showMaximized": mng.window.showMaximized()
            else: mng.full_screen_toggle()
            break
        except Exception:
            pass
    fig.subplots_adjust(left=0.07, right=0.995, bottom=0.08, top=0.98)
    plt.show()

if __name__ == '__main__':
    draw_layout()
