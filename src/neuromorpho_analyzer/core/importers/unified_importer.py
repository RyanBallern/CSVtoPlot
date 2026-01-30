"""Unified importer that works with all supported file formats."""

from pathlib import Path
from typing import List, Dict, Optional, Union
import pandas as pd

from .csv_importer import CSVImporter
from .json_importer import JSONImporter
from .excel_importer import ExcelImporter
from .parameter_mapper import ParameterMapper


class UnifiedImporter:
    """
    Unified importer that automatically detects file format and imports data.

    Integrates FileScanner, HeaderScanner, and ParameterMapper for complete workflow.
    """

    SUPPORTED_EXTENSIONS = {'.xls', '.xlsx', '.csv', '.json'}

    @staticmethod
    def import_file(
        file_path: Path,
        selected_parameters: Optional[List[str]] = None,
        parameter_mapper: Optional[ParameterMapper] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Import data from any supported file format.

        Args:
            file_path: Path to data file
            selected_parameters: List of parameters to import (None = all)
            parameter_mapper: ParameterMapper instance (overrides selected_parameters)
            **kwargs: Additional format-specific arguments
                - delimiter: CSV delimiter
                - sheet_index: Excel sheet index

        Returns:
            DataFrame with imported data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format not supported or parameters not found
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Use ParameterMapper if provided
        if parameter_mapper is not None:
            selected_parameters = parameter_mapper.get_all_parameters()

        # Detect file format and use appropriate importer
        ext = file_path.suffix.lower()

        if ext == '.csv':
            return CSVImporter.import_file(
                file_path,
                selected_parameters,
                delimiter=kwargs.get('delimiter')
            )
        elif ext == '.json':
            return JSONImporter.import_file(
                file_path,
                selected_parameters
            )
        elif ext in {'.xls', '.xlsx'}:
            return ExcelImporter.import_file(
                file_path,
                selected_parameters,
                sheet_index=kwargs.get('sheet_index', 0)
            )
        else:
            raise ValueError(
                f"Unsupported file format: {ext}. "
                f"Supported formats: {', '.join(UnifiedImporter.SUPPORTED_EXTENSIONS)}"
            )

    @staticmethod
    def import_file_as_dict(
        file_path: Path,
        selected_parameters: Optional[List[str]] = None,
        parameter_mapper: Optional[ParameterMapper] = None,
        **kwargs
    ) -> List[Dict[str, any]]:
        """
        Import data from any supported file format as list of dictionaries.

        Args:
            file_path: Path to data file
            selected_parameters: List of parameters to import (None = all)
            parameter_mapper: ParameterMapper instance (overrides selected_parameters)
            **kwargs: Additional format-specific arguments

        Returns:
            List of dictionaries, one per row/measurement

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format not supported or parameters not found
        """
        df = UnifiedImporter.import_file(
            file_path,
            selected_parameters,
            parameter_mapper,
            **kwargs
        )
        return df.to_dict('records')

    @staticmethod
    def import_multiple_files(
        file_paths: List[Path],
        selected_parameters: Optional[List[str]] = None,
        parameter_mapper: Optional[ParameterMapper] = None,
        add_source_column: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """
        Import and combine data from multiple files.

        Args:
            file_paths: List of file paths to import
            selected_parameters: List of parameters to import (None = all)
            parameter_mapper: ParameterMapper instance (overrides selected_parameters)
            add_source_column: If True, add 'source_file' column with filename
            **kwargs: Additional format-specific arguments

        Returns:
            Combined DataFrame with data from all files

        Raises:
            FileNotFoundError: If any file doesn't exist
            ValueError: If any file format not supported
        """
        all_data = []

        for file_path in file_paths:
            df = UnifiedImporter.import_file(
                file_path,
                selected_parameters,
                parameter_mapper,
                **kwargs
            )

            if add_source_column:
                df['source_file'] = Path(file_path).name

            all_data.append(df)

        # Combine all dataframes
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        else:
            return pd.DataFrame()

    @staticmethod
    def get_row_count(file_path: Path, **kwargs) -> int:
        """
        Get number of data rows/measurements in file.

        Args:
            file_path: Path to data file
            **kwargs: Format-specific arguments

        Returns:
            Number of data rows
        """
        file_path = Path(file_path)
        ext = file_path.suffix.lower()

        if ext == '.csv':
            return CSVImporter.get_row_count(
                file_path,
                delimiter=kwargs.get('delimiter')
            )
        elif ext == '.json':
            return JSONImporter.get_measurement_count(file_path)
        elif ext in {'.xls', '.xlsx'}:
            return ExcelImporter.get_row_count(
                file_path,
                sheet_index=kwargs.get('sheet_index', 0)
            )
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    @staticmethod
    def is_supported_format(file_path: Union[Path, str]) -> bool:
        """
        Check if file format is supported.

        Args:
            file_path: Path to file

        Returns:
            True if format is supported, False otherwise
        """
        ext = Path(file_path).suffix.lower()
        return ext in UnifiedImporter.SUPPORTED_EXTENSIONS
