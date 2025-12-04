"""
Simple PyGame HUD overlay for statistics.

Draws a small panel with aggregated numbers obtained from StatsManager.
"""

from __future__ import annotations
from typing import Tuple, Optional

import pygame
from .manager import StatsManager


class StatsHUD:
    """
    Lightweight HUD for PyGame surface.

    Usage:
      hud = StatsHUD(stats_manager)
      ...
      hud.draw(screen)
    """

    def __init__(self,
                 stats: StatsManager,
                 font: Optional[pygame.font.Font] = None,
                 pos: Tuple[int, int] = (10, 10)) -> None:
        self.stats = stats
        self.pos = pos
        if font is None:
            self.font = pygame.font.SysFont("consolas", 14)
        else:
            self.font = font

    def draw(self, surface: pygame.Surface) -> None:
        row = self.stats.last_frame_stats
        if row is None:
            return

        lines = [
            f"t = {row.t:6.1f} s, agents = {row.n_agents}",
            f"Zones: store={row.n_in_store}, vest={row.n_in_vestibule}, street={row.n_in_street}",
            f"Flow [people/min]: left={row.flow_left_door_per_min:.2f}, "
            f"top={row.flow_top_door_per_min:.2f}, right={row.flow_right_door_per_min:.2f}",
            f"Contacts: d<1m={row.contacts_lt_1m}, d<covid={row.contacts_lt_covid}",
            f"Speed: avg={row.avg_speed:.2f}, store={row.avg_speed_store:.2f}, vest={row.avg_speed_vestibule:.2f}",
            f"Queue front cashiers: {row.queue_front_cashiers}",
            f"Density: store={row.density_store:.3f} 1/m^2, vest={row.density_vestibule:.3f} 1/m^2",
        ]

        # Compute panel size
        padding = 6
        line_surfs = [self.font.render(txt, True, (0, 0, 0)) for txt in lines]
        width = max(s.get_width() for s in line_surfs) + 2 * padding
        height = len(line_surfs) * (self.font.get_height() + 2) + 2 * padding

        x, y = self.pos
        panel_rect = pygame.Rect(x, y, width, height)

        # Semi-transparent background
        bg = pygame.Surface((width, height), pygame.SRCALPHA)
        bg.fill((255, 255, 255, 220))
        surface.blit(bg, panel_rect)

        # Border
        pygame.draw.rect(surface, (0, 0, 0), panel_rect, 1)

        # Text lines
        cy = y + padding
        for s in line_surfs:
            surface.blit(s, (x + padding, cy))
            cy += self.font.get_height() + 2
