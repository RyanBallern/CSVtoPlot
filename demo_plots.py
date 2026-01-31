"""
Demo script to generate example plots and save them as PNG files.

This demonstrates the plotting engine capabilities by creating:
- Box plot with scatter overlay and significance brackets
- Bar plot with scatter overlay and significance brackets
- Frequency distribution plot
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from neuromorpho_analyzer.core.plotters import (
    PlotConfig, BoxPlotter, BarPlotter, FrequencyPlotter, PlotExporter
)
from neuromorpho_analyzer.core.processors.statistics import StatisticsEngine


def create_demo_plots():
    """Generate and save demo plots."""

    print("=" * 60)
    print("Generating Demo Plots")
    print("=" * 60)
    print()

    # Create output directory
    output_dir = Path(__file__).parent / 'demo_output'
    output_dir.mkdir(exist_ok=True)
    print(f"Output directory: {output_dir}")
    print()

    # Initialize plot exporter
    exporter = PlotExporter(output_dir, dpi=300)  # 300 DPI for faster generation

    # =================================================================
    # Demo 1: Box Plot with 3 conditions
    # =================================================================
    print("Demo 1: Creating Box Plot with 3 conditions...")

    # Create sample data (simulating neuron measurements)
    np.random.seed(42)
    data_box = {
        'Control': pd.Series(np.random.normal(25, 5, 40)),
        'GST': pd.Series(np.random.normal(35, 6, 40)),
        'Treatment': pd.Series(np.random.normal(45, 5, 40)),
    }

    # Prepare for statistics
    df_box = pd.DataFrame({
        'value': np.concatenate([data_box['Control'], data_box['GST'], data_box['Treatment']]),
        'condition': (['Control'] * 40) + (['GST'] * 40) + (['Treatment'] * 40)
    })

    # Run statistical analysis
    stats = StatisticsEngine()
    result_box = stats.auto_compare(df_box, 'value', 'condition')

    # Prepare comparisons for plotting
    comparisons_box = []
    if result_box.get('post_hoc_tests'):
        for comp in result_box['post_hoc_tests']:
            comparisons_box.append({
                'group1': comp.group1,
                'group2': comp.group2,
                'p_value': comp.p_value,
                'significant': comp.significant
            })

    # Configure plot
    config_box = PlotConfig()
    config_box.set_condition_name('Control', 'Control Group')
    config_box.set_condition_name('GST', 'Gastrin Treatment')
    config_box.set_condition_name('Treatment', 'High Dose Treatment')
    config_box.set_plotting_order(['Control', 'GST', 'Treatment'])
    config_box.set_condition_color('Control', '#FFFFFF')
    config_box.set_condition_color('GST', '#D3D3D3')
    config_box.set_condition_color('Treatment', '#A0A0A0')
    config_box.set_scatter_settings(show=True, alpha=0.6, size=30, jitter=0.1)

    # Create box plot
    box_plotter = BoxPlotter(config_box, stats)
    box_fig = box_plotter.create_boxplot(
        data=data_box,
        title='Neuron Soma Size Comparison',
        ylabel='Soma Diameter (μm)',
        comparisons=comparisons_box
    )

    # Save plot
    exporter.export_figure(box_fig, 'demo_1_box_plot', formats=['png'])
    print(f"  ✓ Saved: demo_1_box_plot.png")
    print()

    # =================================================================
    # Demo 2: Bar Plot without scatter overlay
    # =================================================================
    print("Demo 2: Creating Bar Plot without scatter overlay...")

    # Same data, different config
    config_bar = PlotConfig()
    config_bar.set_condition_name('Control', 'Control')
    config_bar.set_condition_name('GST', 'Gastrin')
    config_bar.set_condition_name('Treatment', 'Treatment')
    config_bar.set_plotting_order(['Control', 'GST', 'Treatment'])
    config_bar.set_condition_color('Control', '#4A90E2')  # Blue
    config_bar.set_condition_color('GST', '#F39C12')     # Orange
    config_bar.set_condition_color('Treatment', '#E74C3C')  # Red
    config_bar.set_scatter_settings(show=False)  # No scatter overlay

    # Create bar plot
    bar_plotter = BarPlotter(config_bar, stats)
    bar_fig = bar_plotter.create_barplot(
        data=data_box,
        title='Mean Soma Diameter Across Conditions',
        ylabel='Mean Diameter (μm)',
        comparisons=comparisons_box
    )

    # Save plot
    exporter.export_figure(bar_fig, 'demo_2_bar_plot', formats=['png'])
    print(f"  ✓ Saved: demo_2_bar_plot.png")
    print()

    # =================================================================
    # Demo 3: Box Plot with scatter overlay (2 conditions only)
    # =================================================================
    print("Demo 3: Creating Box Plot with 2 conditions (t-test)...")

    # Create 2-condition data
    np.random.seed(123)
    data_ttest = {
        'Control': pd.Series(np.random.normal(100, 15, 35)),
        'Treated': pd.Series(np.random.normal(130, 18, 35)),
    }

    # Prepare for statistics
    df_ttest = pd.DataFrame({
        'value': np.concatenate([data_ttest['Control'], data_ttest['Treated']]),
        'condition': (['Control'] * 35) + (['Treated'] * 35)
    })

    # Run t-test
    result_ttest = stats.auto_compare(df_ttest, 'value', 'condition')

    comparisons_ttest = [{
        'group1': 'Control',
        'group2': 'Treated',
        'p_value': result_ttest['main_test'].p_value,
        'significant': result_ttest['main_test'].significant
    }]

    # Configure plot
    config_ttest = PlotConfig()
    config_ttest.set_condition_color('Control', '#FFFFFF')
    config_ttest.set_condition_color('Treated', '#90EE90')  # Light green
    config_ttest.set_scatter_settings(show=True, alpha=0.5, size=40, jitter=0.12)

    # Create box plot
    box_plotter_2 = BoxPlotter(config_ttest, stats)
    ttest_fig = box_plotter_2.create_boxplot(
        data=data_ttest,
        title='Dendritic Branch Points',
        ylabel='Number of Branch Points',
        comparisons=comparisons_ttest
    )

    # Save plot
    exporter.export_figure(ttest_fig, 'demo_3_ttest_box', formats=['png'])
    print(f"  ✓ Saved: demo_3_ttest_box.png")
    print()

    # =================================================================
    # Demo 4: Frequency Distribution Plot
    # =================================================================
    print("Demo 4: Creating Frequency Distribution Plot...")

    # Create frequency distributions (simulating Sholl analysis)
    distributions = {
        'Control': pd.DataFrame({
            'bin_start': [0, 20, 40, 60, 80, 100],
            'bin_end': [20, 40, 60, 80, 100, 120],
            'count': [5, 15, 25, 20, 10, 3],
            'relative_freq': [0.064, 0.192, 0.321, 0.256, 0.128, 0.038]
        }),
        'Treated': pd.DataFrame({
            'bin_start': [0, 20, 40, 60, 80, 100],
            'bin_end': [20, 40, 60, 80, 100, 120],
            'count': [3, 12, 30, 28, 15, 8],
            'relative_freq': [0.031, 0.125, 0.313, 0.292, 0.156, 0.083]
        })
    }

    # Configure plot
    config_freq = PlotConfig()
    config_freq.set_condition_color('Control', '#3498DB')  # Blue
    config_freq.set_condition_color('Treated', '#E67E22')  # Orange

    # Create frequency plotter
    freq_plotter = FrequencyPlotter(config_freq)

    # Create count plot
    freq_fig = freq_plotter.create_frequency_plot(
        distributions=distributions,
        title='Sholl Analysis - Intersection Counts',
        value_type='count'
    )

    # Save plot
    exporter.export_figure(freq_fig, 'demo_4_frequency_count', formats=['png'])
    print(f"  ✓ Saved: demo_4_frequency_count.png")
    print()

    # Create relative frequency plot
    freq_fig_rel = freq_plotter.create_frequency_plot(
        distributions=distributions,
        title='Sholl Analysis - Relative Frequency',
        value_type='relative'
    )

    # Save plot
    exporter.export_figure(freq_fig_rel, 'demo_5_frequency_relative', formats=['png'])
    print(f"  ✓ Saved: demo_5_frequency_relative.png")
    print()

    # =================================================================
    # Demo 5: High-resolution export (800 DPI)
    # =================================================================
    print("Demo 6: Creating high-resolution publication plot (800 DPI)...")

    # Create high-res exporter
    exporter_hires = PlotExporter(output_dir, dpi=800)

    # Use the box plot from Demo 1
    config_pub = PlotConfig()
    config_pub.set_condition_name('Control', 'Control')
    config_pub.set_condition_name('GST', 'Gastrin')
    config_pub.set_condition_name('Treatment', 'Treatment')
    config_pub.set_plotting_order(['Control', 'GST', 'Treatment'])
    config_pub.set_condition_color('Control', '#FFFFFF')
    config_pub.set_condition_color('GST', '#CCCCCC')
    config_pub.set_condition_color('Treatment', '#888888')
    config_pub.set_scatter_settings(show=True, alpha=0.4, size=25, jitter=0.08)

    # Create publication-quality box plot
    box_plotter_pub = BoxPlotter(config_pub, stats)
    pub_fig = box_plotter_pub.create_boxplot(
        data=data_box,
        title='Soma Diameter Analysis',
        ylabel='Diameter (μm)',
        comparisons=comparisons_box
    )

    # Save in multiple formats
    exporter_hires.export_figure(pub_fig, 'demo_6_publication_quality', formats=['png', 'tif', 'pdf'])
    print(f"  ✓ Saved: demo_6_publication_quality.png (800 DPI)")
    print(f"  ✓ Saved: demo_6_publication_quality.tif (800 DPI)")
    print(f"  ✓ Saved: demo_6_publication_quality.pdf (vector)")
    print()

    print("=" * 60)
    print("✓ All demo plots generated successfully!")
    print(f"✓ Output location: {output_dir.absolute()}")
    print("=" * 60)
    print()
    print("Generated files:")
    for file in sorted(output_dir.glob('demo_*')):
        size_kb = file.stat().st_size / 1024
        print(f"  - {file.name} ({size_kb:.1f} KB)")


if __name__ == '__main__':
    create_demo_plots()
