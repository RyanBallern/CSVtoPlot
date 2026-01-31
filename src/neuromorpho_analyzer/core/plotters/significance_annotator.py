import matplotlib.pyplot as plt
from typing import List, Dict
import numpy as np


class SignificanceAnnotator:
    """Adds significance brackets and stars to plots."""

    @staticmethod
    def get_significance_stars(p_value: float) -> str:
        """Convert p-value to star notation."""
        if p_value < 0.001:
            return '***'
        elif p_value < 0.01:
            return '**'
        elif p_value < 0.05:
            return '*'
        else:
            return ''

    def add_brackets(self, ax: plt.Axes, comparisons: List[Dict],
                    positions: Dict[str, int], height_offset: float = 1.0) -> None:
        """
        Add significance brackets to plot.

        Args:
            ax: Matplotlib axes
            comparisons: List of comparison dicts with group1, group2, p_value
            positions: Dict mapping condition names to x positions
            height_offset: Height offset for bracket placement
        """
        # Get current y-axis limits
        y_min, y_max = ax.get_ylim()
        y_range = y_max - y_min

        # Sort comparisons by distance between groups
        comparisons = sorted(
            comparisons,
            key=lambda x: abs(positions[x['group1']] - positions[x['group2']])
        )

        # Track bracket heights to avoid overlaps
        bracket_level = 0
        for comp in comparisons:
            if not comp.get('significant', False):
                continue

            group1 = comp['group1']
            group2 = comp['group2']
            p_value = comp['p_value']

            # Get x positions
            x1 = positions[group1]
            x2 = positions[group2]

            # Calculate bracket height with better spacing
            bracket_height = y_max + (bracket_level * 0.07 * y_range) + (0.03 * y_range)

            # Draw bracket
            self._draw_bracket(ax, x1, x2, bracket_height, y_range * 0.015)

            # Add stars with increased font size (reduced distance by half again)
            stars = self.get_significance_stars(p_value)
            mid_x = (x1 + x2) / 2
            ax.text(mid_x, bracket_height + y_range * 0.00375, stars,
                   ha='center', va='bottom', fontsize=14, fontweight='bold')

            bracket_level += 1

        # Adjust y-axis to accommodate brackets with more space
        if bracket_level > 0:
            new_y_max = y_max + (bracket_level * 0.07 * y_range) + (0.08 * y_range)
            ax.set_ylim(y_min, new_y_max)

    def _draw_bracket(self, ax: plt.Axes, x1: float, x2: float,
                     height: float, bar_height: float) -> None:
        """Draw a single significance bracket."""
        # Horizontal line
        ax.plot([x1, x2], [height, height], 'k-', linewidth=1.5)

        # Vertical lines
        ax.plot([x1, x1], [height - bar_height, height], 'k-', linewidth=1.5)
        ax.plot([x2, x2], [height - bar_height, height], 'k-', linewidth=1.5)
