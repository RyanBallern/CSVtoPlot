"""Statistical analysis engine for neuromorphological data."""

from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
from scipy import stats
from dataclasses import dataclass


@dataclass
class StatisticalTest:
    """Results from a statistical test."""
    test_name: str
    statistic: float
    p_value: float
    significant: bool
    alpha: float = 0.05
    additional_info: Dict[str, Any] = None

    def __repr__(self) -> str:
        sig_str = "significant" if self.significant else "not significant"
        return f"{self.test_name}: statistic={self.statistic:.4f}, p={self.p_value:.4f} ({sig_str})"


@dataclass
class NormalityTest:
    """Results from normality testing."""
    test_name: str
    statistic: float
    p_value: float
    is_normal: bool
    alpha: float = 0.05

    def __repr__(self) -> str:
        normal_str = "normal" if self.is_normal else "not normal"
        return f"{self.test_name}: statistic={self.statistic:.4f}, p={self.p_value:.4f} ({normal_str})"


@dataclass
class PostHocTest:
    """Results from post-hoc pairwise comparisons."""
    group1: str
    group2: str
    mean_diff: float
    p_value: float
    significant: bool
    confidence_interval: Tuple[float, float] = None

    def __repr__(self) -> str:
        sig_str = "***" if self.significant else "ns"
        return f"{self.group1} vs {self.group2}: Δ={self.mean_diff:.4f}, p={self.p_value:.4f} {sig_str}"


class StatisticsEngine:
    """
    Comprehensive statistical analysis engine.

    Features:
    - Normality testing (Shapiro-Wilk)
    - Parametric t-test (independent samples)
    - Non-parametric t-test (Mann-Whitney U)
    - One-way ANOVA
    - Post-hoc tests (Tukey HSD)
    - Automatic test selection based on conditions
    """

    def __init__(self, alpha: float = 0.05):
        """
        Initialize statistics engine.

        Args:
            alpha: Significance level (default: 0.05)
        """
        self.alpha = alpha

    def test_normality(
        self,
        data: pd.Series,
        test: str = 'shapiro'
    ) -> NormalityTest:
        """
        Test if data follows normal distribution.

        Args:
            data: Data to test
            test: Test to use ('shapiro' or 'kstest')

        Returns:
            NormalityTest result
        """
        # Remove NaN values
        data_clean = data.dropna()

        if len(data_clean) < 3:
            # Not enough data for normality test
            return NormalityTest(
                test_name=test,
                statistic=np.nan,
                p_value=np.nan,
                is_normal=False,
                alpha=self.alpha
            )

        if test == 'shapiro':
            statistic, p_value = stats.shapiro(data_clean)
            test_name = "Shapiro-Wilk"
        elif test == 'kstest':
            statistic, p_value = stats.kstest(data_clean, 'norm')
            test_name = "Kolmogorov-Smirnov"
        else:
            raise ValueError(f"Unknown normality test: {test}")

        return NormalityTest(
            test_name=test_name,
            statistic=float(statistic),
            p_value=float(p_value),
            is_normal=p_value > self.alpha,
            alpha=self.alpha
        )

    def independent_t_test(
        self,
        group1: pd.Series,
        group2: pd.Series,
        equal_var: bool = True
    ) -> StatisticalTest:
        """
        Perform independent samples t-test (parametric).

        Args:
            group1: First group data
            group2: Second group data
            equal_var: Assume equal variances (Welch's t-test if False)

        Returns:
            StatisticalTest result
        """
        # Remove NaN values
        g1_clean = group1.dropna()
        g2_clean = group2.dropna()

        # Perform t-test
        statistic, p_value = stats.ttest_ind(g1_clean, g2_clean, equal_var=equal_var)

        # Calculate effect size (Cohen's d)
        mean_diff = g1_clean.mean() - g2_clean.mean()
        pooled_std = np.sqrt((g1_clean.std()**2 + g2_clean.std()**2) / 2)
        cohens_d = mean_diff / pooled_std if pooled_std > 0 else np.nan

        test_name = "Independent t-test" if equal_var else "Welch's t-test"

        return StatisticalTest(
            test_name=test_name,
            statistic=float(statistic),
            p_value=float(p_value),
            significant=p_value < self.alpha,
            alpha=self.alpha,
            additional_info={
                'mean_diff': float(mean_diff),
                'cohens_d': float(cohens_d),
                'group1_mean': float(g1_clean.mean()),
                'group2_mean': float(g2_clean.mean()),
                'group1_std': float(g1_clean.std()),
                'group2_std': float(g2_clean.std()),
                'group1_n': len(g1_clean),
                'group2_n': len(g2_clean)
            }
        )

    def mann_whitney_test(
        self,
        group1: pd.Series,
        group2: pd.Series
    ) -> StatisticalTest:
        """
        Perform Mann-Whitney U test (non-parametric alternative to t-test).

        Args:
            group1: First group data
            group2: Second group data

        Returns:
            StatisticalTest result
        """
        # Remove NaN values
        g1_clean = group1.dropna()
        g2_clean = group2.dropna()

        # Perform Mann-Whitney U test
        statistic, p_value = stats.mannwhitneyu(g1_clean, g2_clean, alternative='two-sided')

        return StatisticalTest(
            test_name="Mann-Whitney U test",
            statistic=float(statistic),
            p_value=float(p_value),
            significant=p_value < self.alpha,
            alpha=self.alpha,
            additional_info={
                'group1_median': float(g1_clean.median()),
                'group2_median': float(g2_clean.median()),
                'group1_n': len(g1_clean),
                'group2_n': len(g2_clean)
            }
        )

    def one_way_anova(
        self,
        *groups: pd.Series
    ) -> StatisticalTest:
        """
        Perform one-way ANOVA.

        Args:
            *groups: Variable number of groups to compare

        Returns:
            StatisticalTest result
        """
        # Remove NaN values from each group
        groups_clean = [g.dropna() for g in groups]

        # Perform one-way ANOVA
        statistic, p_value = stats.f_oneway(*groups_clean)

        # Calculate effect size (eta-squared)
        grand_mean = np.mean([g.mean() for g in groups_clean])
        ss_between = sum(len(g) * (g.mean() - grand_mean)**2 for g in groups_clean)
        ss_total = sum(sum((g - grand_mean)**2) for g in groups_clean)
        eta_squared = ss_between / ss_total if ss_total > 0 else np.nan

        return StatisticalTest(
            test_name="One-way ANOVA",
            statistic=float(statistic),
            p_value=float(p_value),
            significant=p_value < self.alpha,
            alpha=self.alpha,
            additional_info={
                'eta_squared': float(eta_squared),
                'num_groups': len(groups_clean),
                'group_means': [float(g.mean()) for g in groups_clean],
                'group_stds': [float(g.std()) for g in groups_clean],
                'group_ns': [len(g) for g in groups_clean]
            }
        )

    def tukey_hsd(
        self,
        data: pd.DataFrame,
        value_col: str,
        group_col: str
    ) -> List[PostHocTest]:
        """
        Perform Tukey HSD post-hoc test after ANOVA.

        Args:
            data: DataFrame with data
            value_col: Column name with values
            group_col: Column name with group labels

        Returns:
            List of PostHocTest results for all pairwise comparisons
        """
        try:
            from statsmodels.stats.multicomp import pairwise_tukeyhsd
        except ImportError:
            raise ImportError("statsmodels required for Tukey HSD. Install with: pip install statsmodels")

        # Remove NaN values
        data_clean = data[[value_col, group_col]].dropna()

        # Perform Tukey HSD
        tukey_result = pairwise_tukeyhsd(
            endog=data_clean[value_col],
            groups=data_clean[group_col],
            alpha=self.alpha
        )

        # Parse results
        post_hoc_tests = []

        # Get group names and statistics
        summary = tukey_result.summary()
        data_rows = summary.data[1:]  # Skip header row

        for row in data_rows:
            group1 = str(row[0])
            group2 = str(row[1])
            mean_diff = float(row[2])
            p_value = float(row[3])
            ci_lower = float(row[4])
            ci_upper = float(row[5])
            reject = row[6]  # Boolean

            post_hoc_tests.append(PostHocTest(
                group1=group1,
                group2=group2,
                mean_diff=mean_diff,
                p_value=p_value,
                significant=bool(reject),
                confidence_interval=(ci_lower, ci_upper)
            ))

        return post_hoc_tests

    def kruskal_wallis(
        self,
        *groups: pd.Series
    ) -> StatisticalTest:
        """
        Perform Kruskal-Wallis H test (non-parametric alternative to ANOVA).

        Args:
            *groups: Variable number of groups to compare

        Returns:
            StatisticalTest result
        """
        # Remove NaN values from each group
        groups_clean = [g.dropna() for g in groups]

        # Perform Kruskal-Wallis H test
        statistic, p_value = stats.kruskal(*groups_clean)

        return StatisticalTest(
            test_name="Kruskal-Wallis H test",
            statistic=float(statistic),
            p_value=float(p_value),
            significant=p_value < self.alpha,
            alpha=self.alpha,
            additional_info={
                'num_groups': len(groups_clean),
                'group_medians': [float(g.median()) for g in groups_clean],
                'group_ns': [len(g) for g in groups_clean]
            }
        )

    def auto_compare(
        self,
        data: pd.DataFrame,
        value_col: str,
        group_col: str,
        parametric: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Automatically select and perform appropriate statistical test.

        Logic:
        - 2 groups: t-test (parametric) or Mann-Whitney U (non-parametric)
        - 3+ groups: ANOVA (parametric) or Kruskal-Wallis (non-parametric)
        - If parametric=None, automatically test normality
        - If ANOVA is significant, perform Tukey HSD post-hoc

        Args:
            data: DataFrame with data
            value_col: Column name with values
            group_col: Column name with group labels
            parametric: Force parametric (True) or non-parametric (False)
                       If None, test normality to decide

        Returns:
            Dictionary with test results and metadata
        """
        # Get groups
        groups = data[group_col].unique()
        num_groups = len(groups)

        if num_groups < 2:
            raise ValueError("Need at least 2 groups for comparison")

        result = {
            'num_groups': num_groups,
            'group_names': list(groups),
            'value_col': value_col,
            'group_col': group_col,
            'normality_tests': {},
            'main_test': None,
            'post_hoc_tests': None,
            'descriptive_stats': {}
        }

        # Calculate descriptive statistics for each group
        for group in groups:
            group_data = data[data[group_col] == group][value_col].dropna()
            result['descriptive_stats'][group] = {
                'n': len(group_data),
                'mean': float(group_data.mean()),
                'std': float(group_data.std()),
                'median': float(group_data.median()),
                'min': float(group_data.min()),
                'max': float(group_data.max())
            }

        # Test normality if parametric not specified
        if parametric is None:
            print(f"Testing normality for each group...")
            all_normal = True

            for group in groups:
                group_data = data[data[group_col] == group][value_col]
                normality = self.test_normality(group_data)
                result['normality_tests'][group] = normality

                if not normality.is_normal:
                    all_normal = False

            parametric = all_normal
            print(f"  → All groups normal: {all_normal}")
            print(f"  → Using {'parametric' if parametric else 'non-parametric'} tests")

        result['parametric'] = parametric

        # Perform appropriate test based on number of groups
        if num_groups == 2:
            # Two groups: t-test or Mann-Whitney U
            group1_data = data[data[group_col] == groups[0]][value_col]
            group2_data = data[data[group_col] == groups[1]][value_col]

            if parametric:
                result['main_test'] = self.independent_t_test(group1_data, group2_data)
                print(f"\nPerformed: Independent t-test")
            else:
                result['main_test'] = self.mann_whitney_test(group1_data, group2_data)
                print(f"\nPerformed: Mann-Whitney U test")

        else:
            # Three or more groups: ANOVA or Kruskal-Wallis
            group_data_list = [data[data[group_col] == g][value_col] for g in groups]

            if parametric:
                result['main_test'] = self.one_way_anova(*group_data_list)
                print(f"\nPerformed: One-way ANOVA")

                # If ANOVA is significant, perform Tukey HSD
                if result['main_test'].significant:
                    print(f"  → ANOVA significant, performing Tukey HSD post-hoc test...")
                    result['post_hoc_tests'] = self.tukey_hsd(data, value_col, group_col)
            else:
                result['main_test'] = self.kruskal_wallis(*group_data_list)
                print(f"\nPerformed: Kruskal-Wallis H test")

        return result

    def two_way_anova(
        self,
        data: pd.DataFrame,
        value_col: str,
        factor1_col: str,
        factor2_col: str
    ) -> Dict[str, Any]:
        """
        Perform two-way ANOVA with two independent factors.

        Args:
            data: DataFrame with data
            value_col: Column name with values
            factor1_col: First factor column (e.g., 'Condition')
            factor2_col: Second factor column (e.g., 'Distance' or 'Depth')

        Returns:
            Dictionary with ANOVA results including main effects and interaction
        """
        try:
            import statsmodels.api as sm
            from statsmodels.formula.api import ols
        except ImportError:
            raise ImportError("statsmodels required for two-way ANOVA. Install with: pip install statsmodels")

        # Remove NaN values
        data_clean = data[[value_col, factor1_col, factor2_col]].dropna()

        # Create formula for ANOVA
        # C() treats columns as categorical
        formula = f'{value_col} ~ C({factor1_col}) + C({factor2_col}) + C({factor1_col}):C({factor2_col})'

        # Fit the model
        model = ols(formula, data=data_clean).fit()

        # Perform ANOVA
        anova_table = sm.stats.anova_lm(model, typ=2)

        # Extract results
        results = {
            'formula': formula,
            'anova_table': anova_table,
            'model': model,
            'effects': {}
        }

        # Parse ANOVA table
        for effect_name in anova_table.index:
            if effect_name != 'Residual':
                f_stat = float(anova_table.loc[effect_name, 'F'])
                p_value = float(anova_table.loc[effect_name, 'PR(>F)'])
                df = float(anova_table.loc[effect_name, 'df'])

                # Determine effect type
                if ':' in effect_name:
                    effect_type = 'interaction'
                else:
                    effect_type = 'main'

                results['effects'][effect_name] = {
                    'type': effect_type,
                    'F': f_stat,
                    'p_value': p_value,
                    'df': df,
                    'significant': p_value < self.alpha
                }

        return results

    def friedman_test(
        self,
        data: pd.DataFrame,
        value_col: str,
        group_col: str,
        subject_col: str
    ) -> StatisticalTest:
        """
        Perform Friedman test (non-parametric repeated measures/two-way ANOVA).

        Used when you have repeated measurements or matched groups.
        For example: multiple parameters measured for each sample.

        Args:
            data: DataFrame with data
            value_col: Column name with values
            group_col: Column with group/condition labels
            subject_col: Column identifying matched subjects/samples

        Returns:
            StatisticalTest result
        """
        # Pivot data to get samples x groups matrix
        pivoted = data.pivot(index=subject_col, columns=group_col, values=value_col)

        # Remove rows with any NaN
        pivoted_clean = pivoted.dropna()

        # Perform Friedman test
        statistic, p_value = stats.friedmanchisquare(*[pivoted_clean[col] for col in pivoted_clean.columns])

        return StatisticalTest(
            test_name="Friedman test",
            statistic=float(statistic),
            p_value=float(p_value),
            significant=p_value < self.alpha,
            alpha=self.alpha,
            additional_info={
                'num_groups': len(pivoted_clean.columns),
                'num_subjects': len(pivoted_clean),
                'groups': list(pivoted_clean.columns)
            }
        )

    def compare_multiple_parameters(
        self,
        data: pd.DataFrame,
        parameter_cols: List[str],
        group_col: str,
        parametric: Optional[bool] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare multiple parameters across conditions simultaneously.

        Useful for Sholl analysis, branch depth, or frequency distributions
        where you want to compare multiple measurements (columns) across
        conditions (rows).

        Args:
            data: DataFrame with data
            parameter_cols: List of column names to compare (e.g., distances/depths)
            group_col: Column with group/condition labels
            parametric: Force parametric (True) or non-parametric (False).
                       If None, test normality for each parameter

        Returns:
            Dictionary with results for each parameter
        """
        all_results = {}

        print(f"Comparing {len(parameter_cols)} parameters across conditions...")
        print(f"Parameters: {parameter_cols[:5]}{'...' if len(parameter_cols) > 5 else ''}")

        for param in parameter_cols:
            print(f"\nAnalyzing: {param}")

            # Filter to only this parameter and group column
            param_data = data[[param, group_col]].dropna()

            # Skip if no data
            if len(param_data) == 0:
                print(f"  ⚠ No data for {param}, skipping")
                continue

            # Perform auto_compare for this parameter
            try:
                result = self.auto_compare(
                    param_data,
                    value_col=param,
                    group_col=group_col,
                    parametric=parametric
                )
                all_results[param] = result

            except Exception as e:
                print(f"  ✗ Error analyzing {param}: {e}")
                continue

        # Summary
        significant_params = [
            param for param, result in all_results.items()
            if result['main_test'].significant
        ]

        print(f"\n" + "=" * 70)
        print(f"Multi-Parameter Comparison Summary")
        print("=" * 70)
        print(f"Total parameters tested: {len(all_results)}")
        print(f"Significant differences: {len(significant_params)}")

        if significant_params:
            print(f"\nSignificant parameters:")
            for param in significant_params:
                p_val = all_results[param]['main_test'].p_value
                print(f"  {param}: p={p_val:.4f}")

        return all_results

    def compare_across_distances(
        self,
        data: pd.DataFrame,
        distance_cols: List[str],
        condition_col: str,
        parametric: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Compare values across distances/depths for Sholl or branch analysis.

        Convenience wrapper for compare_multiple_parameters specifically
        for distance/depth-based analyses.

        Args:
            data: DataFrame with Sholl or branch data
            distance_cols: List of distance/depth column names
            condition_col: Column with condition labels
            parametric: Force parametric/non-parametric or auto-detect

        Returns:
            Dictionary with results for each distance
        """
        print("=" * 70)
        print("Distance/Depth Analysis")
        print("=" * 70)

        return self.compare_multiple_parameters(
            data,
            parameter_cols=distance_cols,
            group_col=condition_col,
            parametric=parametric
        )

    def format_results_summary(self, results: Dict[str, Any]) -> str:
        """
        Format statistical results as a readable summary.

        Args:
            results: Results dictionary from auto_compare()

        Returns:
            Formatted string summary
        """
        lines = []
        lines.append("=" * 70)
        lines.append("STATISTICAL ANALYSIS SUMMARY")
        lines.append("=" * 70)

        # Groups info
        lines.append(f"\nGroups compared: {results['num_groups']}")
        lines.append(f"Group names: {', '.join(results['group_names'])}")
        lines.append(f"Analysis type: {'Parametric' if results['parametric'] else 'Non-parametric'}")

        # Descriptive statistics
        lines.append("\nDescriptive Statistics:")
        lines.append("-" * 70)
        for group, stats in results['descriptive_stats'].items():
            lines.append(f"\n{group}:")
            lines.append(f"  n = {stats['n']}")
            lines.append(f"  Mean ± SD: {stats['mean']:.3f} ± {stats['std']:.3f}")
            lines.append(f"  Median: {stats['median']:.3f}")
            lines.append(f"  Range: [{stats['min']:.3f}, {stats['max']:.3f}]")

        # Normality tests
        if results['normality_tests']:
            lines.append("\nNormality Tests:")
            lines.append("-" * 70)
            for group, test in results['normality_tests'].items():
                status = "✓ Normal" if test.is_normal else "✗ Not normal"
                lines.append(f"{group}: {status} (p={test.p_value:.4f})")

        # Main test
        lines.append("\nMain Statistical Test:")
        lines.append("-" * 70)
        main_test = results['main_test']
        lines.append(str(main_test))

        if main_test.additional_info:
            for key, value in main_test.additional_info.items():
                if isinstance(value, (int, float)):
                    lines.append(f"  {key}: {value:.4f}")
                else:
                    lines.append(f"  {key}: {value}")

        # Post-hoc tests
        if results['post_hoc_tests']:
            lines.append("\nPost-hoc Tests (Tukey HSD):")
            lines.append("-" * 70)
            for test in results['post_hoc_tests']:
                sig = "***" if test.significant else "ns"
                lines.append(f"{test.group1} vs {test.group2}: p={test.p_value:.4f} {sig}")
                lines.append(f"  Mean difference: {test.mean_diff:.4f}")
                if test.confidence_interval:
                    lines.append(f"  95% CI: [{test.confidence_interval[0]:.4f}, {test.confidence_interval[1]:.4f}]")

        lines.append("\n" + "=" * 70)

        return "\n".join(lines)
