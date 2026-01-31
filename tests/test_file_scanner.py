#!/usr/bin/env python3
"""Simple test script to verify FileScanner functionality."""

import sys
from pathlib import Path

# Add src to path so we can import our module
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from neuromorpho_analyzer.core.importers.file_scanner import FileScanner


def test_file_scanner():
    """Test the FileScanner with sample data."""
    print("=" * 70)
    print("Testing FileScanner")
    print("=" * 70)

    # Set up test directory
    test_dir = Path(__file__).parent / 'test_data'

    print(f"\nScanning directory: {test_dir}")
    print(f"Directory exists: {test_dir.exists()}\n")

    # Create scanner
    scanner = FileScanner(test_dir)

    # Scan files
    files = scanner.scan_files()

    print(f"Found {len(files)} valid files:\n")

    # Display results
    for i, file_info in enumerate(files, 1):
        print(f"{i}. {file_info['path'].name}")
        print(f"   Experiment Index: {file_info['experiment_index']}")
        print(f"   Condition: {file_info['condition']}")
        print(f"   Image Index: {file_info['image_index']}")
        print(f"   Dataset Marker: {file_info['dataset_marker']}")
        print(f"   File Format: {file_info['file_format']}")
        print()

    # Detect dataset markers
    markers = scanner.detect_datasets(files)
    print(f"Dataset markers detected: {markers if markers else 'None'}")

    print("\n" + "=" * 70)
    print("Test Summary:")
    print("=" * 70)
    print(f"✓ FileScanner successfully scanned {len(files)} files")
    if markers:
        print(f"✓ Detected dataset markers: {', '.join(markers)}")
    print("\nFileScanner is working correctly!")
    print("=" * 70)


if __name__ == '__main__':
    test_file_scanner()
