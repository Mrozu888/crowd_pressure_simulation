from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, List

import pygame
import numpy as np


@dataclass
class HUDToggles:
    show_hud: bool = True
    show_graphs: bool = True
    show_heatmap: bool = False


class StatsHUD:
    """
    Simple HUD overlay:
    - Text block with key metrics
    - Optional mini time-series graphs
    - Optional heatmap hotspots overlay

    Note on time mapping:
    `real_seconds_per_sim_second` controls how simulation time is interpreted for display:
    real_time = sim_time * real_seconds_per_sim_second
    This does NOT affect simulation dynamics.
    """

    def __init__(
        self,
        font: pygame.font.Font,
        small_font: Optional[pygame.font.Font] = None,
        toggles: Optional[HUDToggles] = None,
        real_seconds_per_sim_second: float = 1.0,
        sim_seconds_per_real_second: float = 7.0,
    ):
        self.font = font
        self.small_font = small_font or font
        self.toggles = toggles or HUDToggles()
        self.real_seconds_per_sim_second = float(real_seconds_per_sim_second)

        self.sim_seconds_per_real_second = float(sim_seconds_per_real_second)
        self._start_ms = pygame.time.get_ticks()
    def handle_key(self, key: int):
        if key == pygame.K_F1:
            self.toggles.show_hud = not self.toggles.show_hud
        elif key == pygame.K_g:
            self.toggles.show_graphs = not self.toggles.show_graphs
        elif key == pygame.K_h:
            self.toggles.show_heatmap = not self.toggles.show_heatmap


    @staticmethod
    def _format_clock(seconds: float) -> str:
        s = float(seconds)
        if s < 0:
            s = 0.0
        total = int(s)
        h = total // 3600
        m = (total % 3600) // 60
        sec = total % 60
        if h > 0:
            return f"{h:02d}:{m:02d}:{sec:02d}"
        return f"{m:02d}:{sec:02d}"

    def _draw_text_block(self, screen: pygame.Surface, lines: List[str], x: int, y: int):
        pad = 6
        # compute box size
        widths = [self.font.size(line)[0] for line in lines]
        heights = [self.font.size(line)[1] for line in lines]
        box_w = (max(widths) if widths else 0) + 2 * pad
        box_h = (sum(heights) if heights else 0) + 2 * pad

        bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg.fill((255, 255, 255, 210))
        screen.blit(bg, (x, y))

        cy = y + pad
        for line in lines:
            surf = self.font.render(line, True, (0, 0, 0))
            screen.blit(surf, (x + pad, cy))
            cy += surf.get_height()

    def _draw_series(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
        xs: List[float],
        ys: List[float],
        title: str,
        y_label: str,
        legend_main: str = "series",
        extra: Optional[Tuple[List[float], List[float], str]] = None,  # (xs2, ys2, label2)
        fixed_y: Optional[Tuple[float, float]] = None,
    ):
        # background
        pygame.draw.rect(screen, (245, 245, 245), rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 1)

        # title
        title_s = self.small_font.render(title, True, (0, 0, 0))
        screen.blit(title_s, (rect.x + 6, rect.y + 4))

        # plot area
        pad_left = 32
        pad_right = 10
        pad_top = 20
        pad_bottom = 16
        ax = pygame.Rect(rect.x + pad_left, rect.y + pad_top, rect.w - pad_left - pad_right, rect.h - pad_top - pad_bottom)
        pygame.draw.rect(screen, (255, 255, 255), ax, 0)

        if len(xs) < 2 or len(ys) < 2 or len(xs) != len(ys):
            # labels
            yl = self.small_font.render(y_label, True, (0, 0, 0))
            screen.blit(yl, (rect.x + 4, rect.bottom - 16))
            xl = self.small_font.render("t_real(s)", True, (0, 0, 0))
            screen.blit(xl, (rect.right - 58, rect.bottom - 16))
            return

        x_min = float(min(xs))
        x_max = float(max(xs))
        if abs(x_max - x_min) < 1e-9:
            x_max = x_min + 1.0

        y_min = float(min(ys))
        y_max = float(max(ys))
        if extra is not None and len(extra[0]) == len(extra[1]) and len(extra[0]) >= 2:
            y_min = min(y_min, float(min(extra[1])))
            y_max = max(y_max, float(max(extra[1])))

        if fixed_y is not None:
            y_min, y_max = float(fixed_y[0]), float(fixed_y[1])

        if abs(y_max - y_min) < 1e-9:
            y_max = y_min + 1.0

        def to_px(xv: float, yv: float) -> Tuple[int, int]:
            px = ax.x + int((xv - x_min) / (x_max - x_min) * ax.w)
            py = ax.bottom - int((yv - y_min) / (y_max - y_min) * ax.h)
            return px, py

        # grid lines (light)
        for k in range(1, 4):
            gx = ax.x + int(k * ax.w / 4)
            gy = ax.y + int(k * ax.h / 4)
            pygame.draw.line(screen, (230, 230, 230), (gx, ax.y), (gx, ax.bottom), 1)
            pygame.draw.line(screen, (230, 230, 230), (ax.x, gy), (ax.right, gy), 1)

        # main series (blue)
        pts = [to_px(xs[i], ys[i]) for i in range(len(xs))]
        if len(pts) >= 2:
            pygame.draw.lines(screen, (0, 0, 255), False, pts, 2)

        # extra series (red)
        if extra is not None:
            xs2, ys2, _lab = extra
            if len(xs2) == len(ys2) and len(xs2) >= 2:
                pts2 = [to_px(xs2[i], ys2[i]) for i in range(len(xs2))]
                pygame.draw.lines(screen, (255, 0, 0), False, pts2, 2)

        # axis labels
        yl = self.small_font.render(y_label, True, (0, 0, 0))
        screen.blit(yl, (rect.x + 4, rect.bottom - 16))
        xl = self.small_font.render("t_real(s)", True, (0, 0, 0))
        screen.blit(xl, (rect.right - 58, rect.bottom - 16))

        # legend (top-right inside rect)
        lx = rect.right - 6
        ly = rect.y + 4
        # blue
        leg1 = self.small_font.render(legend_main, True, (0, 0, 255))
        lx -= leg1.get_width()
        screen.blit(leg1, (lx, ly))
        if extra is not None:
            xs2, ys2, lab2 = extra
            leg2 = self.small_font.render("  " + lab2, True, (255, 0, 0))
            lx -= leg2.get_width()
            screen.blit(leg2, (lx, ly))

    def _draw_heatmap_overlay(self, screen: pygame.Surface, stats, vis):
        # Draw only hotspots (top cells) as translucent red squares
        hm = getattr(stats, "heatmap", None)
        if hm is None:
            return
        # hotspots are computed in close(), but for live preview we just use current hm top cells
        heat_x0 = stats.geom.heat_x0
        heat_y0 = stats.geom.heat_y0
        cell = stats.geom.heat_cell

        flat = hm.ravel()
        if flat.size == 0 or np.all(flat <= 0):
            return
        k = min(40, flat.size)
        idxs = np.argpartition(flat, -k)[-k:]
        idxs = idxs[np.argsort(flat[idxs])[::-1]]
        rows, cols = hm.shape

        # normalize for alpha
        maxv = float(flat[idxs[0]]) if idxs.size else 0.0
        if maxv <= 0:
            return

        for fi in idxs:
            r = int(fi // cols)
            c = int(fi % cols)
            v = float(hm[r, c])
            if v <= 0:
                continue
            # cell center in world
            x = heat_x0 + (c + 0.0) * cell
            y = heat_y0 + (r + 0.0) * cell
            p1 = vis.world_to_screen((x, y))
            p2 = vis.world_to_screen((x + cell, y + cell))
            rx = min(p1[0], p2[0])
            ry = min(p1[1], p2[1])
            rw = abs(p2[0] - p1[0])
            rh = abs(p2[1] - p1[1])
            alpha = int(30 + 150 * min(1.0, v / maxv))
            s = pygame.Surface((max(1, rw), max(1, rh)), pygame.SRCALPHA)
            s.fill((255, 0, 0, alpha))
            screen.blit(s, (rx, ry))

    def draw(self, screen: pygame.Surface, stats, vis=None):
        if not self.toggles.show_hud:
            return

        last = getattr(stats, "last_frame", {}) or {}
        t_sim = float(last.get("time", 0.0))
        dt_sim = float(last.get("dt", 0.0))

        t_real = t_sim * self.real_seconds_per_sim_second
        dt_real = dt_sim * self.real_seconds_per_sim_second

        real_elapsed = (pygame.time.get_ticks() - self._start_ms) / 1000.0
        sim_elapsed = real_elapsed * self.sim_seconds_per_real_second
        inside = int(last.get("inside_now", 0))
        # total: ile agentów weszło do systemu (sklepu) łącznie
        total = int(last.get("total_entered", last.get("entries_total", 0)))
        # exited: ilu agentów zakończyło zakupy i wyszło ze sklepu
        exited = int(last.get("exited_total", last.get("exits_total", 0)))

        queue_total = int(last.get("queue_total", 0))
        serving_now = int(last.get("serving_now", 0))
        density = float(last.get("density_store", 0.0))

        med_shop_sim_min = last.get("shop_median_min")
        med_shop_real_min = float(med_shop_sim_min) * self.real_seconds_per_sim_second if med_shop_sim_min is not None else None

        lines = [
            f"real={self._format_clock(real_elapsed)}  sim={self._format_clock(sim_elapsed)}",
            f"inside={inside} total={total} exited={exited}",
            f"queue_total={queue_total} serving_now={serving_now}",
            f"density={density:.3f}" + (f" shop_med={med_shop_real_min:.1f}min" if med_shop_real_min is not None else ""),
            "F1 HUD   G graphs   H heatmap",
        ]
        # Put the HUD text block in the right sidebar (so it does not cover the shop).
        if vis is not None and hasattr(vis, "scene_width") and hasattr(vis, "offset_x"):
            x_txt = int(vis.offset_x + vis.scene_width + getattr(vis, "sidebar_gap", 20))
            y_txt = 10
        else:
            x_txt = 10
            y_txt = 40
        self._draw_text_block(screen, lines, x_txt, y_txt)

        if self.toggles.show_heatmap and vis is not None:
            self._draw_heatmap_overlay(screen, stats, vis)

        if not self.toggles.show_graphs:
            return

        # graphs layout
        w = 500
        h = 200
        gap = 10
        x0 = screen.get_width() - w - 10
        # Keep charts in the far-right area.
        y0 = 170

        # scaled time axis (real seconds)
        t_hist_sim = list(getattr(stats, "t_hist", []))
        xs = [x * self.real_seconds_per_sim_second for x in t_hist_sim]

        # 1) inside
        rect1 = pygame.Rect(x0, y0 + (h + gap) * 0, w, h)
        inside_hist = list(getattr(stats, "inside_hist", []))
        self._draw_series(screen, rect1, xs, inside_hist, title="Inside (now)", y_label="people", legend_main="inside")

        # 2) density
        rect2 = pygame.Rect(x0, y0 + (h + gap) * 1, w, h)
        dens_hist = list(getattr(stats, "density_hist", []))
        ymax = max(0.1, (max(dens_hist) * 1.2) if dens_hist else 0.1)
        self._draw_series(screen, rect2, xs, dens_hist, title="Density", y_label="p/m^2", legend_main="density", fixed_y=(0.0, ymax))

        # 3) shopping time (real minutes) + median
        rect3 = pygame.Rect(x0, y0 + (h + gap) * 2, w, h)
        shop_x_sim = list(getattr(stats, "shop_exit_t", []))
        shop_x = [x * self.real_seconds_per_sim_second for x in shop_x_sim]
        shop_y = [y * self.real_seconds_per_sim_second for y in list(getattr(stats, "shop_time_min", []))]
        shop_med = [y * self.real_seconds_per_sim_second for y in list(getattr(stats, "shop_median_min", []))]
        extra_shop = (shop_x, shop_med, "median") if len(shop_x) >= 2 and len(shop_x) == len(shop_med) else None
        self._draw_series(screen, rect3, shop_x, shop_y, title="Shopping time (real min)", y_label="min", legend_main="shopping", extra=extra_shop)

        # 4) serving now (no median)
        rect4 = pygame.Rect(x0, y0 + (h + gap) * 3, w, h)
        serving_hist = list(getattr(stats, "serving_now_hist", []))
        self._draw_series(screen, rect4, xs, serving_hist, title="Serving now", y_label="people", legend_main="serving_now")
