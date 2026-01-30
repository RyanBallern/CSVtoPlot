#!/usr/bin/env python3
"""
Comprehensive integration test for the complete data pipeline.

This test demonstrates the full workflow:
1. Scan directory for files
2. Read headers from files
3. Select parameters to import
4. Import data from multiple files
5. Store in database with duplicate detection
6. Retrieve and analyze stored data
"""

import sys
from pathlib import Path
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from neuromorpho_analyzer.core.importers import (
    FileScanner,
    HeaderScanner,
    ParameterMapper,
    UnifiedImporter
)
from neuromorpho_analyzer.core.database import SQLiteDatabase
from neuromorpho_analyzer.core.models import Assay


def test_complete_workflow():
    """Test the complete end-to-end workflow."""
    print("=" * 70)
    print("INTEGRATION TEST: Complete Data Pipeline Workflow")
    print("=" * 70)

    # Setup
    test_dir = Path(__file__).parent / 'test_data'
    db_path = test_dir / 'integration_test.db'

    # Clean up any existing test database
    if db_path.exists():
        db_path.unlink()

    try:
        # ===================================================================
        # STEP 1: Scan Directory for Files
        # ===================================================================
        print("\n" + "-" * 70)
        print("STEP 1: Scanning Directory for Data Files")
        print("-" * 70)

        scanner = FileScanner(test_dir)
        files = scanner.scan_files()

        print(f"\nFound {len(files)} valid data files:")
        for f in files:
            print(f"  - {f['path'].name}")
            print(f"    Condition: {f['condition']}, Format: {f['file_format']}")

        if len(files) == 0:
            print("\n✗ No files found - cannot proceed with test")
            return False

        # Detect dataset markers
        markers = scanner.detect_datasets(files)
        if markers:
            print(f"\nDataset markers detected: {', '.join(markers)}")

        # ===================================================================
        # STEP 2: Read Headers from First File
        # ===================================================================
        print("\n" + "-" * 70)
        print("STEP 2: Reading Available Headers")
        print("-" * 70)

        first_file = files[0]['path']
        headers = HeaderScanner.scan_headers(first_file)

        print(f"\nScanned headers from {first_file.name}:")
        for i, header in enumerate(headers, 1):
            print(f"  {i}. {header}")

        # ===================================================================
        # STEP 3: Select Parameters to Import
        # ===================================================================
        print("\n" + "-" * 70)
        print("STEP 3: Selecting Parameters for Import")
        print("-" * 70)

        mapper = ParameterMapper(headers)

        # Select specific parameters (in this case, select a subset)
        if len(headers) >= 3:
            selected = headers[:3]  # Select first 3 parameters
        else:
            selected = headers

        mapper.select_parameters(selected)

        print(f"\nSelected {mapper.get_parameter_count()} parameters:")
        for param in mapper.get_all_parameters():
            print(f"  - {param}")

        # ===================================================================
        # STEP 4: Import Data from Multiple Files
        # ===================================================================
        print("\n" + "-" * 70)
        print("STEP 4: Importing Data from Files")
        print("-" * 70)

        # Import from each file
        all_data = []
        for file_info in files[:3]:  # Import up to 3 files for the test
            file_path = file_info['path']
            condition = file_info['condition']

            print(f"\nImporting {file_path.name} (condition: {condition})...")

            df = UnifiedImporter.import_file(
                file_path,
                parameter_mapper=mapper
            )

            # Add metadata
            df['_source_file'] = file_path.name
            df['_condition'] = condition

            all_data.append({
                'dataframe': df,
                'file': file_path.name,
                'condition': condition
            })

            print(f"  ✓ Imported {len(df)} rows")

        total_rows = sum(len(d['dataframe']) for d in all_data)
        print(f"\nTotal data imported: {total_rows} rows from {len(all_data)} files")

        # ===================================================================
        # STEP 5: Store Data in Database
        # ===================================================================
        print("\n" + "-" * 70)
        print("STEP 5: Storing Data in Database")
        print("-" * 70)

        with SQLiteDatabase(db_path) as db:
            # Create an assay
            assay_id = db.insert_assay(
                name="Integration Test Experiment",
                description="Complete workflow integration test"
            )

            print(f"\nCreated assay with ID: {assay_id}")

            # Insert data from each file
            total_inserted = 0
            for data in all_data:
                count = db.insert_measurements(
                    assay_id=assay_id,
                    measurements=data['dataframe'].drop(columns=['_source_file', '_condition']),
                    source_file=data['file'],
                    condition=data['condition'],
                    check_duplicates=True
                )
                total_inserted += count
                print(f"  ✓ Stored {count} measurements from {data['file']}")

            print(f"\nTotal measurements stored: {total_inserted}")

            # ===================================================================
            # STEP 6: Retrieve and Analyze Stored Data
            # ===================================================================
            print("\n" + "-" * 70)
            print("STEP 6: Retrieving and Analyzing Data")
            print("-" * 70)

            # Get all measurements
            all_measurements = db.get_measurements(assay_id)
            print(f"\nRetrieved {len(all_measurements)} total measurements")

            # Get conditions
            conditions = db.get_conditions(assay_id)
            print(f"Conditions in database: {', '.join(conditions)}")

            # Get measurements by condition
            print("\nMeasurements per condition:")
            for condition in conditions:
                cond_data = db.get_measurements(assay_id, condition=condition)
                print(f"  {condition}: {len(cond_data)} measurements")

            # Get available parameters
            params = db.get_parameters(assay_id)
            print(f"\nAvailable parameters: {', '.join(params)}")

            # Test parameter filtering
            if len(params) > 0:
                first_param = params[0]
                filtered = db.get_measurements(assay_id, parameters=[first_param])
                print(f"\nFiltered to '{first_param}' only:")
                print(f"  Columns: {list(filtered.columns)}")

            # ===================================================================
            # STEP 7: Test Duplicate Detection
            # ===================================================================
            print("\n" + "-" * 70)
            print("STEP 7: Testing Duplicate Detection")
            print("-" * 70)

            # Try to insert the same data again
            duplicate_count = db.insert_measurements(
                assay_id=assay_id,
                measurements=all_data[0]['dataframe'].drop(columns=['_source_file', '_condition']),
                source_file=all_data[0]['file'],
                condition=all_data[0]['condition'],
                check_duplicates=True
            )

            print(f"\nAttempted duplicate insertion: {duplicate_count} rows inserted")
            if duplicate_count == 0:
                print("  ✓ Duplicate detection working correctly!")
            else:
                print("  ✗ WARNING: Duplicates were inserted!")

            # Final count should be the same
            final_count = db.get_measurement_count(assay_id)
            print(f"\nFinal measurement count: {final_count}")

            # ===================================================================
            # STEP 8: Summary
            # ===================================================================
            print("\n" + "=" * 70)
            print("WORKFLOW SUMMARY")
            print("=" * 70)

            print(f"""
Files scanned:           {len(files)}
Files imported:          {len(all_data)}
Parameters selected:     {mapper.get_parameter_count()}
Total rows imported:     {total_rows}
Rows stored in DB:       {total_inserted}
Conditions:              {len(conditions)}
Duplicate detection:     {'✓ Working' if duplicate_count == 0 else '✗ Failed'}
Final DB count:          {final_count}
            """)

            # Verify integrity
            if final_count == total_inserted and duplicate_count == 0:
                print("\n" + "=" * 70)
                print("✓ INTEGRATION TEST PASSED!")
                print("=" * 70)
                print("\nAll workflow steps completed successfully:")
                print("  ✓ File scanning")
                print("  ✓ Header reading")
                print("  ✓ Parameter selection")
                print("  ✓ Data import (multiple formats)")
                print("  ✓ Database storage")
                print("  ✓ Data retrieval and filtering")
                print("  ✓ Duplicate detection")
                print("\nThe complete data pipeline is fully functional!")
                return True
            else:
                print("\n✗ INTEGRATION TEST FAILED!")
                print(f"Expected {total_inserted} final measurements, got {final_count}")
                return False

    except Exception as e:
        print(f"\n✗ INTEGRATION TEST FAILED WITH ERROR!")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        if db_path.exists():
            db_path.unlink()
            print("\nCleaned up test database")


if __name__ == '__main__':
    success = test_complete_workflow()
    sys.exit(0 if success else 1)
