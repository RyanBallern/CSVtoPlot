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

        # Calculate figure size: 1 cm = 0.3937 inches per condition (max)
        cm_per_condition = 1.0
        inches_per_condition = cm_per_condition * 0.3937
        width = max(len(conditions) * inches_per_condition + 2, 4)  # Min 4 inches
        height = 6

        # Create figure
        fig, ax = plt.subplots(figsize=(width, height))

        # Calculate means and SEMs
        means = [data[cond].mean() for cond in conditions]
        sems = [data[cond].sem() for cond in conditions]

        # Create positions
        positions = np.arange(len(conditions))
        position_map = {cond: i for i, cond in enumerate(conditions)}

        # Calculate data range
        all_values = np.concatenate([d.values for d in data.values()])
        data_max = np.max(all_values)

        # Bar width: spacing = 0.75 * width, so width + 0.75*width = 1.0 → width = 0.571
        bar_width = 0.57

        # Create bars
        bars = ax.bar(positions, means, width=bar_width, edgecolor='black', linewidth=1.5)

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

        # Set x-axis labels (use full names) with increased font size
        ax.set_xticks(positions)
        ax.set_xticklabels(
            [self.config.get_full_name(c) for c in conditions],
            rotation=45, ha='right', fontsize=12
        )

        # Set labels with increased font size
        ax.set_ylabel(ylabel, fontsize=14, fontweight='bold')
        ax.set_title(title, fontsize=16, fontweight='bold')

        # Apply base styling
        self.config.apply_base_style(ax)

        # Set y-axis to start at 0 and fit data with minimal padding
        y_min = 0
        y_max_data = data_max * 1.05  # 5% padding above data
        ax.set_ylim(y_min, y_max_data)

        # Add significance brackets (this will adjust y-limits)
        self.annotator.add_brackets(ax, comparisons, position_map)

        # Add n-numbers at the bottom of each bar (inside or just above x-axis)
        for i, condition in enumerate(conditions):
            n = len(data[condition])
            # Place n at a small offset above y=0
            y_text = y_min + (ax.get_ylim()[1] - y_min) * 0.02
            ax.text(i, y_text, f'n={n}',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')

        plt.tight_layout()
        return fig
