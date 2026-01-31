"""Export comprehensive analysis results to Excel."""

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

from .parameter_selector import ExportParameterSelector
from ..processors.statistics import StatisticsEngine
from ..database.base import DatabaseBase


class ExcelExporter:
    """Exports comprehensive analysis results to Excel."""

    def __init__(self, parameter_selector: ExportParameterSelector,
                 stats_engine: StatisticsEngine):
        """Initialize Excel exporter.

        Args:
            parameter_selector: Parameter selector for export
            stats_engine: Statistics engine for calculations
        """
        self.param_selector = parameter_selector
        self.stats = stats_engine

    def export(self, assay_ids: List[int], output_dir: Path,
               database: DatabaseBase,
               dataset_split: Optional[Dict[str, str]] = None) -> Path:
        """Export comprehensive Excel file with all parameters and statistics.

        Args:
            assay_ids: List of assay IDs to export
            output_dir: Output directory
            database: Database interface
            dataset_split: Optional dict mapping markers to full names

        Returns:
            Path to created Excel file
        """
        # Get data from all assays
        parameters = self.param_selector.get_selected()
        dfs = []
        for assay_id in assay_ids:
            assay_df = database.get_measurements(assay_id, parameters=parameters)
            if not assay_df.empty:
                assay_df['assay_id'] = assay_id
                dfs.append(assay_df)

        # Combine all data
        if dfs:
            df = pd.concat(dfs, ignore_index=True)
        else:
            df = pd.DataFrame()

        # Create workbook
        wb = Workbook()
        wb.remove(wb.active)  # Remove default sheet

        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        assay_indices = '_'.join(str(aid) for aid in sorted(assay_ids))
        filename = f'analysis_{timestamp}_assays{assay_indices}.xlsx'

        # Create sheets
        self._create_raw_data_sheet(wb, df)
        self._create_summary_stats_sheet(wb, df, parameters)
        self._create_frequency_sheets(wb, df, parameters)

        # Save
        output_path = output_dir / filename
        wb.save(output_path)

        return output_path

    def _create_raw_data_sheet(self, wb: Workbook, df: pd.DataFrame) -> None:
        """Create raw data worksheet.

        Args:
            wb: Workbook to add sheet to
            df: DataFrame with raw data
        """
        ws = wb.create_sheet('Raw Data')

        # Write column headers
        for col_idx, col_name in enumerate(df.columns, 1):
            cell = ws.cell(row=1, column=col_idx, value=col_name)
            cell.font = Font(bold=True, size=11)
            cell.fill = PatternFill(start_color='CCCCCC', end_color='CCCCCC', fill_type='solid')
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Write DataFrame to worksheet
        for r_idx, row in enumerate(df.itertuples(index=False), 2):
            for c_idx, value in enumerate(row, 1):
                cell = ws.cell(row=r_idx, column=c_idx, value=value)
                cell.alignment = Alignment(horizontal='center', vertical='center')

        # Auto-adjust column widths
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column].width = adjusted_width

    def _create_summary_stats_sheet(self, wb: Workbook,
                                     df: pd.DataFrame,
                                     parameters: List[str]) -> None:
        """Create worksheet with statistical summaries.

        Args:
            wb: Workbook to add sheet to
            df: DataFrame with raw data
            parameters: List of parameters to analyze
        """
        ws = wb.create_sheet('Summary Statistics')

        # Headers
        headers = ['Parameter', 'Condition', 'N', 'Mean', 'SEM', 'SD',
                   'Median', 'Min', 'Max']
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = Font(bold=True, size=11)
            cell.fill = PatternFill(start_color='CCCCCC', end_color='CCCCCC', fill_type='solid')
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Calculate stats for each parameter and condition
        row_idx = 2
        for param in parameters:
            param_data = df[df['parameter_name'] == param]
            conditions = param_data['condition'].unique()

            for condition in sorted(conditions):
                cond_data = param_data[
                    param_data['condition'] == condition
                ]['value']

                if len(cond_data) > 0:
                    # Calculate summary statistics
                    import numpy as np
                    n = len(cond_data)
                    mean = cond_data.mean()
                    std = cond_data.std(ddof=1)
                    sem = std / np.sqrt(n) if n > 0 else 0
                    median = cond_data.median()
                    min_val = cond_data.min()
                    max_val = cond_data.max()

                    values = [
                        param,
                        condition,
                        n,
                        round(mean, 3),
                        round(sem, 3),
                        round(std, 3),
                        round(median, 3),
                        round(min_val, 3),
                        round(max_val, 3)
                    ]

                    for col_idx, value in enumerate(values, 1):
                        cell = ws.cell(row=row_idx, column=col_idx, value=value)
                        cell.alignment = Alignment(horizontal='center', vertical='center')

                    row_idx += 1

        # Auto-adjust column widths
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column].width = adjusted_width

    def _create_frequency_sheets(self, wb: Workbook,
                                  df: pd.DataFrame,
                                  parameters: List[str]) -> None:
        """Create frequency distribution worksheets.

        Args:
            wb: Workbook to add sheet to
            df: DataFrame with raw data
            parameters: List of parameters to analyze
        """
        # Create a single sheet for all frequency distributions
        ws = wb.create_sheet('Frequency Distributions')

        # Headers
        headers = ['Parameter', 'Condition', 'Bin Start', 'Bin End', 'Count', 'Percentage']
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = Font(bold=True, size=11)
            cell.fill = PatternFill(start_color='CCCCCC', end_color='CCCCCC', fill_type='solid')
            cell.alignment = Alignment(horizontal='center', vertical='center')

        row_idx = 2

        # Calculate frequency distributions for each parameter
        for param in parameters:
            param_data = df[df['parameter_name'] == param]
            conditions = param_data['condition'].unique()

            # Get global min/max for consistent bins
            all_values = param_data['value'].values
            if len(all_values) == 0:
                continue

            global_min = float(all_values.min())
            global_max = float(all_values.max())

            # Create bins (default 10 bins)
            bin_size = (global_max - global_min) / 10
            bins = [(global_min + i * bin_size, global_min + (i + 1) * bin_size)
                    for i in range(10)]

            for condition in sorted(conditions):
                cond_data = param_data[param_data['condition'] == condition]['value'].values

                if len(cond_data) == 0:
                    continue

                total_count = len(cond_data)

                # Count values in each bin
                for bin_start, bin_end in bins:
                    count = sum(1 for v in cond_data if bin_start <= v < bin_end)
                    percentage = (count / total_count) * 100 if total_count > 0 else 0

                    values = [
                        param,
                        condition,
                        round(bin_start, 2),
                        round(bin_end, 2),
                        count,
                        round(percentage, 2)
                    ]

                    for col_idx, value in enumerate(values, 1):
                        cell = ws.cell(row=row_idx, column=col_idx, value=value)
                        cell.alignment = Alignment(horizontal='center', vertical='center')

                    row_idx += 1

                # Add empty row between conditions
                row_idx += 1

        # Auto-adjust column widths
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column].width = adjusted_width
