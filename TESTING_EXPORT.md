# Testing Export Functionality

## Quick Start

Choose one of these three testing methods:

### 1. Diagnostic Test (Recommended First)
Simple step-by-step test that shows exactly where any issues occur:
```bash
python diagnostic_export.py
```

**What it does:**
- ✓ Tests imports
- ✓ Tests dependencies
- ✓ Creates ExportConfig
- ✓ Creates test database
- ✓ Tests parameter selector
- ✓ Tests Excel export

**Expected output:** All 6 steps should pass with green checkmarks (✓)

### 2. Unit Tests
Comprehensive test suite with 19 tests:
```bash
python test_export.py
```

**Expected output:**
```
Ran 19 tests in 0.2s

OK
```

**If tests fail:**
- Read the error message carefully
- Check which test failed
- Run diagnostic test to narrow down the issue

### 3. Demo with Real Exports
Generates actual export files you can open:
```bash
python demo_export.py
```

**Expected output:**
- Creates test database with 3 conditions and 3 parameters
- Generates 3 export files in `./demo_output/` (relative to current directory):
  - `statistics_tables_Neurite_Length.xlsx` - Statistics tables with ANOVA
  - `analysis_[timestamp]_assays1.xlsx` - Comprehensive Excel export
  - `graphpad_[timestamp]_assays1.pzfx` - GraphPad Prism format

**Files you can open:**
- Open the Excel files to see formatted statistics tables
- Check for color-coded significance levels
- Verify multiple worksheets (Raw Data, Summary Statistics, Frequency Distributions)

## Troubleshooting

### Issue: "Module not found" errors

**Check Python path:**
```bash
python -c "import sys; print('\n'.join(sys.path))"
```

**Verify you're in the correct directory:**
```bash
pwd  # Should be /home/user/CSVtoPlot
ls src/neuromorpho_analyzer/core/exporters/  # Should show export modules
```

### Issue: "Database not found" in tests

This usually means the MockDatabase isn't being used correctly. Run diagnostic test:
```bash
python diagnostic_export.py
```

Look for which step fails (1-6). The diagnostic test will show the exact error.

### Issue: Tests pass but demo fails

**Check output directory permissions:**
```bash
mkdir -p ./demo_output
ls -ld ./demo_output
```

**Note:** Output files are created in `./demo_output/` relative to your current working directory.

**Check disk space:**
```bash
df -h /tmp
df -h ~
```

### Issue: Import errors

**Verify all dependencies:**
```bash
python -c "import pandas; print('pandas:', pandas.__version__)"
python -c "import numpy; print('numpy:', numpy.__version__)"
python -c "import openpyxl; print('openpyxl:', openpyxl.__version__)"
python -c "import scipy; print('scipy:', scipy.__version__)"
```

**Install missing dependencies:**
```bash
pip install pandas numpy openpyxl scipy matplotlib seaborn
```

## What Each Test Covers

### ExportConfig Tests (5 tests)
- Default configuration values
- Custom configuration
- Plot type selection
- Condition filtering
- Getting active plot types

### ExportParameterSelector Tests (6 tests)
- Getting available parameters from database
- Selecting specific parameters
- Selecting all parameters
- Checking if parameter is selected
- Toggling parameter selection
- Clearing selection

### StatisticsTableExporter Tests (2 tests)
- Creating statistics tables (summary, ANOVA, pairwise)
- Exporting to Excel with formatting

### ExcelExporter Tests (3 tests)
- Comprehensive Excel export
- Raw data sheet creation
- Summary statistics sheet creation

### GraphPadExporter Tests (3 tests)
- XML file creation
- XML structure validation
- Parameter table creation

## Expected Test Output

### Diagnostic Test Success:
```
============================================================
Export Functionality Diagnostic Test
============================================================

[1/6] Testing imports...
✓ All export modules imported successfully

[2/6] Testing dependencies...
✓ All dependencies imported successfully

[3/6] Testing ExportConfig...
✓ ExportConfig created
  - Export Excel: True
  - Plot DPI: 800
  - Active plot types: 6

[4/6] Testing database creation...
✓ Database created at: /tmp/diagnostic_test.db
  - Assay ID: 1
  - Measurements inserted: 10
  - Measurements retrieved: 10

[5/6] Testing ExportParameterSelector...
✓ Parameter selector created
  - Available parameters: ['parameter_name', 'value']
  - Selected parameters: ['parameter_name', 'value']

[6/6] Testing Excel export...
✓ Excel export successful
  - Output file: /tmp/analysis_[timestamp]_assays1.xlsx
  - File size: 6,634 bytes
  - File exists: True
  - Worksheets: ['Raw Data', 'Summary Statistics', 'Frequency Distributions']

============================================================
✓ All diagnostic tests passed!
============================================================
```

### Unit Tests Success:
```
test_condition_selection ... ok
test_custom_config ... ok
test_default_config ... ok
test_get_active_plot_types ... ok
test_plot_type_selection ... ok
test_clear_selection ... ok
test_get_available_parameters ... ok
test_is_selected ... ok
test_select_all ... ok
test_select_parameters ... ok
test_toggle_parameter ... ok
test_create_statistics_tables ... ok
test_export_to_excel ... ok
test_export ... ok
test_raw_data_sheet ... ok
test_summary_stats_sheet ... ok
test_export ... ok
test_parameter_tables ... ok
test_xml_structure ... ok

----------------------------------------------------------------------
Ran 19 tests in 0.2s

OK
```

### Demo Success:
```
============================================================
CSVtoPlot Analyzer - Export Functionality Demo
============================================================
✓ Created test database: /tmp/test_export.db
  - Assay ID: 1
  - Conditions: 3
  - Parameters: 3
  - Total measurements: 180

[... shows detailed statistics output ...]

============================================================
All export tests completed successfully!
============================================================

Output files saved to: /home/user/CSVtoPlot/demo_output

Generated files:
  - statistics_tables_Neurite_Length.xlsx (7,030 bytes)
  - analysis_[timestamp]_assays1.xlsx (11,838 bytes)
  - graphpad_[timestamp]_assays1.pzfx (293 bytes)
```

## Contact / Issues

If all three test methods fail:
1. Run diagnostic test and note which step fails
2. Check the error message
3. Verify all dependencies are installed
4. Check file permissions in output directories

If tests pass but you can't use the exports in your workflow:
1. Verify you're creating exports with real data
2. Check that parameter names match your actual data
3. Ensure conditions are properly set
