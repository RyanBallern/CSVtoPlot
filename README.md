# Neuromorpho Analyzer

A comprehensive Python-based tool for neuromorphological data analysis.

## Quick Start

```python
from neuromorpho_analyzer.core.importers import UnifiedImporter
from neuromorpho_analyzer.core.database import SQLiteDatabase

# Import a data file (auto-detects CSV, Excel, JSON)
data = UnifiedImporter.import_file('mydata.csv')

# Store in database
with SQLiteDatabase('mydata.db') as db:
    assay_id = db.insert_assay("My Experiment")
    db.insert_measurements(assay_id, data, condition='Control')

    # Retrieve and analyze
    stored_data = db.get_measurements(assay_id)
    print(f"Stored {len(stored_data)} measurements")
```

See [USAGE_GUIDE.md](USAGE_GUIDE.md) for detailed tutorials and [examples/](examples/) for complete working scripts.

## Project Status

**Version:** 0.1.0-dev
**Current Phase:** Step 6 - Statistical Analysis

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

### Step 5: Database Layer ✓

Complete database functionality for persistent data storage:

**DatabaseBase (Abstract Interface):**
- Abstract base class defining database operations
- Allows easy switching between SQLite and PostgreSQL
- Consistent API for all database backends

**SQLiteDatabase:**
- SQLite implementation for single-user workflows
- Automatic table creation and schema management
- No server setup required - works with local file

**Data Models:**
- **Assay**: Represents an experiment/analysis session
- **Measurement**: Individual data points with parameters
- Serializable to/from dictionaries for easy storage

**Key Features:**
- **Assay Management**: Create, retrieve, list, and delete assays
- **Measurement Storage**: Store DataFrames with metadata
- **Duplicate Detection**: Prevent duplicate imports from same source file
- **Condition Filtering**: Filter measurements by experimental condition
- **Parameter Selection**: Retrieve only specific parameters
- **Source Tracking**: Track which file measurements came from
- **Integration**: Works seamlessly with UnifiedImporter

**Database Schema:**
- `assays` table: Stores experiment metadata
- `measurements` table: Stores individual data points with JSON parameters
- Foreign key constraints for data integrity
- Indexes for fast querying

### Step 6: Statistical Analysis ✓

Comprehensive statistical analysis engine with automatic test selection:

**StatisticsEngine:**
- Normality testing (Shapiro-Wilk)
- Parametric tests: Independent t-test, One-way ANOVA
- Non-parametric tests: Mann-Whitney U, Kruskal-Wallis H
- Post-hoc analysis: Tukey HSD with confidence intervals
- Effect size calculations (Cohen's d, eta-squared)
- Automatic test selection based on data distribution

**Key Features:**
- **Automatic Test Selection**:
  - 2 groups: t-test (parametric) or Mann-Whitney U (non-parametric)
  - 3+ groups: ANOVA (parametric) or Kruskal-Wallis (non-parametric)
  - Automatic normality testing to choose appropriate test
- **Normality Testing**: Shapiro-Wilk test for each group
- **T-Tests**:
  - Independent samples t-test with equal/unequal variances
  - Cohen's d effect size
  - Mean differences and standard deviations
- **Mann-Whitney U**: Non-parametric alternative for 2 groups
- **ANOVA**:
  - One-way ANOVA with eta-squared effect size
  - Two-way ANOVA for two independent factors (e.g., Condition × Distance)
  - Interaction effects and main effects
- **Kruskal-Wallis**: Non-parametric alternative for 3+ groups
- **Friedman Test**: Non-parametric repeated measures/matched groups
- **Post-hoc Analysis**: Tukey HSD for pairwise comparisons after ANOVA
- **Multi-Parameter Comparison**:
  - Compare multiple parameters across conditions simultaneously
  - Perfect for Sholl analysis (multiple distances)
  - Branch depth analysis (multiple depth levels)
  - Frequency distributions (multiple bins)
- **Comprehensive Results**: Detailed statistics, p-values, effect sizes
- **Formatted Output**: Human-readable summary reports

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

### Test Database Layer

Run the test script:
```bash
python test_database.py
```

This will run 6 comprehensive tests covering:
- Basic database operations (create, retrieve, list assays)
- Measurement storage and retrieval
- Conditions and parameter filtering
- Duplicate detection
- Integration with file importer
- Data models (Assay and Measurement)

### Test Statistical Analysis

Run the test script:
```bash
python test_statistics.py
```

This will run 8 comprehensive tests covering:
- Normality testing (Shapiro-Wilk)
- Independent t-test (parametric)
- Mann-Whitney U test (non-parametric)
- One-way ANOVA
- Tukey HSD post-hoc test
- Kruskal-Wallis H test
- Automatic test selection (2 groups)
- Automatic test selection (3+ groups)

### Test Two-Way ANOVA and Multi-Parameter Analysis

Run the test script:
```bash
python test_two_way_anova.py
```

This will run 4 comprehensive tests covering:
- Two-way ANOVA with interaction effects (Condition × Distance)
- Friedman test (non-parametric repeated measures)
- Multiple parameter comparison (Sholl analysis with 10 distances)
- Distance comparison wrapper (branch depth analysis)

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
│           ├── importers/
│           │   ├── __init__.py
│           │   ├── file_scanner.py (FileScanner + HeaderScanner)
│           │   ├── parameter_mapper.py (ParameterMapper)
│           │   ├── csv_importer.py (CSVImporter)
│           │   ├── json_importer.py (JSONImporter)
│           │   ├── excel_importer.py (ExcelImporter)
│           │   └── unified_importer.py (UnifiedImporter)
│           ├── database/
│           │   ├── __init__.py
│           │   ├── base.py (DatabaseBase)
│           │   └── sqlite.py (SQLiteDatabase)
│           ├── models/
│           │   ├── __init__.py
│           │   ├── assay.py (Assay)
│           │   └── measurement.py (Measurement)
│           └── processors/
│               ├── __init__.py
│               └── statistics.py (StatisticsEngine)
│
├── examples/
│   ├── README.md
│   ├── example_1_simple_import.py
│   ├── example_2_selective_import.py
│   └── example_3_batch_import_to_database.py
│
├── test_data/
│   ├── 001_Control_001.xlsx
│   ├── 002_GST_005L.csv
│   ├── 003_Treatment_010T.json
│   ├── 004_Control_002.xls
│   └── 005_Invalid.txt
│
├── requirements.txt
├── README.md
├── USAGE_GUIDE.md
├── test_file_scanner.py
├── test_header_scanner.py
├── test_parameter_mapper.py
├── test_importers.py
├── test_database.py
├── test_statistics.py
├── test_two_way_anova.py
├── test_integration.py
└── create_test_excel_files.py
```

### Documentation

- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Complete usage guide with tutorials
- **[examples/README.md](examples/README.md)** - Examples documentation
- **README.md** (this file) - API reference and project overview

### Integration Test

Run the comprehensive integration test to verify the complete pipeline:

```bash
python test_integration.py
```

This tests the full workflow from file scanning through database storage.

## Next Steps

Future enhancements could include:
- Plotting engine (box plots, bar plots, frequency distributions)
- Significance annotations for plots
- GraphPad Prism export (.pzfx format)
- GUI interface (tkinter-based)
- CLI commands for common workflows

## License

MIT License - See LICENSE file for details
