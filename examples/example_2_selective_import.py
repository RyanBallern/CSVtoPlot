#!/usr/bin/env python3
"""
Example 2: Selective Parameter Import

This example demonstrates:
1. Scanning headers from a file
2. Selecting specific parameters
3. Importing only selected parameters
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from neuromorpho_analyzer.core.importers import (
    HeaderScanner,
    ParameterMapper,
    UnifiedImporter
)


def main():
    """Selective import example."""
    print("=" * 70)
    print("Example 2: Selective Parameter Import")
    print("=" * 70)

    # Path to data file
    data_file = Path(__file__).parent.parent / 'test_data' / '002_GST_005L.csv'

    if not data_file.exists():
        print(f"\nError: File not found: {data_file}")
        return

    # Step 1: Scan available headers
    print(f"\nScanning headers from: {data_file.name}")
    headers = HeaderScanner.scan_headers(data_file)

    print(f"\nAvailable parameters ({len(headers)}):")
    for i, header in enumerate(headers, 1):
        print(f"  {i}. {header}")

    # Step 2: Select specific parameters
    mapper = ParameterMapper(headers)

    # Select only Length and Total Volume
    parameters_to_import = ['Length', 'Total Volume']
    mapper.select_parameters(parameters_to_import)

    print(f"\nSelected for import:")
    for param in mapper.get_all_parameters():
        print(f"  - {param}")

    # Step 3: Import with parameter filtering
    print(f"\nImporting data...")
    df = UnifiedImporter.import_file(data_file, parameter_mapper=mapper)

    # Display results
    print(f"\n✓ Successfully imported {len(df)} rows")
    print(f"\nImported columns: {list(df.columns)}")
    print(f"\nData:")
    print(df)

    # Verify only selected parameters were imported
    expected = set(mapper.get_all_parameters())
    actual = set(df.columns)

    if expected == actual:
        print(f"\n✓ Correct! Only selected parameters were imported.")
    else:
        print(f"\n✗ Warning: Column mismatch")
        print(f"  Expected: {expected}")
        print(f"  Got: {actual}")


if __name__ == '__main__':
    main()
