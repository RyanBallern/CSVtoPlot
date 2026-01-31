#!/usr/bin/env python3
"""
Example 1: Simple Data Import

This example demonstrates the simplest workflow:
1. Import a single file
2. Display the data
"""

import sys
from pathlib import Path

# Add src to path (adjust if running from different location)
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from neuromorpho_analyzer.core.importers import UnifiedImporter


def main():
    """Simple import example."""
    print("=" * 70)
    print("Example 1: Simple Data Import")
    print("=" * 70)

    # Path to data file (adjust to your file)
    data_file = Path(__file__).parent.parent / 'test_data' / '002_GST_005L.csv'

    if not data_file.exists():
        print(f"\nError: File not found: {data_file}")
        print("Please adjust the path to your data file.")
        return

    # Import the file (auto-detects format)
    print(f"\nImporting file: {data_file.name}")
    df = UnifiedImporter.import_file(data_file)

    # Display results
    print(f"\n✓ Successfully imported {len(df)} rows")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nFirst few rows:")
    print(df.head())

    # Show statistics
    print(f"\nBasic statistics:")
    print(df.describe())


if __name__ == '__main__':
    main()
