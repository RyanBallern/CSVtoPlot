#!/usr/bin/env python3
"""
Example 3: Batch Import to Database

This example demonstrates:
1. Scanning a directory for multiple files
2. Importing all files
3. Storing in database with conditions
4. Querying the database
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from neuromorpho_analyzer.core.importers import FileScanner, UnifiedImporter
from neuromorpho_analyzer.core.database import SQLiteDatabase


def main():
    """Batch import example."""
    print("=" * 70)
    print("Example 3: Batch Import to Database")
    print("=" * 70)

    # Paths
    data_dir = Path(__file__).parent.parent / 'test_data'
    db_path = Path(__file__).parent.parent / 'example_data.db'

    # Clean up any existing database
    if db_path.exists():
        db_path.unlink()

    # Step 1: Scan directory for files
    print(f"\nScanning directory: {data_dir}")
    scanner = FileScanner(data_dir)
    files = scanner.scan_files()

    print(f"\nFound {len(files)} data files:")
    for f in files:
        print(f"  - {f['path'].name} (condition: {f['condition']})")

    # Step 2: Import all files
    print(f"\nImporting files...")
    imported_data = []

    for file_info in files:
        file_path = file_info['path']
        condition = file_info['condition']

        print(f"  Importing {file_path.name}...", end=' ')
        df = UnifiedImporter.import_file(file_path)
        print(f"✓ {len(df)} rows")

        imported_data.append({
            'dataframe': df,
            'file': file_path.name,
            'condition': condition
        })

    total_rows = sum(len(d['dataframe']) for d in imported_data)
    print(f"\nTotal imported: {total_rows} rows from {len(imported_data)} files")

    # Step 3: Store in database
    print(f"\nStoring in database: {db_path.name}")

    with SQLiteDatabase(db_path) as db:
        # Create an assay
        assay_id = db.insert_assay(
            name="Batch Import Example",
            description="Imported from multiple files"
        )
        print(f"  Created assay ID: {assay_id}")

        # Insert measurements from each file
        total_stored = 0
        for data in imported_data:
            count = db.insert_measurements(
                assay_id=assay_id,
                measurements=data['dataframe'],
                source_file=data['file'],
                condition=data['condition']
            )
            total_stored += count
            print(f"  ✓ Stored {count} measurements from {data['file']}")

        print(f"\nTotal stored: {total_stored} measurements")

        # Step 4: Query the database
        print("\n" + "-" * 70)
        print("Querying Database")
        print("-" * 70)

        # Get conditions
        conditions = db.get_conditions(assay_id)
        print(f"\nConditions in database: {', '.join(conditions)}")

        # Get measurements per condition
        print(f"\nMeasurements by condition:")
        for condition in conditions:
            cond_data = db.get_measurements(assay_id, condition=condition)
            print(f"  {condition}: {len(cond_data)} measurements")

        # Get all measurements
        all_data = db.get_measurements(assay_id)
        print(f"\nTotal measurements: {len(all_data)}")
        print(f"Columns: {list(all_data.columns)}")

        # Show sample data
        print(f"\nSample data (first 5 rows):")
        print(all_data.head())

    print(f"\n✓ Example complete!")
    print(f"\nDatabase saved to: {db_path}")
    print("You can explore this database file with any SQLite viewer.")


if __name__ == '__main__':
    main()
