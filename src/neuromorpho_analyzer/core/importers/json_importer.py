"""JSON file importer for neuromorphology data."""

from pathlib import Path
from typing import List, Dict, Optional
import json
import pandas as pd


class JSONImporter:
    """Imports data from JSON files."""

    @staticmethod
    def import_file(
        file_path: Path,
        selected_parameters: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Import data from a JSON file.

        Supports multiple JSON structures:
        - {"measurements": [{...}, {...}]}
        - [{...}, {...}]
        - {...} (single measurement)

        Args:
            file_path: Path to JSON file
            selected_parameters: List of parameters to import (None = all)

        Returns:
            DataFrame with imported data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON structure is invalid or parameters not found
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read and parse JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract measurements list
        measurements = JSONImporter._extract_measurements(data)

        if not measurements:
            raise ValueError(f"No measurements found in JSON file: {file_path}")

        # Convert to DataFrame
        df = pd.DataFrame(measurements)

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
    def _extract_measurements(data: any) -> List[Dict]:
        """
        Extract measurements list from various JSON structures.

        Args:
            data: Parsed JSON data

        Returns:
            List of measurement dictionaries
        """
        # Structure: {"measurements": [{...}, {...}]}
        if isinstance(data, dict) and 'measurements' in data:
            return data['measurements']

        # Structure: [{...}, {...}]
        elif isinstance(data, list):
            return data

        # Structure: {...} (single measurement)
        elif isinstance(data, dict):
            return [data]

        return []

    @staticmethod
    def import_file_as_dict(
        file_path: Path,
        selected_parameters: Optional[List[str]] = None
    ) -> List[Dict[str, any]]:
        """
        Import data from JSON file as list of dictionaries.

        Args:
            file_path: Path to JSON file
            selected_parameters: List of parameters to import (None = all)

        Returns:
            List of dictionaries, one per measurement

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON structure is invalid or parameters not found
        """
        df = JSONImporter.import_file(file_path, selected_parameters)
        return df.to_dict('records')

    @staticmethod
    def get_measurement_count(file_path: Path) -> int:
        """
        Get number of measurements in JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            Number of measurements
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        measurements = JSONImporter._extract_measurements(data)
        return len(measurements)
