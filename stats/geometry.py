"""
Geometry helpers for statistics.

This module duplicates the store/vestibule geometry used for visualization
to classify agent positions into zones and queue regions, and to provide
a regular grid for heatmap aggregation.
"""

from dataclasses import dataclass
from typing import Tuple, List, Dict
import math

# ----------------------
# Geometry constants (copy of your store_layout.py)
# ----------------------

ORIG_W = 22.5
STORE_X, STORE_Y = 0.0, -4.0
STORE_W, STORE_H = 25.5, 27.85
SCALE_X = STORE_W / ORIG_W

# Vestibule
VEST_X, VEST_Y = STORE_X, STORE_Y
VEST_W, VEST_H = 5.5, 3.4

# Door intervals in world coordinates (y-ranges on walls)
LEFT_DOOR_Y  = (-2.8, -1.3)                 # street ↔ vestibule (left outer wall)
TOP_DOOR_IN  = (VEST_X + 1.8, VEST_X + 3.0) # vestibule ↔ store (top of vestibule, x-interval)
RIGHT_DOOR_Y = (-2.6, -1.7)                 # store ↔ vestibule (right vestibule wall, y-interval)

# Cashier rectangles approximation (for queue statistics)
# You can refine these if needed; now they are coarse bounding boxes.
CASHIER_ZONE_RECTS = [
    # Big cashiers block (front of the store)
    (5.0, -2.0, 8.0, 5.0),   # (x, y, w, h) – adjust to your needs
]
# Optional: separate queue rectangles per cashier if you want
QUEUE_RECTS = [
    # One general queue area in front of big cashiers
    {"name": "front_cashiers_queue", "rect": (5.0, -3.5, 10.0, 3.5)},
]


@dataclass
class ZoneInfo:
    name: str
    rect: Tuple[float, float, float, float]  # (x, y, w, h)


class StatsGeometry:
    """
    Pure geometric helper: no access to agents/simulation internals.

    Provides:
      - zone classification (street / vestibule / store)
      - queue region membership
      - heatmap grid information
    """

    def __init__(self,
                 grid_nx: int = 32,
                 grid_ny: int = 32) -> None:
        # World bounds are store rectangle extended a bit to the left for "street"
        self.store_rect = (STORE_X, STORE_Y, STORE_W, STORE_H)
        self.vest_rect  = (VEST_X, VEST_Y, VEST_W, VEST_H)

        # Artificial "street" rectangle to the left of the store
        street_w = 3.0
        self.street_rect = (STORE_X - street_w, STORE_Y, street_w, VEST_H)

        self.zones: Dict[str, ZoneInfo] = {
            "street":    ZoneInfo("street",    self.street_rect),
            "vestibule": ZoneInfo("vestibule", self.vest_rect),
            "store":     ZoneInfo("store",     self.store_rect),
        }

        # Heatmap grid setup over store+street
        min_x = self.street_rect[0]
        min_y = STORE_Y
        max_x = STORE_X + STORE_W
        max_y = STORE_Y + STORE_H

        self.grid_min_x = min_x
        self.grid_min_y = min_y
        self.grid_max_x = max_x
        self.grid_max_y = max_y

        self.grid_nx = grid_nx
        self.grid_ny = grid_ny
        self.cell_w = (max_x - min_x) / grid_nx
        self.cell_h = (max_y - min_y) / grid_ny

        self.queue_rects = QUEUE_RECTS
        self.cashier_zone_rects = CASHIER_ZONE_RECTS

    # ------------------
    # Zone classification
    # ------------------
    def point_in_rect(self, x: float, y: float, rect: Tuple[float, float, float, float]) -> bool:
        rx, ry, rw, rh = rect
        return (rx <= x <= rx + rw) and (ry <= y <= ry + rh)

    def classify_zone(self, x: float, y: float) -> str:
        """Return 'street', 'vestibule', 'store' or 'other'."""
        if self.point_in_rect(x, y, self.street_rect):
            return "street"
        if self.point_in_rect(x, y, self.vest_rect):
            return "vestibule"
        if self.point_in_rect(x, y, self.store_rect):
            return "store"
        return "other"

    # ------------------
    # Queue / cashier helpers
    # ------------------
    def in_any_queue(self, x: float, y: float) -> str | None:
        """Return queue name if point is inside a queue rectangle, otherwise None."""
        for q in self.queue_rects:
            if self.point_in_rect(x, y, q["rect"]):
                return q["name"]
        return None

    def in_cashier_zone(self, x: float, y: float) -> bool:
        for rect in self.cashier_zone_rects:
            if self.point_in_rect(x, y, rect):
                return True
        return False

    # ------------------
    # Heatmap helpers
    # ------------------
    def cell_index(self, x: float, y: float) -> tuple[int, int] | None:
        """Return (ix, iy) indices of the heatmap cell or None if outside grid."""
        if not (self.grid_min_x <= x <= self.grid_max_x and
                self.grid_min_y <= y <= self.grid_max_y):
            return None
        ix = int((x - self.grid_min_x) / self.cell_w)
        iy = int((y - self.grid_min_y) / self.cell_h)
        # Clamp indices at the border
        ix = max(0, min(self.grid_nx - 1, ix))
        iy = max(0, min(self.grid_ny - 1, iy))
        return ix, iy

    @property
    def zone_areas(self) -> Dict[str, float]:
        """Return precomputed areas of zones in m^2."""
        res = {}
        for name, info in self.zones.items():
            x, y, w, h = info.rect
            res[name] = w * h
        return res
