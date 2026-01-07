from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, List

import pygame

from .real_data import RealDataSeries


@dataclass
class HUDToggles:
    show_hud: bool = True
    show_graphs: bool = True
    show_hotspots: bool = False
    show_real: bool = True


class StatsHUD:
    """Draws live stats overlay (text + small time-series charts) on the Pygame screen."""

    def __init__(
        self,
        font: pygame.font.Font,
        small_font: Optional[pygame.font.Font] = None,
        toggles: Optional[HUDToggles] = None,
        real_data: Optional[RealDataSeries] = None,
    ):
        self.font = font
        self.small_font = small_font or font
        self.toggles = toggles or HUDToggles()
        self.real_data = real_data

    def handle_key(self, key: int):
        if key == pygame.K_F1:
            self.toggles.show_hud = not self.toggles.show_hud
        elif key == pygame.K_g:
            self.toggles.show_graphs = not self.toggles.show_graphs
        elif key == pygame.K_h:
            self.toggles.show_hotspots = not self.toggles.show_hotspots
        elif key == pygame.K_r:
            self.toggles.show_real = not self.toggles.show_real

    def draw(self, screen: pygame.Surface, vis, stats_manager, sim_time: float):
        lf = getattr(stats_manager, "last_frame", None) or {}

        if self.toggles.show_hotspots:
            self._draw_hotspots(screen, vis, stats_manager)

        if not self.toggles.show_hud or not lf:
            return

        lines = self._format_lines(lf, sim_time)
        self._draw_text_panel(screen, lines, (10, 40))

        if not self.toggles.show_graphs:
            return

        hist = stats_manager.history()
        w, h = screen.get_size()
        panel_w = 360
        x0 = w - panel_w - 10
        y0 = 10

        self._draw_chart(
            screen,
            rect=(x0, y0, panel_w, 120),
            title="Queue len",
            xs=hist["time"],
            ys=hist["queue_len"],
            y_label="people",
            real_key="queue_len",
            sim_time=sim_time,
        )

        self._draw_chart(
            screen,
            rect=(x0, y0 + 130, panel_w, 120),
            title="Flow rate",
            xs=hist["time"],
            ys=hist["entry_rate"],
            y_label="1/s",
            ys2=hist["exit_rate"],
            label2="exit",
            real_key=None,
            sim_time=sim_time,
        )

        self._draw_chart(
            screen,
            rect=(x0, y0 + 260, panel_w, 120),
            title="Inside (est.)",
            xs=hist["time"],
            ys=hist["inside"],
            y_label="people",
            real_key="inside",
            sim_time=sim_time,
        )

        self._draw_chart(
            screen,
            rect=(x0, y0 + 390, panel_w, 120),
            title="Density",
            xs=hist["time"],
            ys=hist["density"],
            y_label="p/m^2",
            real_key="density_store",
            sim_time=sim_time,
        )

    def _format_lines(self, lf: dict, sim_time: float) -> List[str]:
        entry_rate_min = float(lf.get("entry_rate_s", 0.0)) * 60.0
        exit_rate_min = float(lf.get("exit_rate_s", 0.0)) * 60.0

        lines = [
            f"t={sim_time:7.2f}s  dt={float(lf.get('dt', 0.0)):0.3f}",
            f"active={int(lf.get('n_active', 0))}  inside_now={int(lf.get('inside_now', 0))}  inside_est={int(lf.get('inside_est', 0))}",
            f"entry: step={int(lf.get('entries_step', 0))}  total={int(lf.get('entries_total', 0))}  rate={entry_rate_min:0.1f}/min",
            f"exit:  step={int(lf.get('exits_step', 0))}   total={int(lf.get('exits_total', 0))}   rate={exit_rate_min:0.1f}/min",
            f"queue_len={int(lf.get('queue_len', 0))}  service_n={int(lf.get('service_n', 0))}",
            f"avg_speed={float(lf.get('avg_speed', 0.0)):0.2f}  density={float(lf.get('density_store', 0.0)):0.3f}",
        ]

        if self.real_data is not None and self.toggles.show_real:
            rq = self.real_data.value_at("queue_len", sim_time)
            re_in = self.real_data.value_at("entries_per_min", sim_time)
            re_out = self.real_data.value_at("exits_per_min", sim_time)
            if rq is not None or re_in is not None or re_out is not None:
                parts = []
                if re_in is not None:
                    parts.append(f"real_in={re_in:0.1f}/min")
                if re_out is not None:
                    parts.append(f"real_out={re_out:0.1f}/min")
                if rq is not None:
                    parts.append(f"real_queue={rq:0.1f}")
                lines.append("real: " + "  ".join(parts))

        lines.append("F1 HUD  G graphs  H hotspots  R real")
        return lines

    def _draw_text_panel(self, screen: pygame.Surface, lines: List[str], pos: Tuple[int, int]):
        x, y = pos
        padding = 6
        line_h = self.small_font.get_linesize()
        width = max(self.small_font.size(s)[0] for s in lines) + padding * 2
        height = line_h * len(lines) + padding * 2

        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        panel.fill((255, 255, 255, 200))
        screen.blit(panel, (x, y))

        ty = y + padding
        for s in lines:
            surf = self.small_font.render(s, True, (0, 0, 0))
            screen.blit(surf, (x + padding, ty))
            ty += line_h

    def _draw_chart(
        self,
        screen: pygame.Surface,
        rect: Tuple[int, int, int, int],
        title: str,
        xs: List[float],
        ys: List[float],
        y_label: str,
        ys2: Optional[List[float]] = None,
        label2: str = "",
        real_key: Optional[str] = None,
        sim_time: float = 0.0,
    ):
        x, y, w, h = rect
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        panel.fill((255, 255, 255, 200))
        screen.blit(panel, (x, y))

        title_surf = self.small_font.render(title, True, (0, 0, 0))
        screen.blit(title_surf, (x + 6, y + 4))

        if len(xs) < 2 or len(ys) < 2:
            return

        px0, py0 = x + 8, y + 22
        px1, py1 = x + w - 8, y + h - 10

        t0, t1 = xs[0], xs[-1]
        if t1 <= t0:
            return

        ymin = min(ys)
        ymax = max(ys)
        if ys2 is not None and len(ys2) == len(ys):
            ymin = min(ymin, min(ys2))
            ymax = max(ymax, max(ys2))

        real_xs, real_ys = [], []
        if self.real_data is not None and self.toggles.show_real and real_key and self.real_data.has(real_key):
            real_xs, real_ys = self.real_data.window(real_key, t0, t1)
            if real_ys:
                ymin = min(ymin, min(real_ys))
                ymax = max(ymax, max(real_ys))

        if ymax - ymin < 1e-9:
            ymax = ymin + 1.0

        def tx(tt: float) -> int:
            return int(px0 + (tt - t0) / (t1 - t0) * (px1 - px0))

        def ty(vv: float) -> int:
            return int(py1 - (vv - ymin) / (ymax - ymin) * (py1 - py0))

        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(px0, py0, px1 - px0, py1 - py0), 1)

        pts = [(tx(tt), ty(vv)) for tt, vv in zip(xs, ys)]
        if len(pts) >= 2:
            pygame.draw.lines(screen, (20, 90, 220), False, pts, 2)

        if ys2 is not None and len(ys2) == len(ys):
            pts2 = [(tx(tt), ty(vv)) for tt, vv in zip(xs, ys2)]
            if len(pts2) >= 2:
                pygame.draw.lines(screen, (220, 80, 80), False, pts2, 2)

        if real_xs and real_ys:
            for tt, vv in zip(real_xs, real_ys):
                pygame.draw.circle(screen, (0, 0, 0), (tx(tt), ty(vv)), 2)

        if t0 <= sim_time <= t1:
            cx = tx(sim_time)
            pygame.draw.line(screen, (0, 0, 0), (cx, py0), (cx, py1), 1)

        label = f"{y_label}  [{ymin:0.2f}..{ymax:0.2f}]"
        lab_surf = self.small_font.render(label, True, (0, 0, 0))
        screen.blit(lab_surf, (x + 6, y + h - 18))

    def _draw_hotspots(self, screen: pygame.Surface, vis, stats_manager):
        hotspots = stats_manager.live_hotspots()
        if not hotspots:
            return

        max_val = max(h["person_seconds"] for h in hotspots if h.get("person_seconds") is not None)
        if max_val <= 0:
            return

        cell = stats_manager.geom.heat_cell
        half = cell / 2.0

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        for h in hotspots:
            val = float(h.get("person_seconds", 0.0))
            a = int(30 + 180 * min(1.0, val / max_val))
            xw = float(h.get("x", 0.0))
            yw = float(h.get("y", 0.0))

            x0, y0 = xw - half, yw - half
            x1, y1 = xw + half, yw + half

            p0 = vis.world_to_screen((x0, y0))
            p1 = vis.world_to_screen((x1, y1))
            rx = min(p0[0], p1[0])
            ry = min(p0[1], p1[1])
            rw = abs(p1[0] - p0[0])
            rh = abs(p1[1] - p0[1])
            if rw <= 0 or rh <= 0:
                continue

            pygame.draw.rect(overlay, (255, 0, 0, a), pygame.Rect(rx, ry, rw, rh))

        screen.blit(overlay, (0, 0))
