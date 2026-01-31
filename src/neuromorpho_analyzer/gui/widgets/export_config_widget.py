"""Widget for configuring export options."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Set, List

from ...core.exporters import ExportConfig


class ExportConfigWidget(ttk.Frame):
    """Widget for configuring export options.

    Provides checkboxes and inputs for all export settings including:
    - Export formats (Excel, GraphPad, CSV)
    - Plot types (box plots, bar plots, frequency distributions)
    - Plot formats (PNG, TIF, PDF, SVG)
    - DPI setting

    Example:
        widget = ExportConfigWidget(parent=root, callback=on_config_change)
        config = widget.get_config()  # Returns ExportConfig object
    """

    def __init__(self, parent, callback: Optional[Callable] = None):
        """Initialize export config widget.

        Args:
            parent: Parent tkinter widget
            callback: Optional callback when configuration changes
        """
        super().__init__(parent)
        self.callback = callback

        # Export format variables
        self.export_excel_var = tk.BooleanVar(value=True)
        self.export_graphpad_var = tk.BooleanVar(value=False)
        self.export_csv_var = tk.BooleanVar(value=False)
        self.export_stats_var = tk.BooleanVar(value=True)
        self.export_plots_var = tk.BooleanVar(value=True)

        # Plot type variables
        self.plot_boxplot_total_var = tk.BooleanVar(value=True)
        self.plot_boxplot_relative_var = tk.BooleanVar(value=True)
        self.plot_barplot_total_var = tk.BooleanVar(value=True)
        self.plot_barplot_relative_var = tk.BooleanVar(value=True)
        self.plot_freq_count_var = tk.BooleanVar(value=True)
        self.plot_freq_relative_var = tk.BooleanVar(value=True)

        # Plot format variables
        self.plot_png_var = tk.BooleanVar(value=True)
        self.plot_tif_var = tk.BooleanVar(value=True)
        self.plot_pdf_var = tk.BooleanVar(value=False)
        self.plot_svg_var = tk.BooleanVar(value=False)

        self.plot_dpi_var = tk.IntVar(value=800)

        self._create_widgets()

    def _create_widgets(self):
        """Create all widgets."""
        # Export Formats Section
        formats_frame = ttk.LabelFrame(self, text="Export Formats", padding=10)
        formats_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        ttk.Checkbutton(
            formats_frame, text="Excel (.xlsx)",
            variable=self.export_excel_var,
            command=self._on_change
        ).grid(row=0, column=0, sticky='w')
        ttk.Checkbutton(
            formats_frame, text="GraphPad Prism (.pzfx)",
            variable=self.export_graphpad_var,
            command=self._on_change
        ).grid(row=1, column=0, sticky='w')
        ttk.Checkbutton(
            formats_frame, text="CSV",
            variable=self.export_csv_var,
            command=self._on_change
        ).grid(row=2, column=0, sticky='w')
        ttk.Checkbutton(
            formats_frame, text="Statistical Tables",
            variable=self.export_stats_var,
            command=self._on_change
        ).grid(row=3, column=0, sticky='w')

        # Plot Types Section
        plots_frame = ttk.LabelFrame(self, text="Plot Types", padding=10)
        plots_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)

        ttk.Checkbutton(
            plots_frame, text="Export Plots",
            variable=self.export_plots_var,
            command=self._toggle_plot_options
        ).grid(row=0, column=0, columnspan=2, sticky='w')

        self.plot_options_frame = ttk.Frame(plots_frame)
        self.plot_options_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=20)

        self.plot_checkbuttons = []

        cb = ttk.Checkbutton(
            self.plot_options_frame, text="Box Plot - Total",
            variable=self.plot_boxplot_total_var,
            command=self._on_change
        )
        cb.grid(row=0, column=0, sticky='w')
        self.plot_checkbuttons.append(cb)

        cb = ttk.Checkbutton(
            self.plot_options_frame, text="Box Plot - Relative",
            variable=self.plot_boxplot_relative_var,
            command=self._on_change
        )
        cb.grid(row=1, column=0, sticky='w')
        self.plot_checkbuttons.append(cb)

        cb = ttk.Checkbutton(
            self.plot_options_frame, text="Bar Plot - Total",
            variable=self.plot_barplot_total_var,
            command=self._on_change
        )
        cb.grid(row=2, column=0, sticky='w')
        self.plot_checkbuttons.append(cb)

        cb = ttk.Checkbutton(
            self.plot_options_frame, text="Bar Plot - Relative",
            variable=self.plot_barplot_relative_var,
            command=self._on_change
        )
        cb.grid(row=3, column=0, sticky='w')
        self.plot_checkbuttons.append(cb)

        cb = ttk.Checkbutton(
            self.plot_options_frame, text="Frequency - Count",
            variable=self.plot_freq_count_var,
            command=self._on_change
        )
        cb.grid(row=4, column=0, sticky='w')
        self.plot_checkbuttons.append(cb)

        cb = ttk.Checkbutton(
            self.plot_options_frame, text="Frequency - Relative",
            variable=self.plot_freq_relative_var,
            command=self._on_change
        )
        cb.grid(row=5, column=0, sticky='w')
        self.plot_checkbuttons.append(cb)

        # Plot Format Section
        self.format_frame = ttk.LabelFrame(
            self.plot_options_frame, text="Plot Formats", padding=5
        )
        self.format_frame.grid(row=6, column=0, sticky='ew', pady=5)

        self.format_checkbuttons = []

        cb = ttk.Checkbutton(
            self.format_frame, text="PNG",
            variable=self.plot_png_var,
            command=self._on_change
        )
        cb.grid(row=0, column=0, sticky='w')
        self.format_checkbuttons.append(cb)

        cb = ttk.Checkbutton(
            self.format_frame, text="TIF",
            variable=self.plot_tif_var,
            command=self._on_change
        )
        cb.grid(row=0, column=1, sticky='w')
        self.format_checkbuttons.append(cb)

        cb = ttk.Checkbutton(
            self.format_frame, text="PDF",
            variable=self.plot_pdf_var,
            command=self._on_change
        )
        cb.grid(row=1, column=0, sticky='w')
        self.format_checkbuttons.append(cb)

        cb = ttk.Checkbutton(
            self.format_frame, text="SVG",
            variable=self.plot_svg_var,
            command=self._on_change
        )
        cb.grid(row=1, column=1, sticky='w')
        self.format_checkbuttons.append(cb)

        # DPI Setting
        dpi_frame = ttk.Frame(self.format_frame)
        dpi_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=5)
        ttk.Label(dpi_frame, text="DPI:").grid(row=0, column=0, sticky='w')
        self.dpi_entry = ttk.Entry(
            dpi_frame, textvariable=self.plot_dpi_var, width=10
        )
        self.dpi_entry.grid(row=0, column=1, sticky='w', padx=5)
        self.dpi_entry.bind('<FocusOut>', lambda e: self._on_change())

        self.columnconfigure(0, weight=1)

    def _toggle_plot_options(self):
        """Enable/disable plot options based on export_plots checkbox."""
        state = 'normal' if self.export_plots_var.get() else 'disabled'

        for cb in self.plot_checkbuttons:
            cb.configure(state=state)

        for cb in self.format_checkbuttons:
            cb.configure(state=state)

        self.dpi_entry.configure(state=state)

        self._on_change()

    def _on_change(self):
        """Called when any setting changes."""
        if self.callback:
            self.callback()

    def get_config(self) -> ExportConfig:
        """Get ExportConfig from widget state.

        Returns:
            ExportConfig object with current settings
        """
        plot_types: Set[str] = set()
        if self.plot_boxplot_total_var.get():
            plot_types.add('boxplot_total')
        if self.plot_boxplot_relative_var.get():
            plot_types.add('boxplot_relative')
        if self.plot_barplot_total_var.get():
            plot_types.add('barplot_total')
        if self.plot_barplot_relative_var.get():
            plot_types.add('barplot_relative')
        if self.plot_freq_count_var.get():
            plot_types.add('frequency_count')
        if self.plot_freq_relative_var.get():
            plot_types.add('frequency_relative')

        plot_formats: List[str] = []
        if self.plot_png_var.get():
            plot_formats.append('png')
        if self.plot_tif_var.get():
            plot_formats.append('tif')
        if self.plot_pdf_var.get():
            plot_formats.append('pdf')
        if self.plot_svg_var.get():
            plot_formats.append('svg')

        return ExportConfig(
            export_excel=self.export_excel_var.get(),
            export_graphpad=self.export_graphpad_var.get(),
            export_csv=self.export_csv_var.get(),
            export_statistics_tables=self.export_stats_var.get(),
            export_plots=self.export_plots_var.get(),
            plot_types=plot_types,
            plot_formats=plot_formats,
            plot_dpi=self.plot_dpi_var.get()
        )

    def set_config(self, config: ExportConfig):
        """Set widget state from ExportConfig.

        Args:
            config: ExportConfig object to load
        """
        self.export_excel_var.set(config.export_excel)
        self.export_graphpad_var.set(config.export_graphpad)
        self.export_csv_var.set(config.export_csv)
        self.export_stats_var.set(config.export_statistics_tables)
        self.export_plots_var.set(config.export_plots)

        self.plot_boxplot_total_var.set('boxplot_total' in config.plot_types)
        self.plot_boxplot_relative_var.set('boxplot_relative' in config.plot_types)
        self.plot_barplot_total_var.set('barplot_total' in config.plot_types)
        self.plot_barplot_relative_var.set('barplot_relative' in config.plot_types)
        self.plot_freq_count_var.set('frequency_count' in config.plot_types)
        self.plot_freq_relative_var.set('frequency_relative' in config.plot_types)

        self.plot_png_var.set('png' in config.plot_formats)
        self.plot_tif_var.set('tif' in config.plot_formats)
        self.plot_pdf_var.set('pdf' in config.plot_formats)
        self.plot_svg_var.set('svg' in config.plot_formats)

        self.plot_dpi_var.set(config.plot_dpi)

        self._toggle_plot_options()
