#!/usr/bin/env python3
"""Create test Excel files (XLSX and XLS) with sample data."""

from pathlib import Path

# Sample data
headers = ['Length', 'Branch Points', 'Terminal Points', 'Average Diameter', 'Total Volume']
xlsx_data = [
    [110.3, 4, 7, 2.0, 420.5],
    [132.8, 5, 8, 2.2, 510.3],
    [105.6, 3, 6, 1.9, 390.8],
]
xls_data = [
    [118.5, 5, 7, 2.1, 445.2],
    [125.3, 4, 8, 2.3, 485.6],
    [112.7, 6, 9, 2.0, 430.1],
]

test_dir = Path(__file__).parent / 'test_data'

# Create XLSX file
try:
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Measurements"

    # Write headers
    ws.append(headers)

    # Write data
    for row in xlsx_data:
        ws.append(row)

    xlsx_path = test_dir / '001_Control_001.xlsx'
    wb.save(xlsx_path)
    print(f"✓ Created XLSX file: {xlsx_path}")

except ImportError:
    print("✗ openpyxl not installed - skipping XLSX creation")
    print("  Install with: pip install openpyxl")

# Create XLS file
try:
    import xlwt

    wb = xlwt.Workbook()
    ws = wb.add_sheet('Measurements')

    # Write headers
    for col, header in enumerate(headers):
        ws.write(0, col, header)

    # Write data
    for row_idx, row_data in enumerate(xls_data, start=1):
        for col_idx, value in enumerate(row_data):
            ws.write(row_idx, col_idx, value)

    xls_path = test_dir / '004_Control_002.xls'
    wb.save(xls_path)
    print(f"✓ Created XLS file: {xls_path}")

except ImportError:
    print("✗ xlwt not installed - skipping XLS creation")
    print("  Install with: pip install xlwt")

print("\nDone! Test data files created.")
