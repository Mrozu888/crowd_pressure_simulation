from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class RealDataSeries:
    """Holds real-world measurements for comparison."""

    times: List[float]
    columns: Dict[str, List[float]]

    @staticmethod
    def load_csv(path: str, time_col: str = "time_s", column_map: Optional[Dict[str, str]] = None) -> "RealDataSeries":
        if column_map is None:
            column_map = {}

        times: List[float] = []
        cols: Dict[str, List[float]] = {}

        with open(path, "r", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                if time_col not in row or row[time_col] is None or row[time_col] == "":
                    continue
                t = float(row[time_col])
                times.append(t)

                for out_name, csv_name in column_map.items():
                    if csv_name not in row or row[csv_name] is None or row[csv_name] == "":
                        continue
                    cols.setdefault(out_name, []).append(float(row[csv_name]))

        for k, v in cols.items():
            if len(v) < len(times) and len(v) > 0:
                last = v[-1]
                v.extend([last] * (len(times) - len(v)))
            elif len(v) == 0:
                cols[k] = [0.0] * len(times)

        return RealDataSeries(times=times, columns=cols)

    def has(self, key: str) -> bool:
        return key in self.columns and len(self.columns[key]) == len(self.times)

    def value_at(self, key: str, t: float) -> Optional[float]:
        if not self.has(key) or not self.times:
            return None

        lo, hi = 0, len(self.times) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if self.times[mid] < t:
                lo = mid + 1
            else:
                hi = mid
        i = lo
        if i > 0 and abs(self.times[i - 1] - t) <= abs(self.times[i] - t):
            i = i - 1
        return self.columns[key][i]

    def window(self, key: str, t0: float, t1: float) -> Tuple[List[float], List[float]]:
        if not self.has(key) or not self.times:
            return [], []
        xs: List[float] = []
        ys: List[float] = []
        for tt, vv in zip(self.times, self.columns[key]):
            if t0 <= tt <= t1:
                xs.append(tt)
                ys.append(vv)
        return xs, ys
