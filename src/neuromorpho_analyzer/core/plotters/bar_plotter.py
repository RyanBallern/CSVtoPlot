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
                       comparisons: List[Dict],
                       formula: str = None,
                       yunit: str = None) -> plt.Figure:
        """
        Create bar plot with significance brackets and optional scatter overlay.

        Args:
            data: Dict mapping condition names to data series
            title: Plot title
            ylabel: Y-axis label
            comparisons: Statistical comparison results
            formula: Optional formula to display in y-axis label (in italics)
            yunit: Optional unit to display in square brackets after y-axis label

        Returns:
            Matplotlib figure
        """
        # Determine order
        if self.config.plotting_order:
            conditions = [c for c in self.config.plotting_order if c in data]
        else:
            conditions = sorted(data.keys())

        # Calculate figure size: max 1.5 cm per condition for even spacing
        cm_per_condition = 1.5
        inches_per_condition = cm_per_condition * 0.3937
        # Add margins: 1.5 inches on each side for labels
        width = (len(conditions) * inches_per_condition) + 3
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

        # Calculate error bar cap size (half the bar width)
        # Bar width is 0.57 in data units
        capsize = (bar_width / 2) * 72 / (len(conditions) * 0.5)  # Dynamic based on conditions
        capsize = max(capsize, 3)  # Minimum 3 points

        # Add SEM error bars (both directions) with calculated capsize
        ax.errorbar(positions, means, yerr=sems, fmt='none', ecolor='black',
                   elinewidth=2, capsize=capsize, capthick=2)

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
        # Center labels over bars
        ax.set_xticks(positions)
        ax.set_xticklabels(
            [self.config.get_full_name(c) for c in conditions],
            rotation=45, ha='center', fontsize=12, rotation_mode='anchor'
        )

        # Remove x-axis ticks for categorical data
        ax.tick_params(axis='x', which='both', bottom=False, top=False)

        # Set labels with increased font size
        # Add unit in brackets if provided, then formula in italics if provided
        ylabel_full = ylabel
        if yunit:
            ylabel_full = f"{ylabel} [{yunit}]"
        if formula:
            ylabel_full = f"{ylabel_full}\n$\\mathit{{{formula}}}$"
        ax.set_ylabel(ylabel_full, fontsize=14, fontweight='bold')
        ax.set_title(title, fontsize=16, fontweight='bold')

        # Apply base styling
        self.config.apply_base_style(ax)

        # Set y-axis to start at 0 and fit data with minimal padding
        y_min = 0

        # Calculate max value considering bars + SEM
        max_bar_with_sem = max([means[i] + sems[i] for i in range(len(means))])

        # Adjust padding based on whether scatter dots are shown
        if self.config.show_scatter_dots:
            # With scatter: use data maximum with 5% padding
            y_max_data = data_max * 1.05
        else:
            # Without scatter: use bar+SEM with 10-15% padding
            y_max_data = max_bar_with_sem * 1.12  # 12% padding

        # Temporarily set limits to let matplotlib calculate ticks
        ax.set_ylim(y_min, y_max_data)

        # Add significance brackets (this will adjust y-limits)
        self.annotator.add_brackets(ax, comparisons, position_map)

        # Round y_max to nearest tick value and set final limits
        yticks = ax.get_yticks()
        current_ymax = ax.get_ylim()[1]

        # Find the first tick >= current y_max
        final_ymax = None
        for tick in yticks:
            if tick >= current_ymax:
                final_ymax = tick
                break

        if final_ymax is not None:
            ax.set_ylim(y_min, final_ymax)
            # Filter ticks to only show those within the range
            visible_ticks = [t for t in yticks if y_min <= t <= final_ymax]
            ax.set_yticks(visible_ticks)

        # Add n-numbers at the bottom of each bar (inside or just above x-axis)
        for i, condition in enumerate(conditions):
            n = len(data[condition])
            # Place n at a small offset above y=0
            y_text = y_min + (ax.get_ylim()[1] - y_min) * 0.02
            ax.text(i, y_text, f'n={n}',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')

        plt.tight_layout()
        return fig
