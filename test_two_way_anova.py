#!/usr/bin/env python3
"""Test script for two-way ANOVA and multi-parameter comparison."""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from neuromorpho_analyzer.core.processors import StatisticsEngine


def test_two_way_anova():
    """Test two-way ANOVA with two factors."""
    print("=" * 70)
    print("Test 1: Two-Way ANOVA")
    print("=" * 70)

    # Create sample data with two factors
    # Factor 1: Condition (Control, Treatment)
    # Factor 2: Distance (10um, 20um, 30um)
    np.random.seed(42)

    data_list = []
    for condition in ['Control', 'Treatment']:
        for distance in [10, 20, 30]:
            # Different mean for each combination
            if condition == 'Control':
                mean = 100 + distance
            else:
                mean = 120 + distance * 1.5

            values = np.random.normal(mean, 10, 15)

            for val in values:
                data_list.append({
                    'Value': val,
                    'Condition': condition,
                    'Distance': distance
                })

    data = pd.DataFrame(data_list)

    print(f"\nCreated data: {len(data)} observations")
    print(f"Factors: Condition (2 levels), Distance (3 levels)")

    stats_engine = StatisticsEngine(alpha=0.05)

    print("\nPerforming two-way ANOVA...")
    results = stats_engine.two_way_anova(
        data,
        value_col='Value',
        factor1_col='Condition',
        factor2_col='Distance'
    )

    print(f"\nANOVA Results:")
    print(f"Formula: {results['formula']}")
    print(f"\nEffects:")
    for effect_name, effect_data in results['effects'].items():
        sig = "***" if effect_data['significant'] else "ns"
        print(f"  {effect_name} ({effect_data['type']}): F={effect_data['F']:.3f}, p={effect_data['p_value']:.4f} {sig}")

    print("\n✓ Two-way ANOVA working!")
    return True


def test_friedman():
    """Test Friedman test (non-parametric repeated measures)."""
    print("\n" + "=" * 70)
    print("Test 2: Friedman Test (Non-Parametric Repeated Measures)")
    print("=" * 70)

    # Create repeated measures data
    # Same subjects measured under different conditions
    np.random.seed(42)

    data_list = []
    for subject_id in range(1, 21):  # 20 subjects
        for condition in ['Baseline', 'Treatment1', 'Treatment2']:
            # Simulated repeated measurement with increasing values
            if condition == 'Baseline':
                value = np.random.exponential(2) + subject_id * 0.1
            elif condition == 'Treatment1':
                value = np.random.exponential(2.5) + subject_id * 0.1
            else:
                value = np.random.exponential(3) + subject_id * 0.1

            data_list.append({
                'Value': value,
                'Subject': subject_id,
                'Condition': condition
            })

    data = pd.DataFrame(data_list)

    print(f"\nCreated repeated measures data:")
    print(f"  Subjects: 20")
    print(f"  Conditions: 3 (Baseline, Treatment1, Treatment2)")

    stats_engine = StatisticsEngine(alpha=0.05)

    print("\nPerforming Friedman test...")
    result = stats_engine.friedman_test(
        data,
        value_col='Value',
        group_col='Condition',
        subject_col='Subject'
    )

    print(f"\n  {result}")

    if result.additional_info:
        print(f"  Number of subjects: {result.additional_info['num_subjects']}")
        print(f"  Number of groups: {result.additional_info['num_groups']}")

    print("\n✓ Friedman test working!")
    return True


def test_multiple_parameter_comparison():
    """Test comparing multiple parameters across conditions."""
    print("\n" + "=" * 70)
    print("Test 3: Multiple Parameter Comparison (Sholl-like Data)")
    print("=" * 70)

    # Create Sholl-like data
    # Multiple distances, each compared across conditions
    np.random.seed(42)

    distances = [f"{d}um" for d in range(10, 110, 10)]  # 10um, 20um, ..., 100um

    data_list = []
    for condition in ['Control', 'Treatment']:
        for sample in range(15):  # 15 samples per condition
            row = {'Condition': condition}

            # Simulate Sholl data - peak around 40-50um
            for i, dist in enumerate(distances):
                distance_val = (i + 1) * 10
                # Gaussian-like distribution centered at 50um
                base_value = 100 * np.exp(-((distance_val - 50) ** 2) / 500)

                if condition == 'Treatment':
                    base_value *= 1.3  # 30% increase for treatment

                value = base_value + np.random.normal(0, 5)
                row[dist] = max(0, value)  # No negative values

            data_list.append(row)

    data = pd.DataFrame(data_list)

    print(f"\nCreated Sholl-like data:")
    print(f"  Conditions: 2 (Control, Treatment)")
    print(f"  Distances: {len(distances)}")
    print(f"  Samples per condition: 15")

    stats_engine = StatisticsEngine(alpha=0.05)

    print("\nComparing all distances across conditions...")
    results = stats_engine.compare_multiple_parameters(
        data,
        parameter_cols=distances,
        group_col='Condition',
        parametric=None  # Auto-detect
    )

    # Show details for first few distances
    print(f"\nDetailed results for first 3 distances:")
    for dist in distances[:3]:
        if dist in results:
            test_result = results[dist]['main_test']
            sig = "***" if test_result.significant else "ns"
            print(f"  {dist}: {test_result.test_name}, p={test_result.p_value:.4f} {sig}")

    print("\n✓ Multiple parameter comparison working!")
    return True


def test_distance_comparison_wrapper():
    """Test the distance comparison convenience wrapper."""
    print("\n" + "=" * 70)
    print("Test 4: Distance Comparison Wrapper")
    print("=" * 70)

    # Create branch depth data
    np.random.seed(42)

    depths = [f"Depth{d}" for d in range(1, 6)]  # 5 depth levels

    data_list = []
    for condition in ['Control', 'Treatment']:
        for sample in range(20):
            row = {'Condition': condition}

            # Simulate branching that decreases with depth
            for i, depth in enumerate(depths):
                base_value = 50 / (i + 1)  # Decreasing with depth

                if condition == 'Treatment':
                    base_value *= 0.7  # 30% decrease for treatment

                value = base_value + np.random.normal(0, 3)
                row[depth] = max(0, value)

            data_list.append(row)

    data = pd.DataFrame(data_list)

    print(f"\nCreated branch depth data:")
    print(f"  Conditions: 2 (Control, Treatment)")
    print(f"  Depth levels: {len(depths)}")
    print(f"  Samples per condition: 20")

    stats_engine = StatisticsEngine(alpha=0.05)

    results = stats_engine.compare_across_distances(
        data,
        distance_cols=depths,
        condition_col='Condition',
        parametric=True  # Force parametric
    )

    print(f"\n✓ Distance comparison wrapper working!")
    return True


def run_all_tests():
    """Run all tests and display summary."""
    tests = [
        ("Two-Way ANOVA", test_two_way_anova),
        ("Friedman Test", test_friedman),
        ("Multiple Parameter Comparison", test_multiple_parameter_comparison),
        ("Distance Comparison Wrapper", test_distance_comparison_wrapper),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)

    print(f"\nTotal tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed/Skipped: {failed}")

    print("\nDetailed Results:")
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL/SKIP"
        print(f"  {status}: {name}")

    if passed == len(results):
        print("\n" + "=" * 70)
        print("✓ All tests passed! Two-way ANOVA features working!")
        print("=" * 70)
    elif passed > 0:
        print("\n" + "=" * 70)
        print(f"⚠ {passed}/{len(results)} tests passed")
        print("=" * 70)


if __name__ == '__main__':
    run_all_tests()
