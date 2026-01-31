"""Configuration for export operations."""

from dataclasses import dataclass, field
from typing import List, Set, Optional, Dict


@dataclass
class ExportConfig:
    """Configuration for export operations."""

    # Format toggles
    export_excel: bool = True
    export_graphpad: bool = False  # Toggle GraphPad export
    export_csv: bool = False
    export_statistics_tables: bool = True

    # Plot toggles
    export_plots: bool = True
    plot_formats: List[str] = field(default_factory=lambda: ['png', 'tif'])
    plot_dpi: int = 800

    # Plot type selection
    plot_types: Set[str] = field(default_factory=lambda: {
        'boxplot_total',
        'boxplot_relative',
        'barplot_total',
        'barplot_relative',
        'frequency_count',
        'frequency_relative'
    })

    # Condition selection
    selected_conditions: Optional[List[str]] = None  # None = all conditions

    # Parameter selection
    selected_parameters: Optional[List[str]] = None

    # Dataset splitting
    split_by_marker: bool = False
    marker_names: Optional[Dict[str, str]] = None  # {'L': 'Liposomes', 'T': 'Tubules'}

    def should_export_plot_type(self, plot_type: str) -> bool:
        """Check if a plot type should be exported.

        Args:
            plot_type: Plot type identifier

        Returns:
            True if plot type should be exported
        """
        return plot_type in self.plot_types

    def should_include_condition(self, condition: str) -> bool:
        """Check if a condition should be included in export.

        Args:
            condition: Condition name

        Returns:
            True if condition should be included
        """
        if self.selected_conditions is None:
            return True  # Include all
        return condition in self.selected_conditions

    def get_active_plot_types(self) -> List[str]:
        """Get list of active plot types.

        Returns:
            Sorted list of plot types to export
        """
        return sorted(self.plot_types)
