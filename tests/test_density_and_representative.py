#!/usr/bin/env python3
"""Tests for Density Calculator and Representative File Analysis (Parts 7-8)."""

import unittest
import tempfile
from pathlib import Path
import pandas as pd
import numpy as np

from src.neuromorpho_analyzer.core.processors import (
    DensityCalculator, DensityConfig, DensityResult,
    RepresentativeFileAnalyzer
)


class TestDensityConfig(unittest.TestCase):
    """Test DensityConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = DensityConfig()
        self.assertAlmostEqual(config.image_area_um2, 12.2647, places=4)
        self.assertAlmostEqual(config.image_area_um2, 3.5021 ** 2, places=4)

    def test_custom_image_area(self):
        """Test custom image area."""
        config = DensityConfig(image_area_um2=100.0)
        self.assertEqual(config.image_area, 100.0)

    def test_pixel_based_area(self):
        """Test pixel-based area calculation."""
        config = DensityConfig(
            pixel_size=1.0,
            image_width=100,
            image_height=100
        )
        self.assertEqual(config.pixel_area, 1.0)
        self.assertEqual(config.image_area, 10000.0)


class TestDensityCalculator(unittest.TestCase):
    """Test DensityCalculator class."""

    def test_default_density_calculation(self):
        """Test density calculation with default config."""
        calc = DensityCalculator()
        result = calc.calculate_density_from_count(count=10, num_images=1)

        self.assertEqual(result.count, 10)
        self.assertAlmostEqual(result.area, 12.2647, places=4)
        # density = 10 / 12.2647 ≈ 0.8153
        self.assertAlmostEqual(result.density, 10 / 12.2647, places=4)

    def test_density_with_multiple_images(self):
        """Test density calculation with multiple images."""
        calc = DensityCalculator()
        result = calc.calculate_density_from_count(count=50, num_images=5)

        self.assertEqual(result.count, 50)
        self.assertAlmostEqual(result.area, 12.2647 * 5, places=4)
        # Same density as single image with proportional count
        expected_density = 50 / (12.2647 * 5)
        self.assertAlmostEqual(result.density, expected_density, places=4)

    def test_density_with_custom_area(self):
        """Test density calculation with custom area."""
        calc = DensityCalculator()
        result = calc.calculate_density(count=25, image_area_um2=100.0)

        self.assertEqual(result.count, 25)
        self.assertEqual(result.area, 100.0)
        self.assertEqual(result.density, 0.25)

    def test_density_conversions(self):
        """Test density unit conversions."""
        calc = DensityCalculator()
        result = calc.calculate_density(count=100, image_area_um2=100.0)

        # 1 structure per μm²
        self.assertEqual(result.density, 1.0)
        # 1,000,000 structures per mm²
        self.assertEqual(result.density_per_mm2, 1_000_000)
        # 100 structures per 100μm²
        self.assertEqual(result.density_per_100um2, 100)

    def test_density_result_to_dict(self):
        """Test DensityResult to_dict method."""
        calc = DensityCalculator()
        result = calc.calculate_density(
            count=10,
            image_area_um2=100.0,
            source_file='test.csv',
            condition='Control'
        )

        data = result.to_dict()
        self.assertEqual(data['count'], 10)
        self.assertEqual(data['area_um2'], 100.0)
        self.assertEqual(data['source_file'], 'test.csv')
        self.assertEqual(data['condition'], 'Control')

    def test_custom_config(self):
        """Test calculator with custom config."""
        config = DensityConfig(image_area_um2=50.0)
        calc = DensityCalculator(config)
        result = calc.calculate_density_from_count(count=25)

        self.assertEqual(result.area, 50.0)
        self.assertEqual(result.density, 0.5)


class TestRepresentativeFileAnalyzer(unittest.TestCase):
    """Test RepresentativeFileAnalyzer class."""

    def setUp(self):
        """Create test data."""
        np.random.seed(42)
        data = []

        # Create data for two conditions with known patterns
        for condition in ['Control', 'Treatment']:
            base_value = 100 if condition == 'Control' else 150

            for file_idx in range(3):
                file_name = f'{condition.lower()}_{file_idx:03d}.csv'
                # File 0 is closest to average, file 2 is furthest
                offset = file_idx * 20

                for i in range(5):
                    data.append({
                        'condition': condition,
                        'source_file': file_name,
                        'parameter_name': 'Length',
                        'value': base_value + offset + np.random.normal(0, 2)
                    })

        self.test_df = pd.DataFrame(data)

    def test_analyze_from_dataframe(self):
        """Test analysis from DataFrame."""
        analyzer = RepresentativeFileAnalyzer(database=None)
        results = analyzer.analyze_from_dataframe(
            self.test_df,
            parameters=['Length'],
            normalize=True
        )

        self.assertIn('condition', results.columns)
        self.assertIn('file', results.columns)
        self.assertIn('distance_from_average', results.columns)
        self.assertIn('rank', results.columns)

        # Each condition should have 3 ranked files
        control_results = results[results['condition'] == 'Control']
        self.assertEqual(len(control_results), 3)
        self.assertEqual(set(control_results['rank']), {1, 2, 3})

    def test_ranking_order(self):
        """Test that files are ranked correctly."""
        analyzer = RepresentativeFileAnalyzer(database=None)
        results = analyzer.analyze_from_dataframe(
            self.test_df,
            parameters=['Length'],
            normalize=True
        )

        # Rank 1 should have smallest distance
        for condition in results['condition'].unique():
            cond_results = results[results['condition'] == condition]
            rank1_distance = cond_results[cond_results['rank'] == 1]['distance_from_average'].values[0]
            rank3_distance = cond_results[cond_results['rank'] == 3]['distance_from_average'].values[0]
            self.assertLess(rank1_distance, rank3_distance)

    def test_get_top_representative(self):
        """Test getting top N representative files."""
        analyzer = RepresentativeFileAnalyzer(database=None)
        results = analyzer.analyze_from_dataframe(
            self.test_df,
            parameters=['Length']
        )

        top1 = analyzer.get_top_representative(results, n=1)
        self.assertEqual(len(top1), 2)  # One per condition

        top2 = analyzer.get_top_representative(results, n=2)
        self.assertEqual(len(top2), 4)  # Two per condition

    def test_export_to_csv(self):
        """Test CSV export."""
        analyzer = RepresentativeFileAnalyzer(database=None)
        results = analyzer.analyze_from_dataframe(
            self.test_df,
            parameters=['Length']
        )

        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            output_path = Path(f.name)

        analyzer.export_to_csv(results, output_path)
        self.assertTrue(output_path.exists())

        # Read back and verify
        loaded = pd.read_csv(output_path)
        self.assertEqual(len(loaded), len(results))

        output_path.unlink()  # Clean up

    def test_multiple_parameters(self):
        """Test analysis with multiple parameters."""
        # Add another parameter to test data
        df = self.test_df.copy()
        volume_data = []
        for _, row in df.iterrows():
            volume_data.append({
                'condition': row['condition'],
                'source_file': row['source_file'],
                'parameter_name': 'Volume',
                'value': row['value'] * 10 + np.random.normal(0, 50)
            })
        df = pd.concat([df, pd.DataFrame(volume_data)], ignore_index=True)

        analyzer = RepresentativeFileAnalyzer(database=None)
        results = analyzer.analyze_from_dataframe(
            df,
            parameters=['Length', 'Volume'],
            normalize=True
        )

        self.assertEqual(len(results), 6)  # 3 files × 2 conditions

    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        analyzer = RepresentativeFileAnalyzer(database=None)
        empty_df = pd.DataFrame(columns=['condition', 'source_file', 'parameter_name', 'value'])

        results = analyzer.analyze_from_dataframe(empty_df, parameters=['Length'])
        self.assertEqual(len(results), 0)


class TestIntegration(unittest.TestCase):
    """Integration tests combining density and representative analysis."""

    def test_density_per_representative_file(self):
        """Test calculating density for representative files."""
        # Create test data
        np.random.seed(42)
        data = []
        for condition in ['Control', 'Treatment']:
            for file_idx in range(3):
                file_name = f'{condition.lower()}_{file_idx:03d}.csv'
                count = 10 + file_idx * 5  # Different counts per file

                for i in range(count):
                    data.append({
                        'condition': condition,
                        'source_file': file_name,
                        'parameter_name': 'Length',
                        'value': np.random.normal(100, 20)
                    })

        df = pd.DataFrame(data)

        # Find representative files
        rep_analyzer = RepresentativeFileAnalyzer(database=None)
        rep_results = rep_analyzer.analyze_from_dataframe(df, parameters=['Length'])

        # Calculate density for each file
        density_calc = DensityCalculator()
        densities = []

        for _, row in rep_results.iterrows():
            result = density_calc.calculate_density_from_count(
                count=row['n_measurements'],
                source_file=row['file'],
                condition=row['condition']
            )
            densities.append(result.to_dict())

        density_df = pd.DataFrame(densities)

        self.assertEqual(len(density_df), 6)
        self.assertIn('density_per_um2', density_df.columns)


if __name__ == '__main__':
    print("=" * 60)
    print("Testing Density Calculator & Representative File Analysis")
    print("=" * 60)
    unittest.main(verbosity=2)
