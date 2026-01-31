import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, List
import numpy as np

from .plot_config import PlotConfig
from .significance_annotator import SignificanceAnnotator
from ..processors.statistics import StatisticsEngine


class BarPlotter:
    """Creates bar plots with SEM and significance annotations."""

    def __init__(self, plot_config: PlotConfig, stats_engine: StatisticsEngine):
        self.config = plot_config
        self.stats = stats_engine
        self.annotator = SignificanceAnnotator()

    def create_barplot(self, data: Dict[str, pd.Series],
                       title: str, ylabel: str,
                       comparisons: List[Dict]) -> plt.Figure:
        """
        Create bar plot with significance brackets and optional scatter overlay.

        Args:
            data: Dict mapping condition names to data series
            title: Plot title
            ylabel: Y-axis label
            comparisons: Statistical comparison results

        Returns:
            Matplotlib figure
        """
        # Determine order
        if self.config.plotting_order:
            conditions = [c for c in self.config.plotting_order if c in data]
        else:
            conditions = sorted(data.keys())

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        # Calculate means and SEMs
        means = [data[cond].mean() for cond in conditions]
        sems = [data[cond].sem() for cond in conditions]

        # Create positions
        positions = np.arange(len(conditions))
        position_map = {cond: i for i, cond in enumerate(conditions)}

        # Create bars
        bars = ax.bar(positions, means, width=0.6, edgecolor='black', linewidth=1.5)

        # Color bars
        for bar, condition in zip(bars, conditions):
            color = self.config.get_color(condition)
            bar.set_facecolor(color)

        # Add SEM error bars (both directions)
        ax.errorbar(positions, means, yerr=sems, fmt='none', ecolor='black',
                   elinewidth=2, capsize=5, capthick=2)

        # Add scatter dots if enabled
        if self.config.show_scatter_dots:
            for i, condition in enumerate(conditions):
                series = data[condition]

                # Add jitter
                np.random.seed(42)
                x_jitter = np.random.normal(
                    i, self.config.scatter_jitter, size=len(series)
                )

                # Plot individual points
                ax.scatter(x_jitter, series,
                          alpha=self.config.scatter_alpha,
                          s=self.config.scatter_size,
                          c='black',
                          edgecolors='white',
                          linewidths=1,
                          zorder=3)

        # Add n-numbers
        for i, condition in enumerate(conditions):
            n = len(data[condition])
            ax.text(i, ax.get_ylim()[0], f'n={n}',
                   ha='center', va='top', fontsize=10)

        # Set x-axis labels
        ax.set_xticks(positions)
        ax.set_xticklabels(
            [self.config.get_full_name(c) for c in conditions],
            rotation=45, ha='right'
        )

        # Set labels
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')

        # Apply base styling
        self.config.apply_base_style(ax)

        # Add significance brackets
        self.annotator.add_brackets(ax, comparisons, position_map)

        plt.tight_layout()
        return fig
