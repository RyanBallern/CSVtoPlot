#!/usr/bin/env python3
"""Test script to verify HeaderScanner functionality."""

import sys
from pathlib import Path

# Add src to path so we can import our module
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from neuromorpho_analyzer.core.importers.file_scanner import HeaderScanner


def test_header_scanner():
    """Test the HeaderScanner with different file formats."""
    print("=" * 70)
    print("Testing HeaderScanner")
    print("=" * 70)

    test_dir = Path(__file__).parent / 'test_data'

    # Test files
    test_files = [
        '001_Control_001.xlsx',
        '002_GST_005L.csv',
        '003_Treatment_010T.json',
        '004_Control_002.xls',
    ]

    results = []

    for filename in test_files:
        file_path = test_dir / filename

        print(f"\n{'─' * 70}")
        print(f"Testing: {filename}")
        print(f"{'─' * 70}")

        if not file_path.exists():
            print(f"  ✗ File not found - skipping")
            results.append(('SKIP', filename, 'File not found'))
            continue

        try:
            headers = HeaderScanner.scan_headers(file_path)
            print(f"  ✓ Successfully scanned headers")
            print(f"  Found {len(headers)} columns:")
            for i, header in enumerate(headers, 1):
                print(f"    {i}. {header}")
            results.append(('PASS', filename, len(headers)))

        except ImportError as e:
            print(f"  ✗ Missing dependency: {e}")
            results.append(('MISSING_DEP', filename, str(e)))

        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append(('FAIL', filename, str(e)))

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    passed = sum(1 for r in results if r[0] == 'PASS')
    missing_deps = sum(1 for r in results if r[0] == 'MISSING_DEP')
    failed = sum(1 for r in results if r[0] == 'FAIL')
    skipped = sum(1 for r in results if r[0] == 'SKIP')

    print(f"\n  Passed:          {passed}/{len(test_files)}")
    print(f"  Missing deps:    {missing_deps}/{len(test_files)}")
    print(f"  Failed:          {failed}/{len(test_files)}")
    print(f"  Skipped:         {skipped}/{len(test_files)}")

    if missing_deps > 0:
        print("\n" + "─" * 70)
        print("Missing Dependencies:")
        print("─" * 70)
        print("\nTo install all required packages, run:")
        print("  pip install -r requirements.txt")
        print("\nOr install individually:")
        if any('openpyxl' in str(r[2]) for r in results if r[0] == 'MISSING_DEP'):
            print("  pip install openpyxl     # For XLSX files")
        if any('xlrd' in str(r[2]) for r in results if r[0] == 'MISSING_DEP'):
            print("  pip install xlrd         # For XLS files")
        if any('pandas' in str(r[2]) for r in results if r[0] == 'MISSING_DEP'):
            print("  pip install pandas       # For CSV files")

    if passed > 0:
        print("\n" + "=" * 70)
        print("✓ HeaderScanner is working for available file formats!")
        print("=" * 70)

    return passed, missing_deps, failed, skipped


if __name__ == '__main__':
    test_header_scanner()
