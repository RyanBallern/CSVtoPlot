"""Find most representative files per condition using Euclidean distance."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path

try:
    from scipy.spatial.distance import euclidean
except ImportError:
    # Fallback implementation
    def euclidean(u, v):
        return np.sqrt(np.sum((np.array(u) - np.array(v)) ** 2))

from ..database.base import DatabaseBase


class RepresentativeFileAnalyzer:
    """Finds most representative files per condition.

    Uses Euclidean distance from condition average to rank files
    by how representative they are of the overall condition.

    Files closest to the average (smallest distance) are most representative.

    Example usage:
        analyzer = RepresentativeFileAnalyzer(database)
        results = analyzer.analyze(
            assay_ids=[1],
            parameters=['Length', 'Volume']
        )
        # results contains ranked files per condition
        analyzer.export_to_csv(results, Path('representative_files.csv'))
    """

    def __init__(self, database: DatabaseBase):
        """Initialize analyzer.

        Args:
            database: Database interface for retrieving measurements
        """
        self.database = database

    def analyze(self, assay_ids: List[int],
                parameters: List[str],
                normalize: bool = True) -> pd.DataFrame:
        """Find representative files for each condition.

        Args:
            assay_ids: List of assay IDs to analyze
            parameters: Parameters to consider for distance calculation
            normalize: Whether to normalize values before calculating distance

        Returns:
            DataFrame with ranked files per condition containing:
            - condition: Condition name
            - file: Source file name
            - distance_from_average: Euclidean distance to condition average
            - rank: Rank within condition (1 = most representative)
        """
        # Get all measurements
        all_dfs = []
        for assay_id in assay_ids:
            df = self.database.get_measurements(assay_id, parameters=parameters)
            if not df.empty:
                all_dfs.append(df)

        if not all_dfs:
            return pd.DataFrame(columns=['condition', 'file', 'distance_from_average', 'rank'])

        df = pd.concat(all_dfs, ignore_index=True)

        # Determine source file column name
        source_col = 'source_file' if 'source_file' in df.columns else 'origin_file'
        if source_col not in df.columns:
            # Try to add a dummy source column
            df['source_file'] = 'unknown'
            source_col = 'source_file'

        results = []

        # Process each condition
        for condition in df['condition'].unique():
            cond_data = df[df['condition'] == condition]

            # Calculate average values for each parameter
            averages = {}
            stds = {}
            for param in parameters:
                param_data = cond_data[cond_data['parameter_name'] == param]['value']
                if len(param_data) > 0:
                    averages[param] = param_data.mean()
                    stds[param] = param_data.std() if param_data.std() > 0 else 1.0
                else:
                    averages[param] = 0
                    stds[param] = 1.0

            # Calculate distance for each file
            files = cond_data[source_col].unique()
            file_distances = []

            for file in files:
                file_data = cond_data[cond_data[source_col] == file]

                # Build vector of parameter values for this file
                file_vector = []
                avg_vector = []
                for param in parameters:
                    param_values = file_data[
                        file_data['parameter_name'] == param
                    ]['value']

                    if len(param_values) > 0:
                        val = param_values.mean()
                    else:
                        val = averages.get(param, 0)

                    avg_val = averages.get(param, 0)

                    # Normalize if requested
                    if normalize and stds.get(param, 1.0) > 0:
                        val = (val - avg_val) / stds[param]
                        avg_val = 0  # After normalization, average is 0

                    file_vector.append(val)
                    avg_vector.append(avg_val)

                # Calculate Euclidean distance
                distance = euclidean(file_vector, avg_vector)

                file_distances.append({
                    'condition': condition,
                    'file': file,
                    'distance_from_average': distance,
                    'n_measurements': len(file_data)
                })

            # Sort by distance (ascending = most representative first)
            file_distances_sorted = sorted(
                file_distances,
                key=lambda x: x['distance_from_average']
            )

            # Add rank
            for rank, item in enumerate(file_distances_sorted, 1):
                item['rank'] = rank
                results.append(item)

        return pd.DataFrame(results)

    def analyze_from_dataframe(self, df: pd.DataFrame,
                                parameters: List[str],
                                condition_col: str = 'condition',
                                source_col: str = 'source_file',
                                param_col: str = 'parameter_name',
                                value_col: str = 'value',
                                normalize: bool = True) -> pd.DataFrame:
        """Find representative files from a DataFrame.

        Args:
            df: DataFrame with measurement data
            parameters: Parameters to consider
            condition_col: Column name for condition
            source_col: Column name for source file
            param_col: Column name for parameter name
            value_col: Column name for values
            normalize: Whether to normalize values

        Returns:
            DataFrame with ranked files per condition
        """
        results = []

        for condition in df[condition_col].unique():
            cond_data = df[df[condition_col] == condition]

            # Calculate averages and stds
            averages = {}
            stds = {}
            for param in parameters:
                param_data = cond_data[cond_data[param_col] == param][value_col]
                if len(param_data) > 0:
                    averages[param] = param_data.mean()
                    stds[param] = param_data.std() if param_data.std() > 0 else 1.0
                else:
                    averages[param] = 0
                    stds[param] = 1.0

            # Calculate distance for each file
            for file in cond_data[source_col].unique():
                file_data = cond_data[cond_data[source_col] == file]

                file_vector = []
                avg_vector = []

                for param in parameters:
                    param_values = file_data[file_data[param_col] == param][value_col]
                    val = param_values.mean() if len(param_values) > 0 else averages.get(param, 0)
                    avg_val = averages.get(param, 0)

                    if normalize and stds.get(param, 1.0) > 0:
                        val = (val - avg_val) / stds[param]
                        avg_val = 0

                    file_vector.append(val)
                    avg_vector.append(avg_val)

                distance = euclidean(file_vector, avg_vector)

                results.append({
                    'condition': condition,
                    'file': file,
                    'distance_from_average': distance,
                    'n_measurements': len(file_data)
                })

        # Sort and rank
        df_results = pd.DataFrame(results)
        if df_results.empty:
            df_results['rank'] = []
            return df_results

        # Add rank within each condition
        df_results['rank'] = df_results.groupby('condition')['distance_from_average'].rank(method='min').astype(int)
        df_results = df_results.sort_values(['condition', 'rank'])

        return df_results

    def get_top_representative(self, results: pd.DataFrame,
                                n: int = 1) -> pd.DataFrame:
        """Get top N most representative files per condition.

        Args:
            results: Results from analyze()
            n: Number of top files to return per condition

        Returns:
            DataFrame with top N files per condition
        """
        return results[results['rank'] <= n].copy()

    def export_to_csv(self, results: pd.DataFrame, output_path: Path) -> Path:
        """Export representative files list to CSV.

        Args:
            results: Results DataFrame from analyze()
            output_path: Path for output CSV file

        Returns:
            Path to created CSV file
        """
        results.to_csv(output_path, index=False)
        return output_path

    def export_to_excel(self, results: pd.DataFrame, output_path: Path) -> Path:
        """Export representative files list to Excel.

        Args:
            results: Results DataFrame from analyze()
            output_path: Path for output Excel file

        Returns:
            Path to created Excel file
        """
        results.to_excel(output_path, index=False)
        return output_path
