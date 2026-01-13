from __future__ import annotations

from dataclasses import dataclass, field
from typing import Deque, Dict, Optional, Tuple

from collections import deque
import numpy as np

from .geometry import StatsGeometry
from .writer import StatsWriter


@dataclass
class _AgentState:
    agent_id: int
    spawn_time: float

    entry_time: Optional[float] = None  # first time inside store
    exit_time: Optional[float] = None   # when agent.exited becomes True

    inside_at_entry: Optional[int] = None  # number of people inside at entry moment

    last_pos: Optional[np.ndarray] = None
    distance: float = 0.0

    idle_time: float = 0.0
    mean_speed_sum: float = 0.0
    mean_speed_n: int = 0

    zone: str = "outside"


class StatsManager:
    """Collects statistics without changing simulation behavior.

    Terminology (used in different versions of the UI):
    - Flow rate = speed of entering/exiting (e.g., agents per minute). Not shown in HUD now.
    - Inside (est.) = entries_total - exits_total (balance estimate), can drift if entry/exit are defined differently.
    - serving_now (aka service_n) = number of cashiers currently serving an agent.

    Key metrics used in current UI/CSV:
    - inside_now: how many agents are currently inside store zones (vestibule/store/queue).
    - total_entered: how many unique agents crossed from outside to inside (entry_time set).
    - exited_total: how many agents finished and left (agent.exited).
    """

    def __init__(
        self,
        geom: StatsGeometry,
        writer: StatsWriter,
        *,
        real_seconds_per_sim_second: float = 10.0,
        history_seconds: float = 240.0,
        keep_shopping_points: int = 800,
        idle_speed_thresh: float = 0.05,
    ):
        self.geom = geom
        self.writer = writer
        self.real_seconds_per_sim_second = float(real_seconds_per_sim_second)

        self.idle_speed_thresh = float(idle_speed_thresh)

        self._agents: Dict[int, _AgentState] = {}

        # Totals
        self.entries_total = 0
        self.exits_total = 0

        # Live frame snapshot for HUD
        self.last_frame: Dict = {}

        # History for HUD graphs
        self.history_seconds = float(history_seconds)
        self.t_hist: Deque[float] = deque()
        self.inside_hist: Deque[int] = deque()
        self.density_hist: Deque[float] = deque()
        self.queue_total_hist: Deque[int] = deque()
        self.serving_now_hist: Deque[int] = deque()
        self.serving_median_hist: Deque[float] = deque()
        self.max_queue_hist: Deque[int] = deque()

        # Shopping time points (time series by exit time)
        self.keep_shopping_points = int(keep_shopping_points)
        self.shop_exit_t: Deque[float] = deque()
        self.shop_time_min: Deque[float] = deque()
        # Median of shopping time over all completed agents so far (aligned with shop_exit_t)
        self.shop_median_min: Deque[float] = deque()
        # Keep all completed times for true global median (do not trim)
        self._all_shop_time_min: list[float] = []

        # Keep all serving_now values for global median line
        self._all_serving_now: list[int] = []

        # Heatmap (optional)
        self._heatmap = np.zeros(self.geom.heatmap_shape(), dtype=np.float32)

    @property
    def heatmap(self) -> np.ndarray:
        return self._heatmap

    def _get_state(self, agent) -> _AgentState:
        aid = id(agent)
        st = self._agents.get(aid)
        if st is None:
            st = _AgentState(agent_id=aid, spawn_time=float(getattr(agent, "spawn_time", 0.0)))
            self._agents[aid] = st
        return st

    def _trim_history(self, now: float):
        limit = now - self.history_seconds
        while self.t_hist and self.t_hist[0] < limit:
            self.t_hist.popleft()
            self.inside_hist.popleft()
            self.density_hist.popleft()
            self.queue_total_hist.popleft()
            self.serving_now_hist.popleft()
            self.serving_median_hist.popleft()
            self.max_queue_hist.popleft()

    def _queue_metrics(self, env) -> Tuple[int, int, int]:
        """queue_total, serving_now, max_queue.

        queue_total: waiting agents (not including those being served).
        serving_now: number of busy cashiers (cashier.agent is not None).
        max_queue: max queue length among cashiers. If model uses a single shared queue, max_queue=len(queue).
        """
        qm = getattr(env, "queue_manager", None)
        if qm is None:
            return 0, 0, 0

        queue = getattr(qm, "queue", []) or []
        queue_total = int(len(queue))

        cashiers = getattr(qm, "cashiers", []) or []
        serving_now = 0
        agent_phase = getattr(qm, "agent_phase", {}) or {}
        for c in cashiers:
            a = c.get("agent")
            if a is None:
                continue
            # Count only agents that are actually being served: they reached the cashier
            # and are currently waiting there for service_time.
            if agent_phase.get(a) == "to_cashier" and getattr(a, "is_waiting", False):
                serving_now += 1

        # This project uses a single shared physical queue.
        # For HUD/plots we expose a proxy "max_queue" as an estimate of the
        # longest per-cashier waiting line if the shared queue were split evenly.
        n_cashiers = len(cashiers) if cashiers else 0
        if n_cashiers > 0:
            max_queue = int((queue_total + n_cashiers - 1) // n_cashiers)  # ceil
        else:
            max_queue = queue_total

        return queue_total, serving_now, max_queue

    def update(self, dt: float, sim_time: float, agents, env=None):
        dt = float(dt)
        sim_time = float(sim_time)
        if env is None:
            return

        # Count inside_now first (only active and not exited)
        inside_now = 0
        for a in agents:
            if getattr(a, "exited", False):
                continue
            if not getattr(a, "active", True):
                continue
            z = self.geom.classify(np.asarray(a.position, dtype=np.float32))
            if z in ("vestibule", "store", "queue"):
                inside_now += 1

        store_area = self.geom.store.area() if self.geom.store is not None else 0.0
        density_store = (inside_now / store_area) if store_area > 0 else 0.0

        queue_total, serving_now, max_queue = self._queue_metrics(env)

        # Keep history of "serving_now" (busy cashiers right now) + its global median.
        # This is separate from the shopping-time median.
        self._all_serving_now.append(int(serving_now))
        serving_med = float(np.median(np.asarray(self._all_serving_now, dtype=np.float32))) if self._all_serving_now else 0.0

        # Per-agent updates (entry/exit + movement)
        for a in agents:
            st = self._get_state(a)

            # Update movement only for active agents
            if getattr(a, "active", True) and not getattr(a, "exited", False):
                pos = np.asarray(a.position, dtype=np.float32)
                vel = np.asarray(getattr(a, "velocity", (0.0, 0.0)), dtype=np.float32)
                spd = float(np.linalg.norm(vel))

                if st.last_pos is not None:
                    st.distance += float(np.linalg.norm(pos - st.last_pos))
                st.last_pos = pos

                if spd < self.idle_speed_thresh:
                    st.idle_time += dt
                st.mean_speed_sum += spd
                st.mean_speed_n += 1

                st.zone = self.geom.classify(pos)

                # Entry time: first moment agent is inside store zones
                if st.entry_time is None and st.zone in ("vestibule", "store", "queue"):
                    st.entry_time = sim_time
                    st.inside_at_entry = int(inside_now)
                    self.entries_total += 1

                    # Track heatmap
                idx = self.geom.heatmap_index(pos)
                if idx is not None:
                    self._heatmap[idx] += dt

            # Exit time: agent finished and left
            if getattr(a, "exited", False) and st.exit_time is None:
                st.exit_time = sim_time
                self.exits_total += 1

                # Shopping time requires entry_time
                if st.entry_time is not None and st.exit_time >= st.entry_time:
                    shop_s = float(st.exit_time - st.entry_time)
                    shop_min = shop_s / 60.0

                    # Global median across ALL completed agents from the beginning.
                    self._all_shop_time_min.append(float(shop_min))
                    cur_med = float(np.median(np.asarray(self._all_shop_time_min, dtype=np.float32)))

                    # Store time series point
                    self.shop_exit_t.append(float(st.exit_time))
                    self.shop_time_min.append(float(shop_min))
                    self.shop_median_min.append(float(cur_med))
                    while len(self.shop_exit_t) > self.keep_shopping_points:
                        self.shop_exit_t.popleft()
                        self.shop_time_min.popleft()
                        self.shop_median_min.popleft()

                    # Write per-agent row
                self.writer.write_agent(
                    {
                        "agent_id": st.agent_id,
                        "spawn_time": st.spawn_time,
                        "entry_time": st.entry_time,
                        "exit_time": st.exit_time,
                        "shopping_time_s": (st.exit_time - st.entry_time) if st.entry_time is not None else None,
                        "shopping_time_min": ((st.exit_time - st.entry_time) / 60.0) if st.entry_time is not None else None,
                        "inside_at_entry": st.inside_at_entry,
                        "distance": st.distance,
                        "idle_time": st.idle_time,
                        "mean_speed": (st.mean_speed_sum / st.mean_speed_n) if st.mean_speed_n > 0 else 0.0,
                    }
                )

        # Median shopping time (minutes) among completed agents so far
        # Median shopping time in minutes across all completed agents so far
        median_shop = float(np.median(np.asarray(self._all_shop_time_min, dtype=np.float32))) if self._all_shop_time_min else None

        # Save frame row + history
        self.t_hist.append(sim_time)
        self.inside_hist.append(int(inside_now))
        self.density_hist.append(float(density_store))
        self.queue_total_hist.append(int(queue_total))
        self.serving_now_hist.append(int(serving_now))
        self.serving_median_hist.append(float(serving_med))
        self.max_queue_hist.append(int(max_queue))

        self._trim_history(sim_time)

        self.last_frame = {
            "time": sim_time,
            "dt": dt,
            "inside_now": int(inside_now),
            "total_entered": int(self.entries_total),
            "exited_total": int(self.exits_total),
            "density_store": float(density_store),
            "queue_total": int(queue_total),
            "serving_now": int(serving_now),
            "serving_median": float(serving_med),
            "max_queue": int(max_queue),
            "shopping_median_min": median_shop,
        }

        # Persist frame to CSV
        self.writer.write_frame(self.last_frame)

    def close(self):
        # Save heatmap on close for offline analysis
        self.writer.save_heatmap(self._heatmap, self.geom.heat_x0, self.geom.heat_y0, self.geom.heat_cell)
        # Save PNG plots with axes and legend (for reports)
        try:
            from .plots import save_all_plots

            save_all_plots(self, self.writer.base_dir)
        except Exception:
            pass
        self.writer.close()
