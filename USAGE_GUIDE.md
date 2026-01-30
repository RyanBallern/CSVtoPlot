# Neuromorpho Analyzer - Usage Guide

Complete guide for using the Neuromorpho Analyzer to import, store, and manage neuromorphological data.

## Table of Contents

1. [Quick Start](#quick-start)
2. [File Import Basics](#file-import-basics)
3. [Working with the Database](#working-with-the-database)
4. [Complete Workflows](#complete-workflows)
5. [Advanced Usage](#advanced-usage)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 5-Minute Example

```python
from neuromorpho_analyzer.core.importers import UnifiedImporter
from neuromorpho_analyzer.core.database import SQLiteDatabase

# Import a file (auto-detects format)
data = UnifiedImporter.import_file('mydata.csv')
print(f"Imported {len(data)} rows")

# Store in database
with SQLiteDatabase('mydata.db') as db:
    assay_id = db.insert_assay("My Experiment")
    db.insert_measurements(assay_id, data, condition='Control')

    # Retrieve it
    stored_data = db.get_measurements(assay_id)
    print(f"Retrieved {len(stored_data)} measurements")
```

---

## File Import Basics

### Supported File Formats

The analyzer supports four file formats:
- **CSV** (`.csv`) - Comma/semicolon/tab delimited
- **Excel 2007+** (`.xlsx`) - Modern Excel format
- **Excel 97-2003** (`.xls`) - Legacy Excel format
- **JSON** (`.json`) - Structured JSON data

### Simple Import

Import any supported file with automatic format detection:

```python
from neuromorpho_analyzer.core.importers import UnifiedImporter

# Auto-detects format and imports
df = UnifiedImporter.import_file('data.csv')
```

### Scanning a Directory

Find all data files in a directory:

```python
from neuromorpho_analyzer.core.importers import FileScanner
from pathlib import Path

scanner = FileScanner(Path('./data'))
files = scanner.scan_files()

for file_info in files:
    print(f"{file_info['path'].name}")
    print(f"  Condition: {file_info['condition']}")
    print(f"  Format: {file_info['file_format']}")
```

**File Naming Convention:**

Files should follow this pattern:
```
ExperimentIndex_Condition_ImageIndex[Marker].extension
```

Examples:
- `001_Control_001.xlsx` - Basic file
- `002_Treatment_005.csv` - Treatment condition
- `003_GST_010L.json` - With Liposome marker (L)
- `004_Drug_015T.xls` - With Tubule marker (T)

### Reading Available Headers

See what columns are available before importing:

```python
from neuromorpho_analyzer.core.importers import HeaderScanner

headers = HeaderScanner.scan_headers('data.csv')
print(f"Available columns: {headers}")
```

### Selective Parameter Import

Import only specific columns:

```python
from neuromorpho_analyzer.core.importers import (
    HeaderScanner,
    ParameterMapper,
    UnifiedImporter
)

# 1. Scan available headers
headers = HeaderScanner.scan_headers('data.csv')

# 2. Select which ones to import
mapper = ParameterMapper(headers)
mapper.select_parameters(['Length', 'Branch Points', 'Total Volume'])

# 3. Import with filtering
df = UnifiedImporter.import_file('data.csv', parameter_mapper=mapper)
# df now contains only the 3 selected columns
```

### Importing Multiple Files

Combine data from multiple files:

```python
from neuromorpho_analyzer.core.importers import UnifiedImporter

files = ['file1.csv', 'file2.xlsx', 'file3.json']

# Import and combine with source tracking
combined = UnifiedImporter.import_multiple_files(
    files,
    add_source_column=True  # Adds 'source_file' column
)

print(f"Combined {len(combined)} rows from {len(files)} files")
print(f"Sources: {combined['source_file'].unique()}")
```

---

## Working with the Database

### Creating a Database

```python
from neuromorpho_analyzer.core.database import SQLiteDatabase

# Create/open database (file created automatically)
db = SQLiteDatabase('mydata.db')
db.connect()

# ... use database ...

db.disconnect()
```

Or use context manager (recommended):

```python
with SQLiteDatabase('mydata.db') as db:
    # Database automatically connects/disconnects
    pass
```

### Creating an Assay

An assay groups related measurements (one experiment/session):

```python
with SQLiteDatabase('mydata.db') as db:
    assay_id = db.insert_assay(
        name="Dendrite Morphology Study",
        description="Analyzing control vs treatment dendrites"
    )
    print(f"Created assay with ID: {assay_id}")
```

### Storing Measurements

Store a DataFrame of measurements:

```python
with SQLiteDatabase('mydata.db') as db:
    # Import data
    df = UnifiedImporter.import_file('control_data.csv')

    # Store with metadata
    count = db.insert_measurements(
        assay_id=assay_id,
        measurements=df,
        source_file='control_data.csv',
        condition='Control',
        check_duplicates=True  # Prevents duplicate imports
    )
    print(f"Stored {count} measurements")
```

### Retrieving Measurements

Get measurements back from database:

```python
with SQLiteDatabase('mydata.db') as db:
    # Get all measurements for an assay
    all_data = db.get_measurements(assay_id)

    # Get measurements for specific condition
    control = db.get_measurements(assay_id, condition='Control')
    treatment = db.get_measurements(assay_id, condition='Treatment')

    # Get specific parameters only
    lengths = db.get_measurements(
        assay_id,
        parameters=['Length', 'Total Volume']
    )
```

### Querying Database Info

```python
with SQLiteDatabase('mydata.db') as db:
    # List all assays
    assays = db.list_assays()
    for assay in assays:
        print(f"{assay['id']}: {assay['name']}")

    # Get conditions in an assay
    conditions = db.get_conditions(assay_id)
    print(f"Conditions: {conditions}")

    # Get available parameters
    params = db.get_parameters(assay_id)
    print(f"Parameters: {params}")

    # Get measurement count
    count = db.get_measurement_count(assay_id)
    print(f"Total measurements: {count}")
```

### Duplicate Detection

The database prevents importing the same file twice:

```python
with SQLiteDatabase('mydata.db') as db:
    df = UnifiedImporter.import_file('data.csv')

    # First import works
    count1 = db.insert_measurements(
        assay_id, df,
        source_file='data.csv',
        condition='Control',
        check_duplicates=True
    )
    # count1 = 10 (example)

    # Second import blocked (same file + condition)
    count2 = db.insert_measurements(
        assay_id, df,
        source_file='data.csv',
        condition='Control',
        check_duplicates=True
    )
    # count2 = 0 (duplicate detected!)
```

---

## Complete Workflows

### Workflow 1: Simple Single-File Analysis

```python
from neuromorpho_analyzer.core.importers import UnifiedImporter
from neuromorpho_analyzer.core.database import SQLiteDatabase

# Import
df = UnifiedImporter.import_file('experiment_data.csv')

# Store
with SQLiteDatabase('analysis.db') as db:
    assay_id = db.insert_assay("Single File Test")
    db.insert_measurements(assay_id, df, condition='Control')

    # Analyze
    data = db.get_measurements(assay_id)
    print(data.describe())
```

### Workflow 2: Batch Import from Directory

```python
from pathlib import Path
from neuromorpho_analyzer.core.importers import FileScanner, UnifiedImporter
from neuromorpho_analyzer.core.database import SQLiteDatabase

# Scan directory
scanner = FileScanner(Path('./data'))
files = scanner.scan_files()

# Import all files into database
with SQLiteDatabase('batch_import.db') as db:
    assay_id = db.insert_assay("Batch Import Study")

    for file_info in files:
        df = UnifiedImporter.import_file(file_info['path'])
        db.insert_measurements(
            assay_id, df,
            source_file=file_info['path'].name,
            condition=file_info['condition']
        )

    # Summary
    conditions = db.get_conditions(assay_id)
    print(f"Imported {len(files)} files")
    print(f"Conditions: {', '.join(conditions)}")
```

### Workflow 3: Selective Import with Parameter Mapping

```python
from neuromorpho_analyzer.core.importers import (
    HeaderScanner,
    ParameterMapper,
    UnifiedImporter
)
from neuromorpho_analyzer.core.database import SQLiteDatabase

# Scan and select parameters
headers = HeaderScanner.scan_headers('data.csv')
mapper = ParameterMapper(headers)
mapper.select_parameters(['Length', 'Branch Points', 'Total Volume'])

# Import only selected parameters
df = UnifiedImporter.import_file('data.csv', parameter_mapper=mapper)

# Store
with SQLiteDatabase('selective.db') as db:
    assay_id = db.insert_assay("Selective Import")
    db.insert_measurements(assay_id, df)

    # Verify
    params = db.get_parameters(assay_id)
    print(f"Stored parameters: {params}")
    # Should only show: ['Length', 'Branch Points', 'Total Volume']
```

---

## Advanced Usage

### Working with Data Models

```python
from neuromorpho_analyzer.core.models import Assay, Measurement

# Create assay object
assay = Assay(
    name="My Study",
    description="Testing morphology",
    id=1
)

# Serialize to dictionary
assay_dict = assay.to_dict()

# Deserialize from dictionary
assay_restored = Assay.from_dict(assay_dict)

# Create measurement
measurement = Measurement(
    assay_id=1,
    parameters={'Length': 125.5, 'Volume': 450.2},
    condition='Control',
    source_file='data.csv'
)

# Access parameters
length = measurement.get_parameter('Length')
measurement.set_parameter('Width', 2.5)
has_width = measurement.has_parameter('Width')
```

### Custom Parameter Names

Add custom calculated parameters:

```python
from neuromorpho_analyzer.core.importers import ParameterMapper

mapper = ParameterMapper(['Length', 'Width'])
mapper.select_parameters(['Length', 'Width'])

# Add custom parameter
mapper.add_custom_parameter('Area')

# This could be calculated after import:
# df['Area'] = df['Length'] * df['Width']
```

### Parameter Aliases

Create shortcuts for long parameter names:

```python
from neuromorpho_analyzer.core.importers import ParameterMapper

mapper = ParameterMapper(['Total Dendrite Length', 'Number of Branch Points'])

# Add aliases
mapper.add_parameter_alias('Total Dendrite Length', 'Length')
mapper.add_parameter_alias('Number of Branch Points', 'Branches')

# Resolve aliases
original = mapper.resolve_alias('Length')
# Returns: 'Total Dendrite Length'
```

### Saving Parameter Configurations

Save parameter selection for reuse:

```python
from neuromorpho_analyzer.core.importers import ParameterMapper
import json

# Configure
mapper = ParameterMapper(['Length', 'Width', 'Height', 'Volume'])
mapper.select_parameters(['Length', 'Volume'])

# Save configuration
config = mapper.to_dict()
with open('import_config.json', 'w') as f:
    json.dump(config, f)

# Later: load configuration
with open('import_config.json', 'r') as f:
    config = json.load(f)

mapper_restored = ParameterMapper.from_dict(config)
# mapper_restored has the same parameter selection
```

---

## Troubleshooting

### Import Errors

**Error: "File not found"**
```python
# Check if file exists
from pathlib import Path
file_path = Path('data.csv')
print(f"Exists: {file_path.exists()}")
print(f"Absolute path: {file_path.absolute()}")
```

**Error: "Unsupported file format"**
```python
# Check if format is supported
from neuromorpho_analyzer.core.importers import UnifiedImporter
is_supported = UnifiedImporter.is_supported_format('myfile.txt')
# Supported: .csv, .json, .xls, .xlsx
```

**Error: "pandas package required for CSV files"**
```bash
# Install missing dependency
pip install pandas
```

### Database Errors

**Error: "Parameters not found in file"**
```python
# Check available parameters first
from neuromorpho_analyzer.core.importers import HeaderScanner
headers = HeaderScanner.scan_headers('data.csv')
print(f"Available: {headers}")
```

**Duplicate Detection Not Working**
```python
# Make sure check_duplicates=True
db.insert_measurements(
    assay_id, df,
    source_file='data.csv',  # Must provide source_file
    condition='Control',      # Must provide condition
    check_duplicates=True     # Must be True
)
```

### Performance Tips

**Large Files:**
- Use selective import to load only needed columns
- Import in batches if file is very large

**Multiple Files:**
- Use batch import with UnifiedImporter.import_multiple_files()
- Consider using database to avoid loading all data in memory

---

## Getting Help

- **Run tests:** `python test_integration.py` to verify installation
- **Check examples:** See `examples/` directory for working code
- **Read API docs:** See main README.md for full API reference

---

## Next Steps

Now that you understand the basics:

1. **Try the examples** in the `examples/` directory
2. **Import your own data** using the workflows above
3. **Explore the database** with a SQLite viewer
4. **Build custom analysis scripts** using these patterns as templates

Happy analyzing!
