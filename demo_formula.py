"""
Demo of formula feature in y-axis labels.

Shows how to add formulas to y-axis titles when values are calculated.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from neuromorpho_analyzer.core.plotters import PlotConfig, BoxPlotter, BarPlotter, PlotExporter
from neuromorpho_analyzer.core.processors.statistics import StatisticsEngine


def demo_formula_feature():
    """Demonstrate formula in y-axis label."""

    print("=" * 60)
    print("Demo: Formula in Y-Axis Label")
    print("=" * 60)
    print()

    # Create output directory
    output_dir = Path.home() / 'Documents' / 'PythonScripts' / 'CSVtoPlot' / 'CSVtoPlot' / 'demo_output'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize plot exporter
    exporter = PlotExporter(output_dir, dpi=300)

    # Create sample data
    np.random.seed(42)
    data = {
        'Control': pd.Series(np.random.normal(100, 15, 30)),
        'Treatment': pd.Series(np.random.normal(120, 18, 30)),
    }

    # Run statistical analysis
    df = pd.DataFrame({
        'value': np.concatenate([data['Control'], data['Treatment']]),
        'condition': (['Control'] * 30) + (['Treatment'] * 30)
    })

    stats = StatisticsEngine()
    result = stats.auto_compare(df, 'value', 'condition')

    comparisons = [{
        'group1': 'Control',
        'group2': 'Treatment',
        'p_value': result['main_test'].p_value,
        'significant': result['main_test'].significant
    }]

    # Configure plot
    config = PlotConfig()
    config.set_condition_color('Control', '#FFFFFF')
    config.set_condition_color('Treatment', '#90EE90')

    # Example 1: Box plot WITHOUT formula
    print("Creating box plot without formula...")
    box_plotter = BoxPlotter(config, stats)
    fig1 = box_plotter.create_boxplot(
        data=data,
        title='Example 1: No Formula',
        ylabel='Cell Count',
        comparisons=comparisons
    )
    exporter.export_figure(fig1, 'demo_formula_1_no_formula', formats=['png'])
    print("  ✓ Saved: demo_formula_1_no_formula.png")
    print()

    # Example 2: Box plot WITH formula
    print("Creating box plot with formula...")
    fig2 = box_plotter.create_boxplot(
        data=data,
        title='Example 2: With Formula',
        ylabel='Cell Count',
        comparisons=comparisons,
        formula='(Total\\ Cells) / (Area\\ in\\ mm^2)'  # Formula in math notation
    )
    exporter.export_figure(fig2, 'demo_formula_2_with_formula', formats=['png'])
    print("  ✓ Saved: demo_formula_2_with_formula.png")
    print()

    # Example 3: Bar plot with formula
    print("Creating bar plot with formula...")
    bar_plotter = BarPlotter(config, stats)
    fig3 = bar_plotter.create_barplot(
        data=data,
        title='Example 3: Bar Plot with Formula',
        ylabel='Density',
        comparisons=comparisons,
        formula='Cells / mm^2'  # Simpler formula
    )
    exporter.export_figure(fig3, 'demo_formula_3_bar_with_formula', formats=['png'])
    print("  ✓ Saved: demo_formula_3_bar_with_formula.png")
    print()

    # Example 4: Complex mathematical formula
    print("Creating plot with complex formula...")
    data2 = {
        'Low': pd.Series(np.random.normal(50, 10, 30)),
        'Medium': pd.Series(np.random.normal(75, 12, 30)),
        'High': pd.Series(np.random.normal(95, 15, 30)),
    }

    df2 = pd.DataFrame({
        'value': np.concatenate([data2['Low'], data2['Medium'], data2['High']]),
        'condition': (['Low'] * 30) + (['Medium'] * 30) + (['High'] * 30)
    })

    result2 = stats.auto_compare(df2, 'value', 'condition')
    comparisons2 = []
    if result2.get('post_hoc_tests'):
        for comp in result2['post_hoc_tests']:
            comparisons2.append({
                'group1': comp.group1,
                'group2': comp.group2,
                'p_value': comp.p_value,
                'significant': comp.significant
            })

    config2 = PlotConfig()
    config2.set_plotting_order(['Low', 'Medium', 'High'])

    box_plotter2 = BoxPlotter(config2, stats)
    fig4 = box_plotter2.create_boxplot(
        data=data2,
        title='Example 4: Complex Formula',
        ylabel='Branching Index',
        comparisons=comparisons2,
        formula='\\frac{N_{branches}}{N_{terminals}} \\times 100'  # LaTeX-style fraction
    )
    exporter.export_figure(fig4, 'demo_formula_4_complex', formats=['png'])
    print("  ✓ Saved: demo_formula_4_complex.png")
    print()

    print("=" * 60)
    print("✓ Formula demo complete!")
    print(f"✓ Output location: {output_dir.absolute()}")
    print("=" * 60)
    print()
    print("Formula examples demonstrated:")
    print("  1. No formula (baseline)")
    print("  2. Simple division formula")
    print("  3. Units-only formula")
    print("  4. Complex LaTeX fraction formula")


if __name__ == '__main__':
    demo_formula_feature()
