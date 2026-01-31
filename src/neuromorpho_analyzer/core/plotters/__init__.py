"""
Plotting engine for neuromorphological data analysis.

This module provides classes for creating publication-quality plots:
- PlotConfig: Configuration for plot styling
- SignificanceAnnotator: Adds significance brackets and stars
- BoxPlotter: Creates box plots with SEM and scatter overlay
- BarPlotter: Creates bar plots with SEM and scatter overlay
- FrequencyPlotter: Creates frequency distribution plots
- PlotExporter: Exports plots at high resolution (800 DPI)
"""

from .plot_config import PlotConfig
from .significance_annotator import SignificanceAnnotator
from .box_plotter import BoxPlotter
from .bar_plotter import BarPlotter
from .frequency_plotter import FrequencyPlotter
from .plot_exporter import PlotExporter

__all__ = [
    'PlotConfig',
    'SignificanceAnnotator',
    'BoxPlotter',
    'BarPlotter',
    'FrequencyPlotter',
    'PlotExporter',
]
