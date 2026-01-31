#!/usr/bin/env python3
"""Test script to verify all data importers functionality."""

import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from neuromorpho_analyzer.core.importers import (
    CSVImporter,
    JSONImporter,
    ExcelImporter,
    UnifiedImporter,
    HeaderScanner,
    ParameterMapper
)


def test_csv_importer():
    """Test CSV importer."""
    print("=" * 70)
    print("Test 1: CSV Importer")
    print("=" * 70)

    test_file = Path(__file__).parent / 'test_data' / '002_GST_005L.csv'

    if not test_file.exists():
        print(f"  ⚠ Test file not found: {test_file}")
        return False

    try:
        # Import all columns
        df = CSVImporter.import_file(test_file)
        print(f"\n  Imported {len(df)} rows from CSV")
        print(f"  Columns: {list(df.columns)}")
        print(f"\n  First row:")
        print(f"    {df.iloc[0].to_dict()}")

        # Import selected columns only
        df_selected = CSVImporter.import_file(
            test_file,
            selected_parameters=['Length', 'Total Volume']
        )
        print(f"\n  Selected parameters only: {list(df_selected.columns)}")

        # Get row count
        row_count = CSVImporter.get_row_count(test_file)
        print(f"  Row count: {row_count}")

        print("\n  ✓ CSV Importer working!")
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_json_importer():
    """Test JSON importer."""
    print("\n" + "=" * 70)
    print("Test 2: JSON Importer")
    print("=" * 70)

    test_file = Path(__file__).parent / 'test_data' / '003_Treatment_010T.json'

    if not test_file.exists():
        print(f"  ⚠ Test file not found: {test_file}")
        return False

    try:
        # Import all columns
        df = JSONImporter.import_file(test_file)
        print(f"\n  Imported {len(df)} measurements from JSON")
        print(f"  Columns: {list(df.columns)}")
        print(f"\n  First measurement:")
        print(f"    {df.iloc[0].to_dict()}")

        # Import selected columns only
        df_selected = JSONImporter.import_file(
            test_file,
            selected_parameters=['Length', 'Branch Points']
        )
        print(f"\n  Selected parameters only: {list(df_selected.columns)}")

        # Get measurement count
        count = JSONImporter.get_measurement_count(test_file)
        print(f"  Measurement count: {count}")

        print("\n  ✓ JSON Importer working!")
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_excel_importer():
    """Test Excel importer (both XLS and XLSX)."""
    print("\n" + "=" * 70)
    print("Test 3: Excel Importer")
    print("=" * 70)

    test_files = [
        ('001_Control_001.xlsx', 'XLSX'),
        ('004_Control_002.xls', 'XLS')
    ]

    results = []

    for filename, format_name in test_files:
        test_file = Path(__file__).parent / 'test_data' / filename

        print(f"\n  Testing {format_name} format: {filename}")

        if not test_file.exists():
            print(f"    ⚠ File not found")
            results.append(False)
            continue

        try:
            # Import all columns
            df = ExcelImporter.import_file(test_file)
            print(f"    Imported {len(df)} rows")
            print(f"    Columns: {list(df.columns)}")

            # Import selected columns
            df_selected = ExcelImporter.import_file(
                test_file,
                selected_parameters=['Length', 'Total Volume']
            )
            print(f"    Selected: {list(df_selected.columns)}")

            results.append(True)
            print(f"    ✓ {format_name} import working!")

        except Exception as e:
            print(f"    ✗ Error: {e}")
            results.append(False)

    if any(results):
        print("\n  ✓ Excel Importer working!")
        return True
    else:
        print("\n  ✗ Excel Importer failed")
        return False


def test_unified_importer():
    """Test unified importer with all formats."""
    print("\n" + "=" * 70)
    print("Test 4: Unified Importer (Auto-detect format)")
    print("=" * 70)

    test_files = [
        '001_Control_001.xlsx',
        '002_GST_005L.csv',
        '003_Treatment_010T.json',
        '004_Control_002.xls'
    ]

    results = []

    for filename in test_files:
        test_file = Path(__file__).parent / 'test_data' / filename

        if not test_file.exists():
            results.append(False)
            continue

        try:
            # Auto-detect and import
            df = UnifiedImporter.import_file(test_file)
            print(f"\n  {filename}: {len(df)} rows, {len(df.columns)} columns")

            # Check if supported
            is_supported = UnifiedImporter.is_supported_format(test_file)
            print(f"    Format supported: {is_supported}")

            results.append(True)

        except Exception as e:
            print(f"\n  {filename}: ✗ Error: {e}")
            results.append(False)

    if any(results):
        print("\n  ✓ Unified Importer working!")
        return True
    else:
        print("\n  ✗ Unified Importer failed")
        return False


def test_parameter_mapper_integration():
    """Test integration with ParameterMapper."""
    print("\n" + "=" * 70)
    print("Test 5: ParameterMapper Integration")
    print("=" * 70)

    test_file = Path(__file__).parent / 'test_data' / '002_GST_005L.csv'

    if not test_file.exists():
        print(f"  ⚠ Test file not found")
        return False

    try:
        # Scan headers from file
        headers = HeaderScanner.scan_headers(test_file)
        print(f"\n  Available headers: {headers}")

        # Create ParameterMapper
        mapper = ParameterMapper(headers)
        mapper.select_parameters(['Length', 'Branch Points', 'Total Volume'])
        print(f"  Selected parameters: {mapper.get_all_parameters()}")

        # Import using ParameterMapper
        df = UnifiedImporter.import_file(test_file, parameter_mapper=mapper)
        print(f"\n  Imported {len(df)} rows")
        print(f"  Columns: {list(df.columns)}")

        # Verify only selected parameters were imported
        expected = set(mapper.get_all_parameters())
        actual = set(df.columns)
        if expected == actual:
            print(f"  ✓ Correct columns imported!")
        else:
            print(f"  ✗ Column mismatch: expected {expected}, got {actual}")
            return False

        print("\n  ✓ ParameterMapper integration working!")
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_multiple_files():
    """Test importing multiple files at once."""
    print("\n" + "=" * 70)
    print("Test 6: Import Multiple Files")
    print("=" * 70)

    test_files = [
        Path(__file__).parent / 'test_data' / '001_Control_001.xlsx',
        Path(__file__).parent / 'test_data' / '002_GST_005L.csv',
        Path(__file__).parent / 'test_data' / '003_Treatment_010T.json'
    ]

    # Filter to only existing files
    existing_files = [f for f in test_files if f.exists()]

    if not existing_files:
        print(f"  ⚠ No test files found")
        return False

    try:
        # Import all files and combine
        df_combined = UnifiedImporter.import_multiple_files(
            existing_files,
            add_source_column=True
        )

        print(f"\n  Combined data from {len(existing_files)} files")
        print(f"  Total rows: {len(df_combined)}")
        print(f"  Columns: {list(df_combined.columns)}")

        # Check source column
        if 'source_file' in df_combined.columns:
            sources = df_combined['source_file'].unique()
            print(f"\n  Source files in data: {list(sources)}")
            print(f"  ✓ Source tracking working!")
        else:
            print(f"  ✗ Source column missing")
            return False

        print("\n  ✓ Multiple file import working!")
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def run_all_tests():
    """Run all tests and display summary."""
    tests = [
        ("CSV Importer", test_csv_importer),
        ("JSON Importer", test_json_importer),
        ("Excel Importer", test_excel_importer),
        ("Unified Importer", test_unified_importer),
        ("ParameterMapper Integration", test_parameter_mapper_integration),
        ("Multiple Files Import", test_multiple_files),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' failed with error: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)

    print(f"\nTotal tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed/Skipped: {failed}")

    print("\nDetailed Results:")
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL/SKIP"
        print(f"  {status}: {name}")

    if passed == len(results):
        print("\n" + "=" * 70)
        print("✓ All tests passed! All importers working correctly!")
        print("=" * 70)
    elif passed > 0:
        print("\n" + "=" * 70)
        print(f"⚠ {passed}/{len(results)} tests passed")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("✗ All tests failed")
        print("=" * 70)


if __name__ == '__main__':
    run_all_tests()
