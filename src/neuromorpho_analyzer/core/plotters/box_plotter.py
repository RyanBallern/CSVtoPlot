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
                       comparisons: List[Dict],
                       formula: str = None) -> plt.Figure:
        """
        Create box plot with significance brackets and optional scatter overlay.

        Args:
            data: Dict mapping condition names to data series
            title: Plot title
            ylabel: Y-axis label
            comparisons: Statistical comparison results
            formula: Optional formula to display in y-axis label (in italics)

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

        # Prepare data for plotting
        plot_data = [data[cond] for cond in conditions]
        positions = list(range(len(conditions)))
        position_map = {cond: i for i, cond in enumerate(conditions)}

        # Calculate data range for y-axis
        all_values = np.concatenate([d.values for d in data.values()])
        data_min = np.min(all_values)
        data_max = np.max(all_values)

        # Box width: spacing = 0.75 * width, so width + 0.75*width = 1.0 → width = 0.571
        box_width = 0.57

        # Create box plot
        bp = ax.boxplot(plot_data, positions=positions, widths=box_width,
                       patch_artist=True, showmeans=True,
                       meanprops=dict(marker='D', markerfacecolor='red',
                                    markeredgecolor='red', markersize=7))

        # Color boxes
        for patch, condition in zip(bp['boxes'], conditions):
            color = self.config.get_color(condition)
            patch.set_facecolor(color)
            patch.set_edgecolor('black')
            patch.set_linewidth(1.5)

        # Calculate error bar cap size (half the box width)
        # Box width is 0.57 in data units, we need capsize in points
        # Convert: data units -> inches -> points
        # Approximate: capsize should be ~28.5% of space between ticks
        box_width_data = 0.57
        # Rough conversion based on typical axes dimensions
        capsize = (box_width_data / 2) * 72 / (len(conditions) * 0.5)  # Dynamic based on conditions
        capsize = max(capsize, 3)  # Minimum 3 points

        # Add SEM error bars with calculated capsize
        for i, condition in enumerate(conditions):
            series = data[condition]
            mean = series.mean()
            sem = series.sem()

            ax.errorbar(i, mean, yerr=sem, fmt='none', ecolor='black',
                       elinewidth=2, capsize=capsize, capthick=2)

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

        # Set x-axis labels with n-numbers below condition names
        ax.set_xticks(positions)
        # Create labels with condition name and n-number on separate lines
        labels_with_n = [
            f"{self.config.get_full_name(c)}\nn={len(data[c])}"
            for c in conditions
        ]
        ax.set_xticklabels(
            labels_with_n,
            rotation=45, ha='right', fontsize=12
        )

        # Set labels with increased font size
        # If formula provided, add it in italics
        if formula:
            ylabel_full = f"{ylabel}\n$\\mathit{{{formula}}}$"
        else:
            ylabel_full = ylabel
        ax.set_ylabel(ylabel_full, fontsize=14, fontweight='bold')
        ax.set_title(title, fontsize=16, fontweight='bold')

        # Apply base styling
        self.config.apply_base_style(ax)

        # Set y-axis to start at 0 and fit data with minimal padding
        # Leave room for significance brackets at top
        y_min = 0
        y_max_data = data_max * 1.05  # 5% padding above data
        ax.set_ylim(y_min, y_max_data)

        # Add significance brackets (this will adjust y-limits)
        self.annotator.add_brackets(ax, comparisons, position_map)

        plt.tight_layout()
        return fig
