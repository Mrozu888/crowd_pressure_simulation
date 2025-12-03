"""
CSV writers for statistics.

This module exposes a small wrapper class responsible for opening CSV files,
writing header rows, and appending frame-level and agent-level statistics.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
import csv
import pathlib


@dataclass
class AgentSummaryRow:
    agent_id: int
    kind: str
    spawned_at: float
    first_in_vestibule: Optional[float]
    first_in_store: Optional[float]
    last_in_vestibule: Optional[float]
    last_in_store: Optional[float]
    time_to_enter_store: Optional[float]
    time_in_store: Optional[float]
    time_in_vestibule: Optional[float]
    total_idle_time: float
    total_queue_time: float
    total_distance: float
    covid_compliant: Optional[bool]


@dataclass
class FrameStatsRow:
    t: float
    n_agents: int
    n_in_store: int
    n_in_vestibule: int
    n_in_street: int
    flow_left_door_per_min: float
    flow_top_door_per_min: float
    flow_right_door_per_min: float
    contacts_lt_1m: int
    contacts_lt_covid: int
    avg_speed: float
    avg_speed_store: float
    avg_speed_vestibule: float
    queue_front_cashiers: int
    density_store: float
    density_vestibule: float


class StatsCSVWriter:
    """
    Simple CSV writer wrapper. It owns two files:
      - stats_agents.csv
      - stats_frames.csv
    """

    def __init__(self, base_dir: str | pathlib.Path = ".") -> None:
        base_dir = pathlib.Path(base_dir)
        base_dir.mkdir(parents=True, exist_ok=True)

        self._f_agents = (base_dir / "stats_agents.csv").open("w", newline="", encoding="utf-8")
        self._f_frames = (base_dir / "stats_frames.csv").open("w", newline="", encoding="utf-8")

        self._w_agents = csv.DictWriter(self._f_agents, fieldnames=list(AgentSummaryRow.__annotations__.keys()))
        self._w_frames = csv.DictWriter(self._f_frames, fieldnames=list(FrameStatsRow.__annotations__.keys()))

        self._w_agents.writeheader()
        self._w_frames.writeheader()

    def write_agent_row(self, row: AgentSummaryRow) -> None:
        self._w_agents.writerow(asdict(row))

    def write_frame_row(self, row: FrameStatsRow) -> None:
        self._w_frames.writerow(asdict(row))

    def flush(self) -> None:
        self._f_agents.flush()
        self._f_frames.flush()

    def close(self) -> None:
        self._f_agents.close()
        self._f_frames.close()
