"""
Statistics manager (logic).

Collects:
  - per-agent life statistics (times, distances, idle/queue durations),
  - per-frame aggregates (flows, densities, contacts, speeds, queue lengths),
  - heatmap occupancy (time in grid cells).

Integrates with:
  - Agent objects: expected attributes: position (np.ndarray or (x,y)),
    velocity (np.ndarray or (vx,vy)), optional .kind and .covid_compliant and .id.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Iterable, Tuple
from collections import deque
import math
import numpy as np

from .geometry import StatsGeometry
from .writer import StatsCSVWriter, AgentSummaryRow, FrameStatsRow


@dataclass
class AgentRuntimeState:
    """Per-agent evolving state stored inside StatsManager."""
    kind: str
    spawned_at: float
    first_in_vestibule: Optional[float] = None
    first_in_store: Optional[float] = None
    last_in_vestibule: Optional[float] = None
    last_in_store: Optional[float] = None
    total_idle_time: float = 0.0
    total_queue_time: float = 0.0
    total_distance: float = 0.0
    last_pos: Optional[Tuple[float, float]] = None
    covid_compliant: Optional[bool] = None
    last_zone: str = "other"


class StatsManager:
    """
    Central manager for statistics.

    Usage:
      geom = StatsGeometry()
      writer = StatsCSVWriter()
      stats = StatsManager(geom, writer, covid_dist=1.7)

      # each frame
      stats.update(dt, env.agents)

      # HUD can read stats.last_frame_stats
      # Visualization can use stats.crowding_map(env.agents) for coloring.

      # on shutdown
      stats.close()
    """

    def __init__(self,
                 geom: StatsGeometry,
                 writer: Optional[StatsCSVWriter] = None,
                 covid_dist: float = 1.7,
                 idle_speed_thr: float = 0.05) -> None:

        self.geom = geom
        self.writer = writer or StatsCSVWriter(".")
        self.covid_dist = covid_dist
        self.idle_speed_thr = idle_speed_thr

        self.t: float = 0.0

        # id -> AgentRuntimeState
        self._agents: Dict[int, AgentRuntimeState] = {}

        # heatmap (time accumulation in seconds)
        self.heat = np.zeros((geom.grid_ny, geom.grid_nx), dtype=float)

        # flows: sliding window of times for each door
        self._door_windows = {
            "left": deque(),   # street <-> vestibule
            "top": deque(),    # vestibule <-> store
            "right": deque(),  # store <-> vestibule (not used separately yet)
        }
        self.window_len = 60.0  # seconds

        # Per-frame info exposed to HUD
        self.last_frame_stats: Optional[FrameStatsRow] = None

        # For previous frame: mapping id -> zone
        self._prev_zones: Dict[int, str] = {}

    # -------------
    # Utility
    # -------------
    def _get_pos(self, agent) -> Tuple[float, float]:
        p = getattr(agent, "position", getattr(agent, "pos", None))
        if p is None:
            raise AttributeError("Agent has no 'position' or 'pos' attribute")
        return float(p[0]), float(p[1])

    def _get_vel(self, agent) -> Tuple[float, float]:
        v = getattr(agent, "velocity", getattr(agent, "vel", None))
        if v is None:
            return 0.0, 0.0
        return float(v[0]), float(v[1])

    def _get_kind(self, agent) -> str:
        if hasattr(agent, "kind"):
            return str(agent.kind)
        if hasattr(agent, "direction"):
            return str(agent.direction)
        return "unknown"

    def _get_covid_flag(self, agent) -> Optional[bool]:
        if hasattr(agent, "covid_compliant"):
            return bool(agent.covid_compliant)
        if hasattr(agent, "covid_aware"):
            return bool(agent.covid_aware)
        return None

    # -------------
    # Public API
    # -------------
    def update(self, dt: float, agents: Iterable) -> None:
        """
        Update statistics for one simulation step.

        This method:
          - advances global time,
          - detects new/removed agents,
          - updates per-agent times and distances,
          - tracks zone transitions, flows, queue occupancy,
          - writes one frame row to CSV.
        """
        self.t += dt

        agents_list = list(agents)
        current_ids = set()

        # Update or create runtime state per agent
        for a in agents_list:
            if not hasattr(a, "id"):
                # Without a stable id we cannot track per-agent stats
                continue

            aid = int(a.id)
            current_ids.add(aid)
            x, y = self._get_pos(a)
            vx, vy = self._get_vel(a)
            speed = math.hypot(vx, vy)
            zone = self.geom.classify_zone(x, y)

            if aid not in self._agents:
                # New agent
                st = AgentRuntimeState(
                    kind=self._get_kind(a),
                    spawned_at=self.t,
                    covid_compliant=self._get_covid_flag(a),
                    last_zone=zone,
                    last_pos=(x, y),
                )
                self._agents[aid] = st
            else:
                st = self._agents[aid]

            # Distance travelled
            if st.last_pos is not None:
                dx = x - st.last_pos[0]
                dy = y - st.last_pos[1]
                st.total_distance += math.hypot(dx, dy)
            st.last_pos = (x, y)

            # Idle time
            if speed < self.idle_speed_thr:
                st.total_idle_time += dt

            # Queue time
            if self.geom.in_any_queue(x, y) is not None:
                st.total_queue_time += dt

            # Zone timings
            if zone == "vestibule":
                st.last_in_vestibule = self.t
                if st.first_in_vestibule is None:
                    st.first_in_vestibule = self.t
            elif zone == "store":
                st.last_in_store = self.t
                if st.first_in_store is None:
                    st.first_in_store = self.t

            # Heatmap integration
            cell = self.geom.cell_index(x, y)
            if cell is not None:
                ix, iy = cell
                self.heat[iy, ix] += dt

            # Door crossings via zone change
            prev_zone = self._prev_zones.get(aid, zone)
            if prev_zone != zone:
                self._handle_zone_transition(prev_zone, zone)
            self._prev_zones[aid] = zone

        # Detect removed agents
        gone_ids = [aid for aid in self._agents.keys() if aid not in current_ids]
        for aid in gone_ids:
            self._finalize_agent(aid)
            self._agents.pop(aid, None)
            self._prev_zones.pop(aid, None)

        # Per-frame aggregates
        self._update_flows_window()
        self._write_frame_row(agents_list)

    def close(self) -> None:
        """Flush and close CSV files."""
        self.writer.flush()
        self.writer.close()

    # -------------
    # Crowd coloring helper
    # -------------
    def crowding_map(self,
                     agents: Iterable,
                     low_threshold: int = 3,
                     high_threshold: int = 6) -> Dict[int, int]:
        """
        Compute crowding level per agent based on how many agents are in the
        same heatmap cell.

        Returns dict: agent_id -> level, where:
          0 = low density (normal color)
          1 = medium density (yellow)
          2 = high density (red)

        Thresholds:
          - if count < low_threshold   -> 0
          - if low_threshold <= count < high_threshold -> 1
          - if count >= high_threshold -> 2
        """
        # Count agents per grid cell
        cell_counts: Dict[Tuple[int, int], int] = {}
        cell_by_id: Dict[int, Tuple[int, int]] = {}

        for a in agents:
            if not hasattr(a, "id"):
                continue
            aid = int(a.id)
            x, y = self._get_pos(a)
            cell = self.geom.cell_index(x, y)
            if cell is None:
                continue
            cell_by_id[aid] = cell
            cell_counts[cell] = cell_counts.get(cell, 0) + 1

        levels: Dict[int, int] = {}
        for aid, cell in cell_by_id.items():
            c = cell_counts.get(cell, 0)
            if c < low_threshold:
                levels[aid] = 0
            elif c < high_threshold:
                levels[aid] = 1
            else:
                levels[aid] = 2
        return levels

    # -------------
    # Internal helpers
    # -------------
    def _handle_zone_transition(self, prev_zone: str, zone: str) -> None:
        """
        Register transitions for flow counters.

        We interpret:
          street <-> vestibule  -> left door
          vestibule <-> store   -> top door (aggregated).
        """
        t = self.t

        def push(door_name: str):
            self._door_windows[door_name].append(t)

        # Left door: street <-> vestibule
        if ((prev_zone == "street" and zone == "vestibule") or
            (prev_zone == "vestibule" and zone == "street")):
            push("left")

        # Vestibule <-> store: counted as "top" door for now
        if ((prev_zone == "vestibule" and zone == "store") or
            (prev_zone == "store" and zone == "vestibule")):
            push("top")

    def _update_flows_window(self) -> Dict[str, float]:
        """
        Remove old events from door windows and compute flows in people/min.
        """
        flows = {}
        t0 = self.t - self.window_len
        for name, dq in self._door_windows.items():
            while dq and dq[0] < t0:
                dq.popleft()
            flows[name] = len(dq) / (self.window_len / 60.0)
        return flows

    def _finalize_agent(self, aid: int) -> None:
        """Compute agent summary and write one CSV row."""
        st = self._agents[aid]

        time_to_enter_store = None
        time_in_store = None
        time_in_vest = None

        if st.first_in_store is not None and st.spawned_at is not None:
            time_to_enter_store = st.first_in_store - st.spawned_at
        if st.first_in_store is not None and st.last_in_store is not None:
            time_in_store = st.last_in_store - st.first_in_store
        if st.first_in_vestibule is not None and st.last_in_vestibule is not None:
            time_in_vest = st.last_in_vestibule - st.first_in_vestibule

        row = AgentSummaryRow(
            agent_id=aid,
            kind=st.kind,
            spawned_at=st.spawned_at,
            first_in_vestibule=st.first_in_vestibule,
            first_in_store=st.first_in_store,
            last_in_vestibule=st.last_in_vestibule,
            last_in_store=st.last_in_store,
            time_to_enter_store=time_to_enter_store,
            time_in_store=time_in_store,
            time_in_vestibule=time_in_vest,
            total_idle_time=st.total_idle_time,
            total_queue_time=st.total_queue_time,
            total_distance=st.total_distance,
            covid_compliant=st.covid_compliant,
        )
        self.writer.write_agent_row(row)

    def _write_frame_row(self, agents: List) -> None:
        """Compute per-frame aggregates and write stats_frames.csv row."""
        geom = self.geom
        zones = {"street": 0, "vestibule": 0, "store": 0}
        speeds = []
        speeds_store = []
        speeds_vest = []

        queue_counts = {"front_cashiers_queue": 0}
        contacts_lt_1 = 0
        contacts_lt_covid = 0

        positions = []
        for a in agents:
            if not hasattr(a, "id"):
                continue
            x, y = self._get_pos(a)
            vx, vy = self._get_vel(a)
            v = math.hypot(vx, vy)
            zone = geom.classify_zone(x, y)
            if zone in zones:
                zones[zone] += 1
            speeds.append(v)
            if zone == "store":
                speeds_store.append(v)
            elif zone == "vestibule":
                speeds_vest.append(v)

            qname = geom.in_any_queue(x, y)
            if qname is not None:
                queue_counts[qname] += 1

            positions.append((x, y))

        # Contacts
        n = len(positions)
        for i in range(n):
            xi, yi = positions[i]
            for j in range(i + 1, n):
                xj, yj = positions[j]
                d = math.hypot(xi - xj, yi - yj)
                if d < 1.0:
                    contacts_lt_1 += 1
                if d < self.covid_dist:
                    contacts_lt_covid += 1

        flows = self._update_flows_window()
        areas = geom.zone_areas

        density_store = zones["store"] / areas["store"] if areas["store"] > 0 else 0.0
        density_vest = zones["vestibule"] / areas["vestibule"] if areas["vestibule"] > 0 else 0.0

        avg_speed = float(sum(speeds) / len(speeds)) if speeds else 0.0
        avg_speed_store = float(sum(speeds_store) / len(speeds_store)) if speeds_store else 0.0
        avg_speed_vest = float(sum(speeds_vest) / len(speeds_vest)) if speeds_vest else 0.0

        row = FrameStatsRow(
            t=self.t,
            n_agents=len(positions),
            n_in_store=zones["store"],
            n_in_vestibule=zones["vestibule"],
            n_in_street=zones["street"],
            flow_left_door_per_min=flows["left"],
            flow_top_door_per_min=flows["top"],
            flow_right_door_per_min=flows["right"],
            contacts_lt_1m=contacts_lt_1,
            contacts_lt_covid=contacts_lt_covid,
            avg_speed=avg_speed,
            avg_speed_store=avg_speed_store,
            avg_speed_vestibule=avg_speed_vest,
            queue_front_cashiers=queue_counts["front_cashiers_queue"],
            density_store=density_store,
            density_vestibule=density_vest,
        )

        self.writer.write_frame_row(row)
        self.last_frame_stats = row
