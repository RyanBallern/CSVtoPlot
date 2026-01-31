#!/usr/bin/env python3
"""Test script to verify database functionality."""

import sys
from pathlib import Path
import pandas as pd

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from neuromorpho_analyzer.core.database import SQLiteDatabase
from neuromorpho_analyzer.core.models import Assay, Measurement
from neuromorpho_analyzer.core.importers import UnifiedImporter


def test_basic_database_operations():
    """Test basic database CRUD operations."""
    print("=" * 70)
    print("Test 1: Basic Database Operations")
    print("=" * 70)

    # Use a temporary test database
    db_path = Path(__file__).parent / 'test_data' / 'test.db'
    if db_path.exists():
        db_path.unlink()  # Remove if exists

    try:
        with SQLiteDatabase(db_path) as db:
            # Create an assay
            assay_id = db.insert_assay(
                name="Test Experiment 1",
                description="Testing database functionality"
            )
            print(f"\n  Created assay with ID: {assay_id}")

            # Get the assay back
            assay = db.get_assay(assay_id)
            print(f"  Retrieved assay: {assay['name']}")

            # List all assays
            assays = db.list_assays()
            print(f"  Total assays in database: {len(assays)}")

            print("\n  ✓ Basic database operations working!")
            return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    finally:
        # Cleanup
        if db_path.exists():
            db_path.unlink()


def test_measurement_storage():
    """Test storing and retrieving measurements."""
    print("\n" + "=" * 70)
    print("Test 2: Measurement Storage")
    print("=" * 70)

    db_path = Path(__file__).parent / 'test_data' / 'test.db'
    if db_path.exists():
        db_path.unlink()

    try:
        with SQLiteDatabase(db_path) as db:
            # Create assay
            assay_id = db.insert_assay("Dendrite Analysis")
            print(f"\n  Created assay ID: {assay_id}")

            # Create sample measurements
            measurements = pd.DataFrame({
                'Length': [125.5, 142.8, 98.3],
                'Branch Points': [5, 6, 4],
                'Total Volume': [450.2, 520.5, 380.7]
            })

            # Insert measurements
            count = db.insert_measurements(
                assay_id=assay_id,
                measurements=measurements,
                source_file='test_file.csv',
                condition='Control'
            )
            print(f"  Inserted {count} measurements")

            # Get measurements back
            retrieved = db.get_measurements(assay_id)
            print(f"  Retrieved {len(retrieved)} measurements")
            print(f"  Columns: {list(retrieved.columns)}")

            # Get measurement count
            total = db.get_measurement_count(assay_id)
            print(f"  Total measurement count: {total}")

            print("\n  ✓ Measurement storage working!")
            return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if db_path.exists():
            db_path.unlink()


def test_conditions_and_filtering():
    """Test condition filtering and parameter selection."""
    print("\n" + "=" * 70)
    print("Test 3: Conditions and Filtering")
    print("=" * 70)

    db_path = Path(__file__).parent / 'test_data' / 'test.db'
    if db_path.exists():
        db_path.unlink()

    try:
        with SQLiteDatabase(db_path) as db:
            assay_id = db.insert_assay("Multi-Condition Experiment")

            # Insert measurements for different conditions
            control_data = pd.DataFrame({
                'Length': [100, 110, 105],
                'Volume': [400, 450, 425]
            })

            treatment_data = pd.DataFrame({
                'Length': [150, 160, 155],
                'Volume': [600, 650, 625]
            })

            db.insert_measurements(assay_id, control_data, condition='Control')
            db.insert_measurements(assay_id, treatment_data, condition='Treatment')

            print(f"\n  Inserted measurements for 2 conditions")

            # Get conditions
            conditions = db.get_conditions(assay_id)
            print(f"  Conditions: {conditions}")

            # Filter by condition
            control = db.get_measurements(assay_id, condition='Control')
            treatment = db.get_measurements(assay_id, condition='Treatment')

            print(f"\n  Control measurements: {len(control)}")
            print(f"  Treatment measurements: {len(treatment)}")

            # Get specific parameters
            length_only = db.get_measurements(assay_id, parameters=['Length'])
            print(f"\n  Filtered to 'Length' only: {list(length_only.columns)}")

            # Get parameter list
            params = db.get_parameters(assay_id)
            print(f"  Available parameters: {params}")

            print("\n  ✓ Conditions and filtering working!")
            return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if db_path.exists():
            db_path.unlink()


def test_duplicate_detection():
    """Test duplicate detection functionality."""
    print("\n" + "=" * 70)
    print("Test 4: Duplicate Detection")
    print("=" * 70)

    db_path = Path(__file__).parent / 'test_data' / 'test.db'
    if db_path.exists():
        db_path.unlink()

    try:
        with SQLiteDatabase(db_path) as db:
            assay_id = db.insert_assay("Duplicate Test")

            data = pd.DataFrame({
                'Length': [100, 110],
                'Volume': [400, 450]
            })

            # First insertion
            count1 = db.insert_measurements(
                assay_id, data,
                source_file='same_file.csv',
                condition='Control',
                check_duplicates=True
            )
            print(f"\n  First insertion: {count1} measurements")

            # Try to insert same file again (should be blocked)
            count2 = db.insert_measurements(
                assay_id, data,
                source_file='same_file.csv',
                condition='Control',
                check_duplicates=True
            )
            print(f"  Duplicate insertion: {count2} measurements (should be 0)")

            # Insert from different file (should work)
            count3 = db.insert_measurements(
                assay_id, data,
                source_file='different_file.csv',
                condition='Control',
                check_duplicates=True
            )
            print(f"  Different file: {count3} measurements")

            total = db.get_measurement_count(assay_id)
            print(f"\n  Total measurements: {total}")

            if count2 == 0 and total == (count1 + count3):
                print("\n  ✓ Duplicate detection working!")
                return True
            else:
                print("\n  ✗ Duplicate detection failed")
                return False

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False
    finally:
        if db_path.exists():
            db_path.unlink()


def test_integration_with_importer():
    """Test integration with file importer."""
    print("\n" + "=" * 70)
    print("Test 5: Integration with File Importer")
    print("=" * 70)

    db_path = Path(__file__).parent / 'test_data' / 'test.db'
    test_file = Path(__file__).parent / 'test_data' / '002_GST_005L.csv'

    if db_path.exists():
        db_path.unlink()

    if not test_file.exists():
        print(f"  ⚠ Test file not found: {test_file}")
        return False

    try:
        # Import data from file
        df = UnifiedImporter.import_file(test_file)
        print(f"\n  Imported {len(df)} rows from {test_file.name}")

        # Store in database
        with SQLiteDatabase(db_path) as db:
            assay_id = db.insert_assay("CSV Import Test")
            count = db.insert_measurements(
                assay_id, df,
                source_file=test_file.name,
                condition='GST'
            )
            print(f"  Stored {count} measurements in database")

            # Retrieve and verify
            retrieved = db.get_measurements(assay_id)
            print(f"  Retrieved {len(retrieved)} measurements")

            if len(retrieved) == len(df):
                print("\n  ✓ Integration with file importer working!")
                return True
            else:
                print("\n  ✗ Data mismatch")
                return False

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if db_path.exists():
            db_path.unlink()


def test_data_models():
    """Test Assay and Measurement data models."""
    print("\n" + "=" * 70)
    print("Test 6: Data Models (Assay & Measurement)")
    print("=" * 70)

    try:
        # Test Assay model
        assay = Assay(
            name="Test Assay",
            description="Testing data models",
            id=1
        )
        print(f"\n  Created Assay: {assay}")

        # Convert to/from dict
        assay_dict = assay.to_dict()
        assay_restored = Assay.from_dict(assay_dict)
        print(f"  Serialized and restored: {assay_restored}")

        # Test Measurement model
        measurement = Measurement(
            assay_id=1,
            parameters={'Length': 125.5, 'Volume': 450.2},
            condition='Control',
            source_file='test.csv'
        )
        print(f"\n  Created Measurement: {measurement}")

        # Test parameter access
        length = measurement.get_parameter('Length')
        print(f"  Length parameter: {length}")

        has_length = measurement.has_parameter('Length')
        has_width = measurement.has_parameter('Width')
        print(f"  Has 'Length': {has_length}, Has 'Width': {has_width}")

        # Convert to/from dict
        meas_dict = measurement.to_dict()
        meas_restored = Measurement.from_dict(meas_dict)
        print(f"  Serialized and restored: {meas_restored}")

        print("\n  ✓ Data models working!")
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def run_all_tests():
    """Run all tests and display summary."""
    tests = [
        ("Basic Database Operations", test_basic_database_operations),
        ("Measurement Storage", test_measurement_storage),
        ("Conditions and Filtering", test_conditions_and_filtering),
        ("Duplicate Detection", test_duplicate_detection),
        ("Integration with Importer", test_integration_with_importer),
        ("Data Models", test_data_models),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' failed with error: {e}")
            import traceback
            traceback.print_exc()
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
        print("✓ All tests passed! Database layer working correctly!")
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
