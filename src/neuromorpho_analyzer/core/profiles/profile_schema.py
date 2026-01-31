"""Analysis profile schema for pipeline configuration."""

from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional
import json


@dataclass
class AnalysisProfile:
    """Complete analysis pipeline configuration.

    Stores all settings needed to reproduce an analysis:
    - Import settings (parameters, formats)
    - Plot settings (colors, scatter dots, styling)
    - Export settings (formats, output options)
    - Statistics settings (alpha, tests)
    - Frequency distribution settings
    - Density calculation settings
    """

    name: str
    description: str = ""

    # Import settings
    import_parameters: List[str] = field(default_factory=list)
    custom_parameters: List[str] = field(default_factory=list)
    supported_formats: List[str] = field(default_factory=lambda: ['xls', 'xlsx', 'csv', 'json'])

    # Plot settings
    plot_config: Dict = field(default_factory=dict)
    show_scatter_dots: bool = True
    scatter_alpha: float = 0.6
    scatter_size: int = 30
    scatter_jitter: float = 0.1

    # Export settings
    export_excel: bool = True
    export_graphpad: bool = False
    export_csv: bool = False
    export_statistics_tables: bool = True
    export_plots: bool = True
    plot_dpi: int = 800
    plot_formats: List[str] = field(default_factory=lambda: ['png', 'tif'])
    export_parameters: List[str] = field(default_factory=list)

    # Plot type toggles
    plot_types: Dict[str, bool] = field(default_factory=lambda: {
        'barplot_relative': True,
        'barplot_total': True,
        'boxplot_relative': True,
        'boxplot_total': True,
        'frequency_count': True,
        'frequency_relative': True,
    })

    # Condition selection
    selected_conditions: Optional[List[str]] = None  # None = all conditions

    # Statistics settings
    alpha: float = 0.05
    normality_test: bool = True
    post_hoc_test: str = 'tukey'  # 'tukey' or 'mann_whitney'

    # Frequency distribution settings
    frequency_bin_size: float = 10.0
    frequency_bin_count: int = 250

    # Density calculation settings
    calculate_density: bool = False
    image_area_um2: float = 12.2647  # 3.5021² μm² per image

    # Dataset split (for Liposome/Tubule separation)
    dataset_split: Dict[str, str] = field(default_factory=lambda: {
        'L': 'Liposome',
        'T': 'Tubule'
    })

    # Metadata
    created_date: Optional[str] = None
    modified_date: Optional[str] = None
    version: str = "1.0"

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict) -> 'AnalysisProfile':
        """Load from dictionary.

        Args:
            data: Dictionary with profile data

        Returns:
            AnalysisProfile instance
        """
        # Filter out unknown keys to handle version differences
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)

    @classmethod
    def from_json(cls, json_str: str) -> 'AnalysisProfile':
        """Load from JSON string.

        Args:
            json_str: JSON string with profile data

        Returns:
            AnalysisProfile instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def default_profile(cls, name: str = "Default") -> 'AnalysisProfile':
        """Create a default analysis profile.

        Args:
            name: Profile name

        Returns:
            Default AnalysisProfile
        """
        return cls(
            name=name,
            description="Default analysis profile with standard settings"
        )

    def get_active_plot_types(self) -> List[str]:
        """Get list of enabled plot types."""
        return [pt for pt, enabled in self.plot_types.items() if enabled]

    def set_plot_type(self, plot_type: str, enabled: bool) -> None:
        """Enable or disable a plot type."""
        if plot_type in self.plot_types:
            self.plot_types[plot_type] = enabled

    def is_condition_selected(self, condition: str) -> bool:
        """Check if a condition is selected.

        Args:
            condition: Condition name to check

        Returns:
            True if condition is selected (or all are selected)
        """
        if self.selected_conditions is None:
            return True  # All conditions selected
        return condition in self.selected_conditions
