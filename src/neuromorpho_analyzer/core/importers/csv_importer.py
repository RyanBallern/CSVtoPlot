"""CSV file importer for neuromorphology data."""

from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd


class CSVImporter:
    """Imports data from CSV files."""

    @staticmethod
    def import_file(
        file_path: Path,
        selected_parameters: Optional[List[str]] = None,
        delimiter: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Import data from a CSV file.

        Args:
            file_path: Path to CSV file
            selected_parameters: List of parameters to import (None = all)
            delimiter: CSV delimiter (None = auto-detect)

        Returns:
            DataFrame with imported data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If selected parameters not found in file
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Auto-detect delimiter if not specified
        if delimiter is None:
            delimiter = CSVImporter._detect_delimiter(file_path)

        # Read the CSV file
        df = pd.read_csv(file_path, sep=delimiter)

        # Filter to selected parameters if specified
        if selected_parameters is not None:
            # Verify all selected parameters exist
            missing = set(selected_parameters) - set(df.columns)
            if missing:
                raise ValueError(f"Parameters not found in file: {missing}")

            # Select only the requested columns
            df = df[selected_parameters]

        return df

    @staticmethod
    def _detect_delimiter(file_path: Path) -> str:
        """
        Auto-detect CSV delimiter.

        Args:
            file_path: Path to CSV file

        Returns:
            Detected delimiter character
        """
        # Try multiple delimiters
        for delimiter in [',', ';', '\t']:
            try:
                df = pd.read_csv(file_path, sep=delimiter, nrows=0)
                if len(df.columns) > 1:  # Successfully parsed
                    return delimiter
            except Exception:
                continue

        # Default to comma
        return ','

    @staticmethod
    def import_file_as_dict(
        file_path: Path,
        selected_parameters: Optional[List[str]] = None,
        delimiter: Optional[str] = None
    ) -> List[Dict[str, any]]:
        """
        Import data from CSV file as list of dictionaries.

        Args:
            file_path: Path to CSV file
            selected_parameters: List of parameters to import (None = all)
            delimiter: CSV delimiter (None = auto-detect)

        Returns:
            List of dictionaries, one per row

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If selected parameters not found in file
        """
        df = CSVImporter.import_file(file_path, selected_parameters, delimiter)
        return df.to_dict('records')

    @staticmethod
    def get_row_count(file_path: Path, delimiter: Optional[str] = None) -> int:
        """
        Get number of data rows in CSV file (excluding header).

        Args:
            file_path: Path to CSV file
            delimiter: CSV delimiter (None = auto-detect)

        Returns:
            Number of data rows
        """
        if delimiter is None:
            delimiter = CSVImporter._detect_delimiter(file_path)

        df = pd.read_csv(file_path, sep=delimiter)
        return len(df)
