from __future__ import annotations

from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional

import numpy as np
from collections import deque

from .geometry import StatsGeometry
from .writer import StatsWriter


@dataclass
class _AgentState:
    agent_id: int
    activated_at: float
    spawn_time: float

    last_pos: Optional[np.ndarray] = None
    dist: float = 0.0

    idle_time: float = 0.0
    queue_time: float = 0.0

    zone: str = "outside"
    pending_zone: Optional[str] = None
    pending_since: float = 0.0

    zone_durations: Dict[str, float] = field(default_factory=dict)

    exited: bool = False
    exit_time: Optional[float] = None

    speed_sum: float = 0.0
    speed_samples: int = 0


class StatsManager:
    """Collects per-frame and per-agent statistics."""

    def __init__(
        self,
        geom: StatsGeometry,
        writer: StatsWriter,
        zone_debounce_s: float = 0.30,
        idle_speed_thresh: float = 0.05,
        history_seconds: float = 120.0,
    ):
        self.geom = geom
        self.writer = writer

        self.zone_debounce_s = float(zone_debounce_s)
        self.idle_speed_thresh = float(idle_speed_thresh)

        self._agents: Dict[int, _AgentState] = {}
        self._heatmap = np.zeros(self.geom.heatmap_shape(), dtype=np.float32)

        self._entries_total = 0
        self._exits_total = 0

        self.last_frame: Dict = {}

        self._hist_t: Deque[float] = deque()
        self._hist_entry_rate: Deque[float] = deque()
        self._hist_exit_rate: Deque[float] = deque()
        self._hist_queue_len: Deque[float] = deque()
        self._hist_inside: Deque[float] = deque()
        self._hist_density: Deque[float] = deque()
        self._history_seconds = float(history_seconds)

        self._live_hotspots: List[Dict] = []
        self._last_hotspot_update_t: float = -1e9

    @property
    def heatmap(self) -> np.ndarray:
        return self._heatmap

    def live_hotspots(self) -> List[Dict]:
        return self._live_hotspots

    def _get_state(self, agent, sim_time: float) -> _AgentState:
        aid = id(agent)
        st = self._agents.get(aid)
        if st is None:
            st = _AgentState(
                agent_id=aid,
                activated_at=float(sim_time),
                spawn_time=float(getattr(agent, "spawn_time", 0.0)),
            )
            self._agents[aid] = st
        return st

    def _push_hist(self, t: float, entry_rate: float, exit_rate: float, queue_len: float, inside: float, density: float):
        self._hist_t.append(t)
        self._hist_entry_rate.append(entry_rate)
        self._hist_exit_rate.append(exit_rate)
        self._hist_queue_len.append(queue_len)
        self._hist_inside.append(inside)
        self._hist_density.append(density)

        tmin = t - self._history_seconds
        while self._hist_t and self._hist_t[0] < tmin:
            self._hist_t.popleft()
            self._hist_entry_rate.popleft()
            self._hist_exit_rate.popleft()
            self._hist_queue_len.popleft()
            self._hist_inside.popleft()
            self._hist_density.popleft()

    def history(self) -> Dict[str, List[float]]:
        return {
            "time": list(self._hist_t),
            "entry_rate": list(self._hist_entry_rate),
            "exit_rate": list(self._hist_exit_rate),
            "queue_len": list(self._hist_queue_len),
            "inside": list(self._hist_inside),
            "density": list(self._hist_density),
        }

    def update(self, dt: float, sim_time: float, agents, env=None):
        dt = float(dt)
        sim_time = float(sim_time)

        entries_step = 0
        exits_step = 0

        n_active = 0
        zone_counts = {"street": 0, "vestibule": 0, "store": 0, "queue": 0, "outside": 0}
        speed_sum = 0.0
        speed_n = 0

        for agent in agents:
            if not getattr(agent, "active", True):
                continue

            n_active += 1
            st = self._get_state(agent, sim_time)

            pos = np.asarray(getattr(agent, "position"), dtype=np.float32)
            vel = np.asarray(getattr(agent, "velocity"), dtype=np.float32)
            spd = float(np.linalg.norm(vel))
            st.speed_sum += spd
            st.speed_samples += 1

            speed_sum += spd
            speed_n += 1

            if st.last_pos is not None:
                st.dist += float(np.linalg.norm(pos - st.last_pos))
            st.last_pos = pos

            if spd < self.idle_speed_thresh:
                st.idle_time += dt

            z = self.geom.classify(pos)
            zone_counts[z] = zone_counts.get(z, 0) + 1

            if z != st.zone:
                if st.pending_zone != z:
                    st.pending_zone = z
                    st.pending_since = sim_time
                else:
                    if (sim_time - st.pending_since) >= self.zone_debounce_s:
                        prev = st.zone
                        st.zone = z
                        st.pending_zone = None
                        if prev == "street" and z in ("vestibule", "store", "queue"):
                            entries_step += 1
                            self._entries_total += 1
            else:
                st.pending_zone = None

            st.zone_durations[st.zone] = st.zone_durations.get(st.zone, 0.0) + dt
            if st.zone == "queue":
                st.queue_time += dt

            idx = self.geom.heatmap_index(pos)
            if idx is not None:
                self._heatmap[idx] += dt

            if getattr(agent, "exited", False) and not st.exited:
                st.exited = True
                st.exit_time = sim_time
                exits_step += 1
                self._exits_total += 1
                self._write_agent_row(st)

        queue_len = 0
        service_n = 0
        if env is not None and hasattr(env, "queue_manager"):
            qm = env.queue_manager
            queue_len = int(len(getattr(qm, "queue", []) or []))
            cashiers = getattr(qm, "cashiers", []) or []
            service_n = sum(1 for c in cashiers if c.get("agent") is not None)

        store_area = self.geom.store.area() if self.geom.store is not None else 0.0
        inside_now = zone_counts.get("store", 0) + zone_counts.get("vestibule", 0) + zone_counts.get("queue", 0)
        density_store = (inside_now / store_area) if store_area > 0 else 0.0

        avg_speed = (speed_sum / speed_n) if speed_n > 0 else 0.0

        entry_rate = (entries_step / dt) if dt > 0 else 0.0
        exit_rate = (exits_step / dt) if dt > 0 else 0.0

        inside_est = float(self._entries_total - self._exits_total)

        frame = {
            "time": sim_time,
            "dt": dt,
            "n_active": n_active,
            "n_street": zone_counts.get("street", 0),
            "n_vestibule": zone_counts.get("vestibule", 0),
            "n_store": zone_counts.get("store", 0),
            "n_queue_zone": zone_counts.get("queue", 0),
            "inside_now": inside_now,
            "inside_est": inside_est,
            "queue_len": queue_len,
            "service_n": service_n,
            "entries_step": entries_step,
            "exits_step": exits_step,
            "entries_total": self._entries_total,
            "exits_total": self._exits_total,
            "entry_rate_s": entry_rate,
            "exit_rate_s": exit_rate,
            "avg_speed": avg_speed,
            "density_store": density_store,
        }

        self.last_frame = frame
        self.writer.write_frame(frame)

        self._push_hist(sim_time, entry_rate, exit_rate, float(queue_len), inside_est, density_store)

        if sim_time - self._last_hotspot_update_t >= 1.0:
            self._live_hotspots = self._compute_hotspots(top_k=40)
            self._last_hotspot_update_t = sim_time

    def _write_agent_row(self, st: _AgentState):
        exit_time = float(st.exit_time) if st.exit_time is not None else None
        travel_time = (exit_time - st.activated_at) if exit_time is not None else None
        mean_speed = (st.speed_sum / st.speed_samples) if st.speed_samples > 0 else 0.0

        row = {
            "agent_id": st.agent_id,
            "spawn_time": st.spawn_time,
            "activated_at": st.activated_at,
            "exit_time": exit_time,
            "travel_time": travel_time,
            "distance": st.dist,
            "mean_speed": mean_speed,
            "idle_time": st.idle_time,
            "queue_time": st.queue_time,
            "time_street": st.zone_durations.get("street", 0.0),
            "time_vestibule": st.zone_durations.get("vestibule", 0.0),
            "time_store": st.zone_durations.get("store", 0.0),
            "time_queue": st.zone_durations.get("queue", 0.0),
        }
        self.writer.write_agent(row)

    def close(self):
        for st in list(self._agents.values()):
            if st.exited and st.exit_time is not None:
                continue
            row = {
                "agent_id": st.agent_id,
                "spawn_time": st.spawn_time,
                "activated_at": st.activated_at,
                "exit_time": st.exit_time,
                "travel_time": (st.exit_time - st.activated_at) if st.exit_time is not None else None,
                "distance": st.dist,
                "mean_speed": (st.speed_sum / st.speed_samples) if st.speed_samples > 0 else 0.0,
                "idle_time": st.idle_time,
                "queue_time": st.queue_time,
                "time_street": st.zone_durations.get("street", 0.0),
                "time_vestibule": st.zone_durations.get("vestibule", 0.0),
                "time_store": st.zone_durations.get("store", 0.0),
                "time_queue": st.zone_durations.get("queue", 0.0),
            }
            self.writer.write_agent(row)

        self.writer.save_heatmap(self._heatmap, self.geom.heat_x0, self.geom.heat_y0, self.geom.heat_cell)
        self.writer.save_hotspots(self._compute_hotspots(top_k=25))
        self.writer.close()

    def _compute_hotspots(self, top_k: int = 25) -> List[Dict]:
        hm = self._heatmap
        if hm.size == 0:
            return []
        flat = hm.ravel()
        if np.all(flat <= 0):
            return []

        top_k = int(min(top_k, flat.size))
        idxs = np.argpartition(flat, -top_k)[-top_k:]
        idxs = idxs[np.argsort(flat[idxs])[::-1]]

        rows, cols = hm.shape
        out: List[Dict] = []
        for rank, flat_idx in enumerate(idxs, start=1):
            r = int(flat_idx // cols)
            c = int(flat_idx % cols)
            val = float(hm[r, c])
            x, y = self.geom.heat_cell_center(r, c)
            out.append(
                {"rank": rank, "person_seconds": val, "cell_row": r, "cell_col": c, "x": x, "y": y}
            )
        return out
