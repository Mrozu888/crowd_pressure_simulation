from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np


@dataclass(frozen=True)
class Rect:
    x0: float
    y0: float
    x1: float
    y1: float

    def contains(self, p: np.ndarray) -> bool:
        x = float(p[0])
        y = float(p[1])
        return (self.x0 <= x <= self.x1) and (self.y0 <= y <= self.y1)

    def area(self) -> float:
        return max(0.0, self.x1 - self.x0) * max(0.0, self.y1 - self.y0)


@dataclass
class StatsGeometry:
    """World geometry helper for stats.

    Coordinates are in simulation units (same as Environment/Agent).
    """

    store: Rect
    street: Rect
    vestibule: Rect
    queue: Optional[Rect]

    door_segments: List[Tuple[Tuple[float, float], Tuple[float, float]]]

    # Heatmap extents (cover street + store)
    heat_x0: float
    heat_y0: float
    heat_x1: float
    heat_y1: float
    heat_cell: float

    @staticmethod
    def from_environment(env, street_width: float = 3.0, heat_cell: float = 0.25) -> "StatsGeometry":
        width = float(getattr(env, "width", 0.0))
        height = float(getattr(env, "height", 0.0))

        store = Rect(0.0, 0.0, width, height)
        street = Rect(-street_width, 0.0, 0.0, height)

        doors = list(getattr(env, "doors", []) or [])

        # Vestibule near the entrance door (inside store), to preserve a stable 'entry area' metric.
        if doors:
            (x1, y1), (x2, y2) = doors[0]
            mid_y = (float(y1) + float(y2)) / 2.0
        else:
            entrance_pts = getattr(env, "config", {}).get("agent_generation", {}).get("entrance_points", [])
            if entrance_pts:
                mid_y = float(entrance_pts[0][1])
            else:
                mid_y = height * 0.9

        vestibule = Rect(
            0.0,
            max(0.0, mid_y - 1.0),
            min(width, 2.0),
            min(height, mid_y + 1.0),
        )

        # Queue zone: bounding box around QueueManager.queue_slots (if present)
        queue_rect = None
        qm = getattr(env, "queue_manager", None)
        slots = getattr(qm, "queue_slots", None)
        if slots is not None and len(slots) > 0:
            pts = np.asarray(slots, dtype=np.float32)
            x0 = float(np.min(pts[:, 0])) - 0.6
            x1 = float(np.max(pts[:, 0])) + 0.6
            y0 = float(np.min(pts[:, 1])) - 0.6
            y1 = float(np.max(pts[:, 1])) + 0.6
            queue_rect = Rect(max(store.x0, x0), max(store.y0, y0), min(store.x1, x1), min(store.y1, y1))

        heat_x0 = -street_width
        heat_y0 = 0.0
        heat_x1 = width
        heat_y1 = height

        return StatsGeometry(
            store=store,
            street=street,
            vestibule=vestibule,
            queue=queue_rect,
            door_segments=doors,
            heat_x0=heat_x0,
            heat_y0=heat_y0,
            heat_x1=heat_x1,
            heat_y1=heat_y1,
            heat_cell=float(heat_cell),
        )

    def classify(self, pos: np.ndarray) -> str:
        if self.street.contains(pos):
            return "street"
        if self.store.contains(pos):
            if self.queue is not None and self.queue.contains(pos):
                return "queue"
            if self.vestibule.contains(pos):
                return "vestibule"
            return "store"
        return "outside"

    def heatmap_shape(self) -> Tuple[int, int]:
        w = int(np.ceil((self.heat_x1 - self.heat_x0) / self.heat_cell))
        h = int(np.ceil((self.heat_y1 - self.heat_y0) / self.heat_cell))
        return (h, w)

    def heatmap_index(self, pos: np.ndarray) -> Optional[Tuple[int, int]]:
        x = float(pos[0])
        y = float(pos[1])
        if x < self.heat_x0 or x > self.heat_x1 or y < self.heat_y0 or y > self.heat_y1:
            return None
        col = int((x - self.heat_x0) / self.heat_cell)
        row = int((y - self.heat_y0) / self.heat_cell)
        h, w = self.heatmap_shape()
        if 0 <= row < h and 0 <= col < w:
            return (row, col)
        return None

    def heat_cell_center(self, row: int, col: int) -> Tuple[float, float]:
        x = self.heat_x0 + (col + 0.5) * self.heat_cell
        y = self.heat_y0 + (row + 0.5) * self.heat_cell
        return x, y
