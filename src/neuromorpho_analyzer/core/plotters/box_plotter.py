import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, List
import numpy as np

from .plot_config import PlotConfig
from .significance_annotator import SignificanceAnnotator
from ..processors.statistics import StatisticsEngine


class BoxPlotter:
    """Creates box plots with SEM and significance annotations."""

    def __init__(self, plot_config: PlotConfig, stats_engine: StatisticsEngine):
        self.config = plot_config
        self.stats = stats_engine
        self.annotator = SignificanceAnnotator()

    def create_boxplot(self, data: Dict[str, pd.Series],
                       title: str, ylabel: str,
                       comparisons: List[Dict]) -> plt.Figure:
        """
        Create box plot with significance brackets and optional scatter overlay.

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

        # Prepare data for plotting
        plot_data = [data[cond] for cond in conditions]
        positions = list(range(len(conditions)))
        position_map = {cond: i for i, cond in enumerate(conditions)}

        # Create box plot
        bp = ax.boxplot(plot_data, positions=positions, widths=0.6,
                       patch_artist=True, showmeans=True,
                       meanprops=dict(marker='D', markerfacecolor='red',
                                    markeredgecolor='red', markersize=6))

        # Color boxes
        for patch, condition in zip(bp['boxes'], conditions):
            color = self.config.get_color(condition)
            patch.set_facecolor(color)
            patch.set_edgecolor('black')
            patch.set_linewidth(1.5)

        # Add SEM error bars
        for i, condition in enumerate(conditions):
            series = data[condition]
            mean = series.mean()
            sem = series.sem()

            ax.errorbar(i, mean, yerr=sem, fmt='none', ecolor='black',
                       elinewidth=2, capsize=5, capthick=2)

        # Add scatter dots if enabled
        if self.config.show_scatter_dots:
            for i, condition in enumerate(conditions):
                series = data[condition]

                # Add jitter to x-coordinates
                np.random.seed(42)  # Reproducible jitter
                x_jitter = np.random.normal(
                    i, self.config.scatter_jitter, size=len(series)
                )

                # Plot individual points
                ax.scatter(x_jitter, series,
                          alpha=self.config.scatter_alpha,
                          s=self.config.scatter_size,
                          c='black',
                          edgecolors='black',
                          linewidths=0.5,
                          zorder=3)  # Ensure dots appear on top

        # Add n-numbers
        for i, condition in enumerate(conditions):
            n = len(data[condition])
            ax.text(i, ax.get_ylim()[0], f'n={n}',
                   ha='center', va='top', fontsize=10)

        # Set x-axis labels (use full names)
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
