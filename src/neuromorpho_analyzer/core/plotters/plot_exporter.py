from pathlib import Path
import matplotlib.pyplot as plt
from typing import List, Dict


class PlotExporter:
    """Exports plots in high-resolution formats."""

    DEFAULT_DPI = 800
    SUPPORTED_FORMATS = ['png', 'tif', 'tiff', 'pdf', 'svg']

    def __init__(self, output_dir: Path, dpi: int = DEFAULT_DPI):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi

    def export_figure(self, fig: plt.Figure,
                     base_name: str,
                     formats: List[str] = ['png', 'tif']) -> List[Path]:
        """
        Export matplotlib figure in multiple formats at 800 DPI.

        Args:
            fig: Matplotlib figure to export
            base_name: Base filename (without extension)
            formats: List of formats to export ['png', 'tif', 'pdf', 'svg']

        Returns:
            List of paths to exported files
        """
        exported_files = []

        for fmt in formats:
            if fmt not in self.SUPPORTED_FORMATS:
                raise ValueError(f"Unsupported format: {fmt}")

            # Normalize format name
            if fmt == 'tiff':
                fmt = 'tif'

            output_path = self.output_dir / f"{base_name}.{fmt}"

            # Export with high DPI
            fig.savefig(output_path,
                       dpi=self.dpi,
                       format=fmt,
                       bbox_inches='tight',
                       facecolor='white',
                       edgecolor='none',
                       transparent=False)

            exported_files.append(output_path)

        return exported_files

    def export_multiple_figures(self, figures: Dict[str, plt.Figure],
                                formats: List[str] = ['png', 'tif']) -> Dict[str, List[Path]]:
        """
        Export multiple figures at once.

        Args:
            figures: Dict mapping base names to figures
            formats: Export formats

        Returns:
            Dict mapping base names to lists of exported file paths
        """
        results = {}
        for name, fig in figures.items():
            results[name] = self.export_figure(fig, name, formats)
        return results
