# Neuromorpho Analyzer

A comprehensive Python-based tool for neuromorphological data analysis.

## Project Status

**Version:** 0.1.0-dev
**Current Phase:** Step 4 - Data Importers

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

### Step 3: ParameterMapper ✓

The `ParameterMapper` class can:
- Dynamically select which columns/parameters to import from data files
- Select all or specific parameters from available headers
- Add custom parameters not present in file headers
- Create parameter aliases (short names for long parameter names)
- Serialize/deserialize configuration for saving analysis profiles
- Track standard vs custom parameters separately

**Key Features:**
- **Select Parameters**: Choose specific columns from available headers
- **Custom Parameters**: Add computed or derived parameters
- **Parameter Aliases**: Create shortcuts (e.g., "Len" → "Length")
- **Save/Load**: Export configuration as dictionary for profiles
- **Integration**: Works seamlessly with HeaderScanner output

### Step 4: Data Importers ✓

Complete file import functionality with format-specific and unified importers:

**CSVImporter:**
- Import data from CSV files with auto-delimiter detection
- Filter to selected parameters only
- Get row count without loading full file

**JSONImporter:**
- Import from JSON files (multiple structure support)
- Handle list, dict, and single-object formats
- Extract measurement data with parameter filtering

**ExcelImporter:**
- Import from both XLS and XLSX files
- Multi-sheet support
- Get sheet names and row counts

**UnifiedImporter (recommended):**
- Auto-detect file format and use appropriate importer
- Works with all supported formats (XLS, XLSX, CSV, JSON)
- Integrate with ParameterMapper for selective import
- Import multiple files and combine into single DataFrame
- Add source file tracking

**Key Features:**
- **Format Auto-Detection**: Automatically uses correct importer for file type
- **Parameter Filtering**: Import only selected columns
- **ParameterMapper Integration**: Use mapper to control what gets imported
- **Multiple File Support**: Combine data from multiple files
- **Source Tracking**: Track which file each row came from
- **Error Handling**: Clear error messages for missing dependencies

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

### Test ParameterMapper

Run the test script:
```bash
python test_parameter_mapper.py
```

This will run 7 comprehensive tests covering:
- Basic parameter selection
- Select all functionality
- Custom parameters
- Parameter aliases
- Serialization (save/load)
- Integration with real files
- Deselection and clearing

### Test Data Importers

Run the test script:
```bash
python test_importers.py
```

This will run 6 comprehensive tests covering:
- CSV importer with parameter filtering
- JSON importer with measurement extraction
- Excel importer (both XLS and XLSX)
- Unified importer with auto-format detection
- ParameterMapper integration
- Multiple file import with source tracking

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
│               ├── file_scanner.py (FileScanner + HeaderScanner)
│               ├── parameter_mapper.py (ParameterMapper)
│               ├── csv_importer.py (CSVImporter)
│               ├── json_importer.py (JSONImporter)
│               ├── excel_importer.py (ExcelImporter)
│               └── unified_importer.py (UnifiedImporter)
├── test_data/
│   ├── 001_Control_001.xlsx
│   ├── 002_GST_005L.csv
│   ├── 003_Treatment_010T.json
│   ├── 004_Control_002.xls
│   └── 005_Invalid.txt
├── requirements.txt
├── test_file_scanner.py
├── test_header_scanner.py
├── test_parameter_mapper.py
├── test_importers.py
├── create_test_excel_files.py
└── README.md
```

## Next Steps

Step 5 will implement:
- Database layer (SQLite and PostgreSQL support)
- Data models (Assay, Measurement)
- Duplicate detection and origin tracking
- Complete import workflow integration

## License

MIT License - See LICENSE file for details
