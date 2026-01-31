from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors


class PlotConfig:
    """Configuration for plot styling and aesthetics."""

    DEFAULT_COLORS = {
        'Control': '#FFFFFF',  # White
        'GST': '#D3D3D3',      # Light grey
    }

    def __init__(self):
        self.condition_colors: Dict[str, str] = {}
        self.condition_names: Dict[str, str] = {}  # Short name -> Full display name
        self.plotting_order: List[str] = []
        self.plot_range: Optional[Tuple[float, float]] = None

        # Scatter plot settings
        self.show_scatter_dots: bool = True  # Default: show individual points
        self.scatter_alpha: float = 0.6  # Transparency
        self.scatter_size: int = 6  # Point size (reduced to 1/5 of original 30)
        self.scatter_jitter: float = 0.1  # Jitter to prevent overlap

    def set_condition_color(self, condition: str, color: str) -> None:
        """
        Set color for a condition.

        Args:
            condition: Condition name
            color: Hex color code (e.g., '#FF0000')
        """
        # Validate color
        try:
            mcolors.hex2color(color)
            self.condition_colors[condition] = color
        except ValueError:
            raise ValueError(f"Invalid color code: {color}")

    def set_condition_colors_from_rgb(self, condition: str,
                                     rgb: Tuple[int, int, int]) -> None:
        """
        Set color from RGB values (0-255).

        Args:
            condition: Condition name
            rgb: Tuple of (R, G, B) values
        """
        # Convert to hex
        hex_color = '#{:02x}{:02x}{:02x}'.format(*rgb)
        self.set_condition_color(condition, hex_color)

    def set_condition_name(self, short_name: str, full_name: str) -> None:
        """
        Map short condition name to full display name.

        This allows users to define custom aliases/expansions for condition names.
        For example: 'GST' -> 'Gastrin Treatment', 'Ctrl' -> 'Control Group'

        Args:
            short_name: Short condition code (as it appears in filenames/data)
            full_name: Full descriptive name for display in plots
        """
        self.condition_names[short_name] = full_name

    def set_plotting_order(self, order: List[str]) -> None:
        """Set order in which conditions appear in plots."""
        self.plotting_order = order

    def set_plot_range(self, y_min: float, y_max: float) -> None:
        """Set y-axis range for plots."""
        self.plot_range = (y_min, y_max)

    def set_scatter_settings(self, show: bool = True, alpha: float = 0.6,
                           size: int = 30, jitter: float = 0.1) -> None:
        """Configure scatter dot overlay settings."""
        self.show_scatter_dots = show
        self.scatter_alpha = alpha
        self.scatter_size = size
        self.scatter_jitter = jitter

    def get_color(self, condition: str) -> str:
        """Get color for condition (returns default if not set)."""
        if condition in self.condition_colors:
            return self.condition_colors[condition]
        elif condition in self.DEFAULT_COLORS:
            return self.DEFAULT_COLORS[condition]
        else:
            return self._generate_default_color(condition)

    def _generate_default_color(self, condition: str) -> str:
        """Generate a default color based on condition name hash."""
        import colorsys
        hash_val = hash(condition) % 360
        h = hash_val / 360.0
        s = 0.7
        l = 0.6
        # Convert HSL to RGB
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        # Convert to hex
        return '#{:02x}{:02x}{:02x}'.format(int(r * 255), int(g * 255), int(b * 255))

    def get_full_name(self, condition: str) -> str:
        """Get full display name for condition."""
        return self.condition_names.get(condition, condition)

    def apply_base_style(self, ax: plt.Axes) -> None:
        """
        Apply base styling to matplotlib axes.

        Args:
            ax: Matplotlib axes object
        """
        # Remove frame
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(True)  # Show x-axis
        ax.spines['left'].set_visible(True)

        # Increase axis thickness by 0.5 (default is ~0.8, new is 1.3)
        ax.spines['bottom'].set_linewidth(1.3)
        ax.spines['left'].set_linewidth(1.3)

        # Keep x-axis ticks
        ax.tick_params(axis='x', which='both', bottom=True, top=False)

        # Keep y-axis ticks
        ax.tick_params(axis='y', which='both', left=True, right=False)

        # Apply plot range if set
        if self.plot_range:
            ax.set_ylim(self.plot_range)

    def to_dict(self) -> Dict:
        """Export to dict for profile saving."""
        return {
            'condition_colors': self.condition_colors,
            'condition_names': self.condition_names,
            'plotting_order': self.plotting_order,
            'plot_range': list(self.plot_range) if self.plot_range else None,
            'show_scatter_dots': self.show_scatter_dots,
            'scatter_alpha': self.scatter_alpha,
            'scatter_size': self.scatter_size,
            'scatter_jitter': self.scatter_jitter
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'PlotConfig':
        """Load from dict (profile loading)."""
        config = cls()
        config.condition_colors = data.get('condition_colors', {})
        config.condition_names = data.get('condition_names', {})
        config.plotting_order = data.get('plotting_order', [])
        plot_range = data.get('plot_range')
        config.plot_range = tuple(plot_range) if plot_range else None
        config.show_scatter_dots = data.get('show_scatter_dots', True)
        config.scatter_alpha = data.get('scatter_alpha', 0.6)
        config.scatter_size = data.get('scatter_size', 30)
        config.scatter_jitter = data.get('scatter_jitter', 0.1)
        return config
