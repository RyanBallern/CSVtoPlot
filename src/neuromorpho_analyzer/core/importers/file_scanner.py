"""File scanning and metadata extraction for neuromorphology data files."""

from pathlib import Path
from typing import List, Dict, Optional
import re
import json


class FileScanner:
    """Scans directories for morphology data files and extracts metadata."""

    def __init__(self, directory: Path):
        """
        Initialize the FileScanner.

        Args:
            directory: Path to directory containing data files
        """
        self.directory = Path(directory)
        # Updated pattern to include CSV and JSON
        self.file_pattern = re.compile(
            r'^(\d+)_([A-Za-z]+)_(\d+)([LT]?)\.(xlsx?|csv|json)$'
        )
        self.supported_extensions = {'.xls', '.xlsx', '.csv', '.json'}

    def scan_files(self) -> List[Dict[str, any]]:
        """
        Scan directory and return file metadata.

        Returns:
            List of dicts with: path, experiment_index, condition,
            image_index, dataset_marker, file_format
        """
        files = []
        for ext in self.supported_extensions:
            for file_path in self.directory.glob(f'*{ext}'):
                metadata = self._parse_filename(file_path)
                if metadata:
                    files.append(metadata)
        return files

    def _parse_filename(self, file_path: Path) -> Optional[Dict[str, any]]:
        """
        Parse filename to extract metadata.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file metadata or None if pattern doesn't match
        """
        match = self.file_pattern.match(file_path.name)
        if not match:
            return None

        return {
            'path': file_path,
            'experiment_index': int(match.group(1)),
            'condition': match.group(2),
            'image_index': int(match.group(3)),
            'dataset_marker': match.group(4) or None,  # 'L', 'T', or None
            'file_format': match.group(5)  # 'xls', 'xlsx', 'csv', 'json'
        }

    def detect_datasets(self, files: List[Dict]) -> List[str]:
        """
        Detect if L/T dataset markers are present.

        Args:
            files: List of file metadata dictionaries

        Returns:
            Sorted list of unique dataset markers found
        """
        markers = {f['dataset_marker'] for f in files if f['dataset_marker']}
        return sorted(markers)


class HeaderScanner:
    """Extracts column headers from various file formats."""

    @staticmethod
    def scan_headers(file_path: Path) -> List[str]:
        """
        Scan first file to get available column headers.

        Args:
            file_path: Path to data file

        Returns:
            List of column header names

        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file does not exist
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = file_path.suffix.lower()

        if ext == '.xls':
            return HeaderScanner._scan_xls(file_path)
        elif ext == '.xlsx':
            return HeaderScanner._scan_xlsx(file_path)
        elif ext == '.csv':
            return HeaderScanner._scan_csv(file_path)
        elif ext == '.json':
            return HeaderScanner._scan_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    @staticmethod
    def _scan_xls(file_path: Path) -> List[str]:
        """
        Scan XLS file for headers.

        Args:
            file_path: Path to XLS file

        Returns:
            List of header names from first row
        """
        try:
            import xlrd
        except ImportError:
            raise ImportError("xlrd package required for XLS files. Install with: pip install xlrd")

        workbook = xlrd.open_workbook(file_path)
        sheet = workbook.sheet_by_index(0)
        headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
        return [str(h).strip() for h in headers if h]

    @staticmethod
    def _scan_xlsx(file_path: Path) -> List[str]:
        """
        Scan XLSX file for headers.

        Args:
            file_path: Path to XLSX file

        Returns:
            List of header names from first row
        """
        try:
            from openpyxl import load_workbook
        except ImportError:
            raise ImportError("openpyxl package required for XLSX files. Install with: pip install openpyxl")

        workbook = load_workbook(file_path, read_only=True)
        sheet = workbook.active
        headers = [cell.value for cell in sheet[1]]
        workbook.close()
        return [str(h).strip() for h in headers if h is not None]

    @staticmethod
    def _scan_csv(file_path: Path) -> List[str]:
        """
        Scan CSV file for headers.
        Automatically detects delimiter (comma, semicolon, or tab).

        Args:
            file_path: Path to CSV file

        Returns:
            List of header names from first row
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas package required for CSV files. Install with: pip install pandas")

        # Try multiple delimiters
        for delimiter in [',', ';', '\t']:
            try:
                df = pd.read_csv(file_path, sep=delimiter, nrows=0)
                if len(df.columns) > 1:  # Successfully parsed with multiple columns
                    return [str(col).strip() for col in df.columns]
            except Exception:
                continue

        # Fallback to default comma delimiter (single column is also valid)
        df = pd.read_csv(file_path, nrows=0)
        return [str(col).strip() for col in df.columns]

    @staticmethod
    def _scan_json(file_path: Path) -> List[str]:
        """
        Scan JSON file for headers (keys from first measurement).
        Supports multiple JSON structures:
        - {"measurements": [{...}, {...}]}
        - [{...}, {...}]

        Args:
            file_path: Path to JSON file

        Returns:
            List of keys from first measurement object
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle different JSON structures
        if isinstance(data, dict) and 'measurements' in data:
            measurements_list = data['measurements']
        elif isinstance(data, list):
            measurements_list = data
        else:
            # Single measurement object
            if isinstance(data, dict):
                return list(data.keys())
            return []

        if measurements_list and len(measurements_list) > 0:
            return list(measurements_list[0].keys())
        return []
