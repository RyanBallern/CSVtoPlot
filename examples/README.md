# Examples

This directory contains practical examples demonstrating how to use the Neuromorpho Analyzer.

## Running the Examples

All examples can be run directly from the command line:

```bash
cd examples
python example_1_simple_import.py
```

Or from the project root:

```bash
python examples/example_1_simple_import.py
```

## Available Examples

### Example 1: Simple Data Import
**File:** `example_1_simple_import.py`

The simplest possible workflow - import a single file and display the data.

**What it demonstrates:**
- Using `UnifiedImporter` for automatic format detection
- Importing a CSV file
- Displaying imported data and basic statistics

**Good for:** Getting started, testing if import works

---

### Example 2: Selective Parameter Import
**File:** `example_2_selective_import.py`

Shows how to import only specific columns/parameters from a file.

**What it demonstrates:**
- Using `HeaderScanner` to see available columns
- Using `ParameterMapper` to select specific parameters
- Importing only selected columns

**Good for:** Working with large files, importing only what you need

---

### Example 3: Batch Import to Database
**File:** `example_3_batch_import_to_database.py`

Complete workflow for importing multiple files into a database.

**What it demonstrates:**
- Using `FileScanner` to find all data files in a directory
- Importing multiple files in a batch
- Storing data in SQLite database with conditions
- Querying the database by condition
- Retrieving and analyzing stored data

**Good for:** Real-world workflows, managing multiple experiments

---

## Modifying the Examples

All examples use test data from the `test_data/` directory. To use your own data:

1. **Change the file path:**
   ```python
   data_file = Path('path/to/your/data.csv')
   ```

2. **Adjust parameter selection:**
   ```python
   parameters_to_import = ['YourColumn1', 'YourColumn2']
   ```

3. **Change database location:**
   ```python
   db_path = Path('path/to/your/database.db')
   ```

## Next Steps

After running these examples, you can:

1. **Explore the database** with any SQLite viewer (e.g., DB Browser for SQLite)
2. **Modify the examples** to work with your own data
3. **Combine workflows** from different examples
4. **Build your own scripts** using these as templates

## Need Help?

- See the main [README.md](../README.md) for full API documentation
- Check [USAGE_GUIDE.md](../USAGE_GUIDE.md) for detailed tutorials
- Run the test scripts to verify everything is working:
  ```bash
  python test_importers.py
  python test_database.py
  python test_integration.py
  ```
