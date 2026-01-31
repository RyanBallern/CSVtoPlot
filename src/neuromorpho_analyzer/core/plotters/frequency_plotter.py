import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, Optional
import numpy as np

from .plot_config import PlotConfig
from .significance_annotator import SignificanceAnnotator


class FrequencyPlotter:
    """Creates frequency distribution plots."""

    def __init__(self, plot_config: PlotConfig):
        self.config = plot_config
        self.annotator = SignificanceAnnotator()

    def create_frequency_plot(self, distributions: Dict[str, pd.DataFrame],
                            title: str, value_type: str = 'count',
                            bin_comparisons: Optional[pd.DataFrame] = None,
                            formula: str = None) -> plt.Figure:
        """
        Create frequency distribution plot.

        Args:
            distributions: Dict mapping conditions to frequency DataFrames
            title: Plot title
            value_type: 'count' or 'relative'
            bin_comparisons: DataFrame with per-bin significance results
            formula: Optional formula to display in y-axis label (in italics)

        Returns:
            Matplotlib figure
        """
        # Determine order
        if self.config.plotting_order:
            conditions = [c for c in self.config.plotting_order if c in distributions]
        else:
            conditions = sorted(distributions.keys())

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))

        # Get all bins
        all_bins = set()
        for dist in distributions.values():
            all_bins.update(zip(dist['bin_start'], dist['bin_end']))
        all_bins = sorted(all_bins)

        # Create grouped bar chart
        n_conditions = len(conditions)
        n_bins = len(all_bins)
        bar_width = 0.8 / n_conditions

        x = np.arange(n_bins)

        # Store values for optional line plot
        condition_values = {}

        for i, condition in enumerate(conditions):
            dist = distributions[condition]

            # Extract values for each bin
            values = []
            for bin_start, bin_end in all_bins:
                row = dist[(dist['bin_start'] == bin_start) &
                          (dist['bin_end'] == bin_end)]
                if not row.empty:
                    if value_type == 'count':
                        values.append(row['count'].values[0])
                    else:
                        values.append(row['relative_freq'].values[0])
                else:
                    values.append(0)

            # Plot bars
            offset = (i - n_conditions/2 + 0.5) * bar_width
            color = self.config.get_color(condition)
            ax.bar(x + offset, values, bar_width,
                  label=self.config.get_full_name(condition),
                  color=color, edgecolor='black', linewidth=1)

        # Set x-axis labels (bin ranges) with increased font size
        # Right-align labels: upper corner aligns with bin center
        bin_labels = [f'{start:.0f}-{end:.0f}' for start, end in all_bins]
        ax.set_xticks(x)
        ax.set_xticklabels(bin_labels, rotation=45, ha='right', fontsize=12, rotation_mode='anchor')

        # Add 3mm (≈8 points) spacing between axis and labels (half of box/bar plots)
        ax.tick_params(axis='x', which='both', bottom=False, top=False, pad=8)

        # Labels with increased font size
        ax.set_xlabel('Bin Range', fontsize=14, fontweight='bold')
        ylabel = 'Count' if value_type == 'count' else 'Relative Frequency'
        # If formula provided, add it in italics
        if formula:
            ylabel_full = f"{ylabel}\n$\\mathit{{{formula}}}$"
        else:
            ylabel_full = ylabel
        ax.set_ylabel(ylabel_full, fontsize=14, fontweight='bold')
        ax.set_title(title, fontsize=16, fontweight='bold')

        # Legend with increased font size
        ax.legend(frameon=False, fontsize=12)

        # Apply base styling
        self.config.apply_base_style(ax)

        # Set y-axis to start at 0
        current_ylim = ax.get_ylim()
        ax.set_ylim(0, current_ylim[1])

        # Add significance markers if provided
        if bin_comparisons is not None:
            self._add_bin_significance_markers(ax, bin_comparisons, x)

        plt.tight_layout()
        return fig

    def create_frequency_line_plot(self, distributions: Dict[str, pd.DataFrame],
                                   title: str, value_type: str = 'count',
                                   formula: str = None) -> plt.Figure:
        """
        Create line plot for frequency distributions (separate from bar chart).

        Only creates plot if there are fewer than 5 conditions.

        Args:
            distributions: Dict mapping conditions to frequency DataFrames
            title: Plot title
            value_type: 'count' or 'relative'
            formula: Optional formula to display in y-axis label (in italics)

        Returns:
            Matplotlib figure or None if too many conditions
        """
        # Determine order
        if self.config.plotting_order:
            conditions = [c for c in self.config.plotting_order if c in distributions]
        else:
            conditions = sorted(distributions.keys())

        n_conditions = len(conditions)

        # Only create line plot if fewer than 5 conditions
        if n_conditions >= 5:
            return None

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))

        # Get all bins
        all_bins = set()
        for dist in distributions.values():
            all_bins.update(zip(dist['bin_start'], dist['bin_end']))
        all_bins = sorted(all_bins)

        n_bins = len(all_bins)
        x = np.arange(n_bins)

        # Plot lines for each condition
        for condition in conditions:
            dist = distributions[condition]

            # Extract values for each bin
            values = []
            for bin_start, bin_end in all_bins:
                row = dist[(dist['bin_start'] == bin_start) &
                          (dist['bin_end'] == bin_end)]
                if not row.empty:
                    if value_type == 'count':
                        values.append(row['count'].values[0])
                    else:
                        values.append(row['relative_freq'].values[0])
                else:
                    values.append(0)

            color = self.config.get_color(condition)
            # Plot line with markers
            ax.plot(x, values,
                   color=color,
                   linewidth=2,
                   marker='o',
                   markersize=6,
                   markerfacecolor=color,
                   markeredgecolor='black',
                   markeredgewidth=1,
                   label=self.config.get_full_name(condition))

        # Set x-axis labels (bin ranges) with increased font size
        # Right-align labels: upper corner aligns with bin center
        bin_labels = [f'{start:.0f}-{end:.0f}' for start, end in all_bins]
        ax.set_xticks(x)
        ax.set_xticklabels(bin_labels, rotation=45, ha='right', fontsize=12, rotation_mode='anchor')

        # Add 3mm (≈8 points) spacing between axis and labels (half of box/bar plots)
        ax.tick_params(axis='x', which='both', bottom=False, top=False, pad=8)

        # Labels with increased font size
        ax.set_xlabel('Bin Range', fontsize=14, fontweight='bold')
        ylabel = 'Count' if value_type == 'count' else 'Relative Frequency'
        # If formula provided, add it in italics
        if formula:
            ylabel_full = f"{ylabel}\n$\\mathit{{{formula}}}$"
        else:
            ylabel_full = ylabel
        ax.set_ylabel(ylabel_full, fontsize=14, fontweight='bold')
        ax.set_title(title, fontsize=16, fontweight='bold')

        # Legend with increased font size
        ax.legend(frameon=False, fontsize=12)

        # Apply base styling
        self.config.apply_base_style(ax)

        # Set y-axis to start at 0
        current_ylim = ax.get_ylim()
        ax.set_ylim(0, current_ylim[1])

        plt.tight_layout()
        return fig

    def _add_bin_significance_markers(self, ax: plt.Axes,
                                     bin_comparisons: pd.DataFrame,
                                     bin_positions: np.ndarray) -> None:
        """Add significance markers above bins."""
        y_max = ax.get_ylim()[1]

        for idx, row in bin_comparisons.iterrows():
            if row['significant']:
                stars = self.annotator.get_significance_stars(row['p_value'])
                if stars:
                    ax.text(bin_positions[idx], y_max * 0.95, stars,
                           ha='center', va='top', fontsize=14, fontweight='bold')
