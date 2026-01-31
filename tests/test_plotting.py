"""
Test suite for the plotting engine.

Tests PlotConfig, SignificanceAnnotator, BoxPlotter, BarPlotter,
FrequencyPlotter, and PlotExporter.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tempfile import TemporaryDirectory

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from neuromorpho_analyzer.core.plotters import (
    PlotConfig, SignificanceAnnotator, BoxPlotter, BarPlotter,
    FrequencyPlotter, PlotExporter
)
from neuromorpho_analyzer.core.processors.statistics import StatisticsEngine


def test_plot_config():
    """Test PlotConfig functionality."""
    print("Test 1: PlotConfig configuration and serialization")

    config = PlotConfig()

    # Test color setting
    config.set_condition_color('Control', '#FFFFFF')
    config.set_condition_color('Treatment', '#FF0000')
    assert config.get_color('Control') == '#FFFFFF'
    assert config.get_color('Treatment') == '#FF0000'

    # Test RGB color setting
    config.set_condition_colors_from_rgb('GST', (128, 128, 128))
    assert config.get_color('GST') == '#808080'

    # Test condition name mapping
    config.set_condition_name('Ctrl', 'Control Group')
    config.set_condition_name('GST', 'Gastrin Treatment')
    assert config.get_full_name('Ctrl') == 'Control Group'
    assert config.get_full_name('GST') == 'Gastrin Treatment'
    assert config.get_full_name('Unknown') == 'Unknown'  # Fallback

    # Test plotting order
    config.set_plotting_order(['Control', 'GST', 'Treatment'])
    assert config.plotting_order == ['Control', 'GST', 'Treatment']

    # Test plot range
    config.set_plot_range(0, 100)
    assert config.plot_range == (0, 100)

    # Test scatter settings
    config.set_scatter_settings(show=False, alpha=0.8, size=50, jitter=0.2)
    assert config.show_scatter_dots == False
    assert config.scatter_alpha == 0.8
    assert config.scatter_size == 50
    assert config.scatter_jitter == 0.2

    # Test serialization
    data = config.to_dict()
    assert data['condition_colors']['Control'] == '#FFFFFF'
    assert data['condition_names']['Ctrl'] == 'Control Group'
    assert data['plotting_order'] == ['Control', 'GST', 'Treatment']
    assert data['plot_range'] == [0, 100]

    # Test deserialization
    config2 = PlotConfig.from_dict(data)
    assert config2.get_color('Control') == '#FFFFFF'
    assert config2.get_full_name('Ctrl') == 'Control Group'
    assert config2.plot_range == (0, 100)

    print("  ✓ PlotConfig works correctly")


def test_significance_annotator():
    """Test SignificanceAnnotator."""
    print("Test 2: SignificanceAnnotator star notation")

    annotator = SignificanceAnnotator()

    # Test star conversion
    assert annotator.get_significance_stars(0.0001) == '***'
    assert annotator.get_significance_stars(0.005) == '**'
    assert annotator.get_significance_stars(0.03) == '*'
    assert annotator.get_significance_stars(0.1) == ''

    print("  ✓ SignificanceAnnotator star notation works")


def test_box_plotter():
    """Test BoxPlotter."""
    print("Test 3: BoxPlotter with scatter overlay")

    # Create sample data
    np.random.seed(42)
    data = {
        'Control': pd.Series(np.random.normal(10, 2, 30)),
        'Treatment': pd.Series(np.random.normal(15, 2, 30)),
    }

    # Create comparisons
    comparisons = [
        {
            'group1': 'Control',
            'group2': 'Treatment',
            'p_value': 0.001,
            'significant': True
        }
    ]

    # Create config and stats engine
    config = PlotConfig()
    config.set_condition_color('Control', '#FFFFFF')
    config.set_condition_color('Treatment', '#D3D3D3')
    config.set_plotting_order(['Control', 'Treatment'])

    stats = StatisticsEngine()

    # Create plotter
    plotter = BoxPlotter(config, stats)

    # Create plot
    fig = plotter.create_boxplot(
        data=data,
        title='Test Box Plot',
        ylabel='Value',
        comparisons=comparisons
    )

    assert fig is not None
    assert len(fig.axes) == 1

    plt.close(fig)

    print("  ✓ BoxPlotter creates plots correctly")


def test_box_plotter_no_scatter():
    """Test BoxPlotter without scatter overlay."""
    print("Test 4: BoxPlotter without scatter dots")

    # Create sample data
    np.random.seed(42)
    data = {
        'Control': pd.Series(np.random.normal(10, 2, 30)),
        'Treatment': pd.Series(np.random.normal(15, 2, 30)),
    }

    # Create config with scatter disabled
    config = PlotConfig()
    config.set_scatter_settings(show=False)

    stats = StatisticsEngine()
    plotter = BoxPlotter(config, stats)

    # Create plot
    fig = plotter.create_boxplot(
        data=data,
        title='Test Box Plot',
        ylabel='Value',
        comparisons=[]
    )

    assert fig is not None
    plt.close(fig)

    print("  ✓ BoxPlotter without scatter works")


def test_bar_plotter():
    """Test BarPlotter."""
    print("Test 5: BarPlotter with scatter overlay")

    # Create sample data
    np.random.seed(42)
    data = {
        'Control': pd.Series(np.random.normal(10, 2, 30)),
        'GST': pd.Series(np.random.normal(13, 2, 30)),
        'Treatment': pd.Series(np.random.normal(15, 2, 30)),
    }

    # Create comparisons
    comparisons = [
        {
            'group1': 'Control',
            'group2': 'GST',
            'p_value': 0.02,
            'significant': True
        },
        {
            'group1': 'Control',
            'group2': 'Treatment',
            'p_value': 0.001,
            'significant': True
        }
    ]

    # Create config
    config = PlotConfig()
    config.set_condition_name('Control', 'Control Group')
    config.set_condition_name('GST', 'Gastrin Treatment')
    config.set_plotting_order(['Control', 'GST', 'Treatment'])

    stats = StatisticsEngine()
    plotter = BarPlotter(config, stats)

    # Create plot
    fig = plotter.create_barplot(
        data=data,
        title='Test Bar Plot',
        ylabel='Mean Value',
        comparisons=comparisons
    )

    assert fig is not None
    plt.close(fig)

    print("  ✓ BarPlotter creates plots correctly")


def test_frequency_plotter():
    """Test FrequencyPlotter."""
    print("Test 6: FrequencyPlotter with frequency distributions")

    # Create sample frequency distributions
    distributions = {
        'Control': pd.DataFrame({
            'bin_start': [0, 10, 20, 30],
            'bin_end': [10, 20, 30, 40],
            'count': [5, 10, 8, 2],
            'relative_freq': [0.2, 0.4, 0.32, 0.08]
        }),
        'Treatment': pd.DataFrame({
            'bin_start': [0, 10, 20, 30],
            'bin_end': [10, 20, 30, 40],
            'count': [3, 8, 12, 7],
            'relative_freq': [0.1, 0.27, 0.4, 0.23]
        })
    }

    config = PlotConfig()
    config.set_condition_color('Control', '#FFFFFF')
    config.set_condition_color('Treatment', '#D3D3D3')

    plotter = FrequencyPlotter(config)

    # Create count plot
    fig = plotter.create_frequency_plot(
        distributions=distributions,
        title='Frequency Distribution',
        value_type='count'
    )

    assert fig is not None
    plt.close(fig)

    # Create relative frequency plot
    fig2 = plotter.create_frequency_plot(
        distributions=distributions,
        title='Relative Frequency Distribution',
        value_type='relative'
    )

    assert fig2 is not None
    plt.close(fig2)

    print("  ✓ FrequencyPlotter creates plots correctly")


def test_plot_exporter():
    """Test PlotExporter."""
    print("Test 7: PlotExporter high-resolution export")

    with TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        # Create a simple figure
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])
        ax.set_title('Test Plot')

        # Create exporter
        exporter = PlotExporter(output_dir, dpi=800)

        # Export in PNG and TIF
        exported = exporter.export_figure(fig, 'test_plot', formats=['png', 'tif'])

        assert len(exported) == 2
        assert exported[0].exists()
        assert exported[1].exists()
        assert exported[0].suffix == '.png'
        assert exported[1].suffix == '.tif'

        plt.close(fig)

        # Test multiple figures export
        figs = {
            'plot1': plt.figure(),
            'plot2': plt.figure()
        }

        results = exporter.export_multiple_figures(figs, formats=['png'])

        assert len(results) == 2
        assert 'plot1' in results
        assert 'plot2' in results
        assert len(results['plot1']) == 1
        assert results['plot1'][0].exists()

        for fig in figs.values():
            plt.close(fig)

    print("  ✓ PlotExporter exports at high resolution")


def test_integration():
    """Test integrated workflow."""
    print("Test 8: Integrated plotting workflow")

    # Create sample data with 3 conditions
    np.random.seed(42)
    data = {
        'Control': pd.Series(np.random.normal(10, 2, 30)),
        'GST': pd.Series(np.random.normal(13, 2, 30)),
        'Treatment': pd.Series(np.random.normal(16, 2, 30)),
    }

    # Prepare for DataFrame for statistics
    df = pd.DataFrame({
        'value': np.concatenate([data['Control'], data['GST'], data['Treatment']]),
        'condition': (['Control'] * 30) + (['GST'] * 30) + (['Treatment'] * 30)
    })

    # Run statistical analysis
    stats = StatisticsEngine()
    result = stats.auto_compare(df, 'value', 'condition')

    # Prepare comparisons for plotting
    comparisons = []
    if result.get('post_hoc_tests'):
        for comp in result['post_hoc_tests']:
            comparisons.append({
                'group1': comp.group1,
                'group2': comp.group2,
                'p_value': comp.p_value,
                'significant': comp.significant
            })

    # Configure plot
    config = PlotConfig()
    config.set_condition_name('GST', 'Gastrin Treatment')
    config.set_plotting_order(['Control', 'GST', 'Treatment'])
    config.set_condition_color('Control', '#FFFFFF')
    config.set_condition_color('GST', '#D3D3D3')
    config.set_condition_color('Treatment', '#A0A0A0')

    # Create box plot
    box_plotter = BoxPlotter(config, stats)
    box_fig = box_plotter.create_boxplot(
        data=data,
        title='Integrated Test - Box Plot',
        ylabel='Value (units)',
        comparisons=comparisons
    )

    # Create bar plot
    bar_plotter = BarPlotter(config, stats)
    bar_fig = bar_plotter.create_barplot(
        data=data,
        title='Integrated Test - Bar Plot',
        ylabel='Value (units)',
        comparisons=comparisons
    )

    # Export both plots
    with TemporaryDirectory() as tmpdir:
        exporter = PlotExporter(Path(tmpdir), dpi=800)

        exported = exporter.export_multiple_figures(
            {
                'integrated_box': box_fig,
                'integrated_bar': bar_fig
            },
            formats=['png']
        )

        assert len(exported) == 2
        assert exported['integrated_box'][0].exists()
        assert exported['integrated_bar'][0].exists()

    plt.close(box_fig)
    plt.close(bar_fig)

    print("  ✓ Integrated workflow works correctly")


if __name__ == '__main__':
    print("=" * 60)
    print("Testing Plotting Engine")
    print("=" * 60)
    print()

    test_plot_config()
    test_significance_annotator()
    test_box_plotter()
    test_box_plotter_no_scatter()
    test_bar_plotter()
    test_frequency_plotter()
    test_plot_exporter()
    test_integration()

    print()
    print("=" * 60)
    print("✓ All tests passed! Plotting engine working correctly!")
    print("=" * 60)
