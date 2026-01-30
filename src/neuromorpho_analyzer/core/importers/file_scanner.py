"""File scanning and metadata extraction for neuromorphology data files."""

from pathlib import Path
from typing import List, Dict, Optional
import re


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
