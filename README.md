# Neuromorpho Analyzer

A comprehensive Python-based tool for neuromorphological data analysis.

## Project Status

**Version:** 0.1.0-dev
**Current Phase:** Step 2 - Header Scanner

## What's Implemented

### Step 1: FileScanner ✓

The `FileScanner` class can:
- Scan directories for data files (XLS, XLSX, CSV, JSON)
- Parse filenames following the naming convention: `ExperimentIndex_Condition_ImageIndex[Marker].extension`
- Extract metadata: experiment index, condition, image index, dataset marker (L/T)
- Detect dataset markers across multiple files

**File Naming Convention Examples:**
- `001_Control_001.xlsx` - Basic file
- `002_GST_005L.csv` - File with Liposome marker (L)
- `003_Treatment_010T.json` - File with Tubule marker (T)

### Step 2: HeaderScanner ✓

The `HeaderScanner` class can:
- Extract column headers from XLS, XLSX, CSV, and JSON files
- Auto-detect CSV delimiters (comma, semicolon, tab)
- Handle different JSON structures (list or dict with 'measurements' key)
- Provide clear error messages for missing dependencies

**Supported File Formats:**
- **XLS**: Requires `xlrd` package
- **XLSX**: Requires `openpyxl` package
- **CSV**: Requires `pandas` package (auto-detects delimiter)
- **JSON**: Native Python support (no extra dependencies)

## Installation

### Install Dependencies

Install all required packages:
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install pandas      # For CSV files
pip install openpyxl    # For XLSX files
pip install xlrd        # For XLS files
pip install xlwt        # For creating XLS files
```

**Note:** JSON file support works without any additional dependencies.

## Testing

### Test FileScanner

Run the test script:
```bash
python test_file_scanner.py
```

This will scan the `test_data/` directory and display parsed metadata for each file.

### Test HeaderScanner

Run the test script:
```bash
python test_header_scanner.py
```

This will attempt to read headers from all test files and show which dependencies are missing.

### Sample Test Files

Located in `test_data/`:
- `001_Control_001.xlsx` - Excel 2007+ format (requires openpyxl)
- `002_GST_005L.csv` - CSV with sample data (requires pandas)
- `003_Treatment_010T.json` - JSON with measurements (no dependencies)
- `004_Control_002.xls` - Excel 97-2003 format (requires xlrd)
- `005_Invalid.txt` - Invalid format (should be ignored)

### Creating Test Excel Files

To create test Excel files with actual data:
```bash
python create_test_excel_files.py
```

This requires `openpyxl` and `xlwt` to be installed.

## Project Structure

```
CSVtoPlot/
├── src/
│   └── neuromorpho_analyzer/
│       └── core/
│           └── importers/
│               ├── __init__.py
│               └── file_scanner.py (FileScanner + HeaderScanner)
├── test_data/
│   ├── 001_Control_001.xlsx
│   ├── 002_GST_005L.csv
│   ├── 003_Treatment_010T.json
│   ├── 004_Control_002.xls
│   └── 005_Invalid.txt
├── requirements.txt
├── test_file_scanner.py
├── test_header_scanner.py
├── create_test_excel_files.py
└── README.md
```

## Next Steps

Step 3 will implement:
- ParameterMapper - Dynamic parameter selection from available headers
- Allow users to select which columns to import
- Support for custom parameter names

## License

MIT License - See LICENSE file for details
