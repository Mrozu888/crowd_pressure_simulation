"""Statistics collection for the simulation (CSV + live HUD + heatmap).

This package only *reads* Environment/Agent state; it should not change simulation behavior.
"""

from .geometry import StatsGeometry
from .manager import StatsManager
from .writer import StatsWriter
from .real_data import RealDataSeries
from .hud import StatsHUD

__all__ = ["StatsGeometry", "StatsManager", "StatsWriter", "RealDataSeries", "StatsHUD"]
