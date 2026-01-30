# Neuromorpho Analyzer

A comprehensive Python-based tool for neuromorphological data analysis.

## Project Status

**Version:** 0.1.0-dev
**Current Phase:** Step 1 - Basic Project Structure & File Scanner

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

## Testing

### Test FileScanner

Run the test script:
```bash
python3 test_file_scanner.py
```

This will scan the `test_data/` directory and display parsed metadata for each file.

### Sample Test Files

Located in `test_data/`:
- `001_Control_001.xlsx`
- `002_GST_005L.csv`
- `003_Treatment_010T.json`
- `004_Control_002.xls`
- `005_Invalid.txt` (should be ignored - wrong format)

## Project Structure

```
CSVtoPlot/
├── src/
│   └── neuromorpho_analyzer/
│       ├── __init__.py
│       └── core/
│           ├── __init__.py
│           └── importers/
│               ├── __init__.py
│               └── file_scanner.py
├── test_data/
│   └── (sample files)
├── test_file_scanner.py
└── README.md
```

## Next Steps

Step 2 will implement:
- HeaderScanner - Extract column headers from files
- Support for reading XLS, XLSX, CSV, and JSON file headers

## License

MIT License - See LICENSE file for details
