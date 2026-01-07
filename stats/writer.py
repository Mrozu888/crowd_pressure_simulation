from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np


@dataclass
class StatsPaths:
    base_dir: str
    frames_csv: str
    agents_csv: str
    heatmap_npy: str
    heatmap_csv: str
    hotspots_csv: str


class StatsWriter:
    """Writes simulation statistics to CSV/NPY."""

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_dir = os.path.join("stats_output", stamp)

        os.makedirs(base_dir, exist_ok=True)

        self.paths = StatsPaths(
            base_dir=base_dir,
            frames_csv=os.path.join(base_dir, "stats_frames.csv"),
            agents_csv=os.path.join(base_dir, "stats_agents.csv"),
            heatmap_npy=os.path.join(base_dir, "stats_heatmap.npy"),
            heatmap_csv=os.path.join(base_dir, "stats_heatmap.csv"),
            hotspots_csv=os.path.join(base_dir, "stats_hotspots.csv"),
        )

        self._frames_f = open(self.paths.frames_csv, "w", newline="", encoding="utf-8")
        self._agents_f = open(self.paths.agents_csv, "w", newline="", encoding="utf-8")

        self._frames_writer = None
        self._agents_writer = None

    @property
    def base_dir(self) -> str:
        return self.paths.base_dir

    def write_frame(self, row: Dict):
        if self._frames_writer is None:
            fieldnames = list(row.keys())
            self._frames_writer = csv.DictWriter(self._frames_f, fieldnames=fieldnames)
            self._frames_writer.writeheader()
        self._frames_writer.writerow(row)
        self._frames_f.flush()

    def write_agent(self, row: Dict):
        if self._agents_writer is None:
            fieldnames = list(row.keys())
            self._agents_writer = csv.DictWriter(self._agents_f, fieldnames=fieldnames)
            self._agents_writer.writeheader()
        self._agents_writer.writerow(row)
        self._agents_f.flush()

    def save_heatmap(self, heatmap: np.ndarray, heat_x0: float, heat_y0: float, heat_cell: float):
        np.save(self.paths.heatmap_npy, heatmap)

        with open(self.paths.heatmap_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["heat_x0", heat_x0])
            w.writerow(["heat_y0", heat_y0])
            w.writerow(["heat_cell", heat_cell])
            w.writerow(["rows", heatmap.shape[0]])
            w.writerow(["cols", heatmap.shape[1]])
            w.writerow([])
            for r in range(heatmap.shape[0]):
                w.writerow([float(x) for x in heatmap[r, :]])

    def save_hotspots(self, hotspots: List[Dict]):
        if not hotspots:
            return
        with open(self.paths.hotspots_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(hotspots[0].keys()))
            w.writeheader()
            for row in hotspots:
                w.writerow(row)

    def close(self):
        try:
            self._frames_f.close()
        finally:
            self._agents_f.close()
