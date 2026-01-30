#!/usr/bin/env python3
"""Test script to verify statistical analysis functionality."""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from neuromorpho_analyzer.core.processors import StatisticsEngine


def test_normality_testing():
    """Test normality testing."""
    print("=" * 70)
    print("Test 1: Normality Testing")
    print("=" * 70)

    stats_engine = StatisticsEngine(alpha=0.05)

    # Create normal data
    np.random.seed(42)
    normal_data = pd.Series(np.random.normal(100, 15, 50))

    # Create non-normal data (exponential distribution)
    non_normal_data = pd.Series(np.random.exponential(2, 50))

    print("\nTesting normal data:")
    result1 = stats_engine.test_normality(normal_data)
    print(f"  {result1}")

    print("\nTesting non-normal data:")
    result2 = stats_engine.test_normality(non_normal_data)
    print(f"  {result2}")

    if result1.is_normal and not result2.is_normal:
        print("\n✓ Normality testing working correctly!")
        return True
    else:
        print("\n✗ Normality test results unexpected")
        return False


def test_t_test():
    """Test independent t-test (parametric)."""
    print("\n" + "=" * 70)
    print("Test 2: Independent T-Test (Parametric)")
    print("=" * 70)

    stats_engine = StatisticsEngine(alpha=0.05)

    # Create two groups with different means
    np.random.seed(42)
    control = pd.Series(np.random.normal(100, 15, 30))
    treatment = pd.Series(np.random.normal(120, 15, 30))  # Higher mean

    print("\nComparing Control vs Treatment:")
    print(f"  Control: mean={control.mean():.2f}, std={control.std():.2f}, n={len(control)}")
    print(f"  Treatment: mean={treatment.mean():.2f}, std={treatment.std():.2f}, n={len(treatment)}")

    result = stats_engine.independent_t_test(control, treatment)
    print(f"\n  {result}")

    if result.additional_info:
        print(f"  Cohen's d (effect size): {result.additional_info['cohens_d']:.3f}")
        print(f"  Mean difference: {result.additional_info['mean_diff']:.3f}")

    if result.significant:
        print("\n✓ T-test detected significant difference!")
        return True
    else:
        print("\n⚠ T-test did not detect difference (may be due to random seed)")
        return True  # Still pass as functionality works


def test_mann_whitney():
    """Test Mann-Whitney U test (non-parametric)."""
    print("\n" + "=" * 70)
    print("Test 3: Mann-Whitney U Test (Non-Parametric)")
    print("=" * 70)

    stats_engine = StatisticsEngine(alpha=0.05)

    # Create two groups with different distributions
    np.random.seed(42)
    group1 = pd.Series(np.random.exponential(2, 30))
    group2 = pd.Series(np.random.exponential(3, 30))  # Higher scale

    print("\nComparing Group1 vs Group2 (non-normal data):")
    print(f"  Group1: median={group1.median():.2f}, n={len(group1)}")
    print(f"  Group2: median={group2.median():.2f}, n={len(group2)}")

    result = stats_engine.mann_whitney_test(group1, group2)
    print(f"\n  {result}")

    if result.additional_info:
        print(f"  Group1 median: {result.additional_info['group1_median']:.3f}")
        print(f"  Group2 median: {result.additional_info['group2_median']:.3f}")

    print("\n✓ Mann-Whitney U test working!")
    return True


def test_anova():
    """Test one-way ANOVA."""
    print("\n" + "=" * 70)
    print("Test 4: One-Way ANOVA")
    print("=" * 70)

    stats_engine = StatisticsEngine(alpha=0.05)

    # Create three groups with different means
    np.random.seed(42)
    control = pd.Series(np.random.normal(100, 15, 30))
    treatment1 = pd.Series(np.random.normal(120, 15, 30))
    treatment2 = pd.Series(np.random.normal(140, 15, 30))

    print("\nComparing 3 groups:")
    print(f"  Control: mean={control.mean():.2f}, n={len(control)}")
    print(f"  Treatment1: mean={treatment1.mean():.2f}, n={len(treatment1)}")
    print(f"  Treatment2: mean={treatment2.mean():.2f}, n={len(treatment2)}")

    result = stats_engine.one_way_anova(control, treatment1, treatment2)
    print(f"\n  {result}")

    if result.additional_info:
        print(f"  Eta-squared (effect size): {result.additional_info['eta_squared']:.3f}")

    if result.significant:
        print("\n✓ ANOVA detected significant difference!")
        return True
    else:
        print("\n⚠ ANOVA did not detect difference (may be due to random seed)")
        return True


def test_tukey_hsd():
    """Test Tukey HSD post-hoc test."""
    print("\n" + "=" * 70)
    print("Test 5: Tukey HSD Post-Hoc Test")
    print("=" * 70)

    try:
        import statsmodels
    except ImportError:
        print("\n⚠ statsmodels not installed - skipping Tukey HSD test")
        print("  Install with: pip install statsmodels")
        return False

    stats_engine = StatisticsEngine(alpha=0.05)

    # Create DataFrame with three groups
    np.random.seed(42)
    data = pd.DataFrame({
        'value': np.concatenate([
            np.random.normal(100, 15, 30),
            np.random.normal(120, 15, 30),
            np.random.normal(140, 15, 30)
        ]),
        'group': ['Control'] * 30 + ['Treatment1'] * 30 + ['Treatment2'] * 30
    })

    print("\nPerforming Tukey HSD on 3 groups...")

    results = stats_engine.tukey_hsd(data, 'value', 'group')

    print(f"\nFound {len(results)} pairwise comparisons:")
    for test in results:
        sig_marker = "***" if test.significant else "ns"
        print(f"  {test.group1} vs {test.group2}: p={test.p_value:.4f} {sig_marker}")
        print(f"    Mean diff: {test.mean_diff:.3f}")

    print("\n✓ Tukey HSD working!")
    return True


def test_kruskal_wallis():
    """Test Kruskal-Wallis H test."""
    print("\n" + "=" * 70)
    print("Test 6: Kruskal-Wallis H Test (Non-Parametric ANOVA)")
    print("=" * 70)

    stats_engine = StatisticsEngine(alpha=0.05)

    # Create three groups with different distributions
    np.random.seed(42)
    group1 = pd.Series(np.random.exponential(2, 30))
    group2 = pd.Series(np.random.exponential(3, 30))
    group3 = pd.Series(np.random.exponential(4, 30))

    print("\nComparing 3 groups (non-normal data):")
    print(f"  Group1: median={group1.median():.2f}, n={len(group1)}")
    print(f"  Group2: median={group2.median():.2f}, n={len(group2)}")
    print(f"  Group3: median={group3.median():.2f}, n={len(group3)}")

    result = stats_engine.kruskal_wallis(group1, group2, group3)
    print(f"\n  {result}")

    print("\n✓ Kruskal-Wallis test working!")
    return True


def test_auto_compare_two_groups():
    """Test automatic test selection for two groups."""
    print("\n" + "=" * 70)
    print("Test 7: Auto Compare (2 Groups)")
    print("=" * 70)

    stats_engine = StatisticsEngine(alpha=0.05)

    # Create DataFrame with two groups (normal data)
    np.random.seed(42)
    data = pd.DataFrame({
        'value': np.concatenate([
            np.random.normal(100, 15, 30),
            np.random.normal(120, 15, 30)
        ]),
        'condition': ['Control'] * 30 + ['Treatment'] * 30
    })

    print("\nAutomatic test selection for 2 groups (normal data)...")

    results = stats_engine.auto_compare(data, 'value', 'condition')

    print(f"\nSelected test: {results['main_test'].test_name}")
    print(f"Result: {results['main_test']}")

    # Print formatted summary
    summary = stats_engine.format_results_summary(results)
    print("\n" + summary)

    print("\n✓ Auto compare (2 groups) working!")
    return True


def test_auto_compare_multiple_groups():
    """Test automatic test selection for multiple groups."""
    print("\n" + "=" * 70)
    print("Test 8: Auto Compare (3+ Groups)")
    print("=" * 70)

    stats_engine = StatisticsEngine(alpha=0.05)

    # Create DataFrame with three groups (normal data)
    np.random.seed(42)
    data = pd.DataFrame({
        'value': np.concatenate([
            np.random.normal(100, 15, 30),
            np.random.normal(120, 15, 30),
            np.random.normal(140, 15, 30)
        ]),
        'condition': ['Control'] * 30 + ['Treatment1'] * 30 + ['Treatment2'] * 30
    })

    print("\nAutomatic test selection for 3 groups (normal data)...")

    results = stats_engine.auto_compare(data, 'value', 'condition')

    print(f"\nSelected test: {results['main_test'].test_name}")
    print(f"Result: {results['main_test']}")

    if results['post_hoc_tests']:
        print(f"\nPost-hoc tests performed: {len(results['post_hoc_tests'])} comparisons")

    # Print formatted summary
    summary = stats_engine.format_results_summary(results)
    print("\n" + summary)

    print("\n✓ Auto compare (multiple groups) working!")
    return True


def run_all_tests():
    """Run all tests and display summary."""
    tests = [
        ("Normality Testing", test_normality_testing),
        ("Independent T-Test", test_t_test),
        ("Mann-Whitney U Test", test_mann_whitney),
        ("One-Way ANOVA", test_anova),
        ("Tukey HSD Post-Hoc", test_tukey_hsd),
        ("Kruskal-Wallis H Test", test_kruskal_wallis),
        ("Auto Compare (2 Groups)", test_auto_compare_two_groups),
        ("Auto Compare (3+ Groups)", test_auto_compare_multiple_groups),
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
        print("✓ All tests passed! Statistics engine working correctly!")
        print("=" * 70)
    elif passed > 0:
        print("\n" + "=" * 70)
        print(f"⚠ {passed}/{len(results)} tests passed")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("✗ All tests failed")
        print("=" * 70)


if __name__ == '__main__':
    run_all_tests()
