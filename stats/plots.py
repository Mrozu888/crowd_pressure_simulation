"""Offline plot saving for simulation statistics.

These plots are saved to files (PNG) when the simulation ends.
They are meant for reports and calibration work.
"""

from __future__ import annotations

import os
from typing import Sequence

import matplotlib


def _setup_matplotlib():
    # Use a non-interactive backend (works in headless environments)
    try:
        matplotlib.use("Agg")
    except Exception:
        pass


def _save_line_plot(
    *,
    path: str,
    xs: Sequence[float],
    ys: Sequence[float],
    title: str,
    x_label: str,
    y_label: str,
    label: str,
    xs2: Sequence[float] | None = None,
    ys2: Sequence[float] | None = None,
    label2: str | None = None,
):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(8, 3.5))
    plt.plot(list(xs), list(ys), label=label)
    if xs2 is not None and ys2 is not None and label2 is not None and len(xs2) and len(ys2):
        plt.plot(list(xs2), list(ys2), label=label2)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def _save_scatter_plot(
    *,
    path: str,
    xs: Sequence[float],
    ys: Sequence[float],
    title: str,
    x_label: str,
    y_label: str,
    label: str,
):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(6, 4))
    plt.scatter(list(xs), list(ys), s=12, label=label)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def save_all_plots(stats, base_dir: str):
    """Save key HUD plots into files with axes and legend."""
    _setup_matplotlib()

    out_dir = os.path.join(base_dir, "plots")
    os.makedirs(out_dir, exist_ok=True)

    time_factor = float(getattr(stats, "real_seconds_per_sim_second", 1.0))
    t_sim = list(getattr(stats, "t_hist", []))
    t = [x * time_factor for x in t_sim]

    inside = list(getattr(stats, "inside_hist", []))
    if len(t) >= 2 and len(inside) >= 2:
        _save_line_plot(
            path=os.path.join(out_dir, "inside_now.png"),
            xs=t,
            ys=inside,
            title="Inside (now)",
            x_label="time (real s)",
            y_label="people",
            label="inside_now",
        )

    dens = list(getattr(stats, "density_hist", []))
    if len(t) >= 2 and len(dens) >= 2:
        _save_line_plot(
            path=os.path.join(out_dir, "density.png"),
            xs=t,
            ys=dens,
            title="Density (store)",
            x_label="time (real s)",
            y_label="people / m^2",
            label="density_store",
        )

        serving = list(getattr(stats, "serving_now_hist", []))
    if len(t) >= 2 and len(serving) >= 2:
        _save_line_plot(
            path=os.path.join(out_dir, "queue.png"),
            xs=t,
            ys=serving,
            title="Serving now (cashiers)",
            x_label="time (real s)",
            y_label="people",
            label="serving_now",
        )

    shop_t_sim = list(getattr(stats, "shop_exit_t", []))
    shop_t = [x * time_factor for x in shop_t_sim]
    shop_y = [y * time_factor for y in list(getattr(stats, "shop_time_min", []))]
    shop_med = [y * time_factor for y in list(getattr(stats, "shop_median_min", []))]
    if len(shop_t) >= 2 and len(shop_y) >= 2:
        _save_line_plot(
            path=os.path.join(out_dir, "shopping_time.png"),
            xs=shop_t,
            ys=shop_y,
            xs2=shop_t if len(shop_med) == len(shop_t) else None,
            ys2=shop_med if len(shop_med) == len(shop_t) else None,
            title="Shopping time (completed agents)",
            x_label="exit time (real s)",
            y_label="shopping time (real min)",
            label="shopping_time",
            label2="median",
        )
