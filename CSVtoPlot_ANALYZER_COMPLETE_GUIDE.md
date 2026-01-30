# NEUROMORPHOLOGICAL DATA ANALYSIS TOOL - COMPLETE DEVELOPMENT GUIDE

**Version:** 1.0  
**Last Updated:** 2025-01-30  
**Target Publication:** Journal of Open Source Software (JOSS)  
**Repository Goal:** Production-ready, publishable scientific software

---

## TABLE OF CONTENTS

1. [Project Overview](#project-overview)
2. [Technical Architecture](#technical-architecture)
3. [Project Structure](#project-structure)
4. [Detailed Feature Specifications](#detailed-feature-specifications)
   - [Import Functionality](#1-import-functionality)
   - [Database Layer](#2-database-layer)
   - [Statistical Analysis](#3-statistical-analysis)
   - [Plotting Engine](#4-plotting-engine)
   - [Export Functionality](#5-export-functionality)
   - [Analysis Profiles](#6-analysis-profiles)
   - [Representative File Analysis](#7-representative-file-analysis)
   - [GUI Components](#8-gui-components)
5. [Implementation Roadmap](#implementation-roadmap)
6. [Testing Strategy](#testing-strategy)
7. [Documentation Requirements](#documentation-requirements)
8. [Coding Standards](#coding-standards)
9. [Complete Implementation Checklist](#complete-implementation-checklist)

---

## PROJECT OVERVIEW

### Purpose
Build a comprehensive Python-based tool for neuromorphological data analysis, specifically processing dendrite measurements, Sholl intersection data, and morphological parameters from research datasets. The tool must support both GUI and CLI interfaces while maintaining a single source of truth for core logic.

### Target Users
- Neuroscience researchers
- Laboratory technicians
- Data analysts in neuromorphology

### Current State
- PostgreSQL/SQLite database backend exists
- Basic Python data processing scripts exist
- File parsing works (XLS/XLSX support via xlrd)
- Unicode encoding handled
- Windows environment support

### End Goal
A production-ready, publishable tool with:
- **Import:** Dynamic parameter selection from XLS/XLSX/CSV/JSON files
- **Statistics:** Normality testing, ANOVA, Tukey HSD post-hoc
- **Plotting:** Publication-quality plots (box, bar, frequency distributions) at 800 DPI
- **Export:** Excel, GraphPad Prism (.pzfx), CSV with statistical tables
- **Profiles:** Save/load complete analysis pipelines
- **Quality:** >80% test coverage, full documentation, JOSS-compliant

---

## TECHNICAL ARCHITECTURE

### Core Design Principles

1. **Adapter Pattern Architecture**
   ```
   Core Logic Layer (business logic, data processing)
        ↓
   Interface Adapter Layer
        ↓
   ┌──────────┬──────────┐
   │   GUI    │   CLI    │
   └──────────┴──────────┘
   ```

2. **Single Source of Truth**
   - All business logic in core modules
   - GUI/CLI are thin presentation layers
   - No logic duplication between interfaces

3. **Database-Centric**
   - PostgreSQL for multi-user environments
   - SQLite for single-user workflows
   - Abstract database layer for easy switching

### Technology Stack

**Core:**
- Python 3.8+ (type hints throughout)
- PostgreSQL / SQLite
- pandas (data manipulation)
- numpy (numerical operations)

**Data Import:**
- xlrd (XLS files)
- openpyxl (XLSX files)
- Built-in csv module (CSV files)
- Built-in json module (JSON files)

**Visualization:**
- matplotlib (plotting)
- seaborn (statistical plots)

**Statistics:**
- scipy.stats (normality tests, ANOVA)
- statsmodels (post-hoc tests)
- pingouin (comprehensive statistical analysis)

**GUI:**
- tkinter (cross-platform GUI)
- matplotlib.backends.backend_tkagg (plot embedding)

**Export:**
- openpyxl (Excel export)
- Custom XML generation (GraphPad Prism .pzfx)

**Testing:**
- pytest (unit and integration tests)
- pytest-cov (coverage reporting)
- pytest-mock (mocking)

**Build:**
- PyInstaller (executable generation)

---

## PROJECT STRUCTURE

```
neuromorpho_analyzer/
├── README.md
├── LICENSE (MIT)
├── CHANGELOG.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── CITATION.cff
├── paper.md (JOSS manuscript)
├── pyproject.toml
├── requirements.txt
├── setup.py
│
├── src/
│   └── neuromorpho_analyzer/
│       ├── __init__.py
│       ├── __main__.py (entry point)
│       │
│       ├── core/ (Core business logic - NO UI code)
│       │   ├── __init__.py
│       │   ├── database/
│       │   │   ├── __init__.py
│       │   │   ├── base.py (abstract DB interface)
│       │   │   ├── postgres.py (PostgreSQL implementation)
│       │   │   └── sqlite.py (SQLite implementation)
│       │   ├── importers/
│       │   │   ├── __init__.py
│       │   │   ├── file_scanner.py (scan headers, parse filenames)
│       │   │   ├── excel_importer.py (XLS/XLSX reading)
│       │   │   ├── csv_importer.py (CSV reading)
│       │   │   ├── json_importer.py (JSON reading)
│       │   │   ├── unified_importer.py (format-agnostic importer)
│       │   │   └── parameter_mapper.py (dynamic parameter selection)
│       │   ├── processors/
│       │   │   ├── __init__.py
│       │   │   ├── data_validator.py (duplicate detection, origin tracking)
│       │   │   ├── statistics.py (normality, ANOVA, post-hoc)
│       │   │   ├── representative_files.py (Euclidean distance analysis)
│       │   │   └── density_calculator.py (liposome/tubule density)
│       │   ├── plotters/
│       │   │   ├── __init__.py
│       │   │   ├── box_plotter.py (boxplots with SEM)
│       │   │   ├── bar_plotter.py (bar plots with SEM)
│       │   │   ├── frequency_plotter.py (frequency distributions)
│       │   │   ├── significance_annotator.py (brackets and stars)
│       │   │   ├── plot_config.py (colors, styling, no frames/ticks)
│       │   │   └── plot_exporter.py (800 DPI PNG/TIF export)
│       │   ├── exporters/
│       │   │   ├── __init__.py
│       │   │   ├── excel_exporter.py (comprehensive xlsx)
│       │   │   ├── graphpad_exporter.py (.pzfx generation)
│       │   │   ├── csv_exporter.py (representative files list)
│       │   │   ├── statistics_table_exporter.py (formatted stat tables)
│       │   │   ├── parameter_selector.py (dynamic export parameters)
│       │   │   └── export_config.py (export configuration)
│       │   ├── profiles/
│       │   │   ├── __init__.py
│       │   │   ├── profile_manager.py (save/load/edit profiles)
│       │   │   └── profile_schema.py (profile data structure)
│       │   └── models/
│       │       ├── __init__.py
│       │       ├── assay.py (Assay data model)
│       │       ├── measurement.py (Measurement data model)
│       │       └── config.py (Configuration model)
│       │
│       ├── adapters/ (Interface adapters - thin layers)
│       │   ├── __init__.py
│       │   ├── gui_adapter.py (GUI → Core)
│       │   └── cli_adapter.py (CLI → Core)
│       │
│       ├── gui/ (GUI-specific code ONLY)
│       │   ├── __init__.py
│       │   ├── main_window.py
│       │   ├── widgets/
│       │   │   ├── __init__.py
│       │   │   ├── parameter_selector.py (tick boxes)
│       │   │   ├── condition_names_widget.py (short→long name mappings)
│       │   │   ├── color_picker.py (RGB with preview)
│       │   │   ├── plot_preview.py (matplotlib embedded)
│       │   │   ├── profile_manager_widget.py
│       │   │   ├── export_config_widget.py (format/plot toggles)
│       │   │   ├── condition_selector_widget.py (condition selection)
│       │   │   └── progress_dialog.py
│       │   └── dialogs/
│       │       ├── __init__.py
│       │       ├── import_dialog.py
│       │       ├── export_dialog.py
│       │       └── settings_dialog.py
│       │
│       ├── cli/ (CLI-specific code ONLY)
│       │   ├── __init__.py
│       │   ├── main.py
│       │   ├── commands/
│       │   │   ├── __init__.py
│       │   │   ├── import_cmd.py
│       │   │   ├── export_cmd.py
│       │   │   ├── plot_cmd.py
│       │   │   └── analyze_cmd.py
│       │   └── formatters/
│       │       ├── __init__.py
│       │       ├── table_formatter.py
│       │       └── color_formatter.py (text color for CLI)
│       │
│       └── utils/
│           ├── __init__.py
│           ├── logger.py (logging setup)
│           ├── validators.py (input validation)
│           └── constants.py (default values, constants)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py (pytest fixtures)
│   ├── unit/
│   │   ├── test_database.py
│   │   ├── test_importers.py
│   │   ├── test_statistics.py
│   │   ├── test_plotters.py
│   │   ├── test_exporters.py
│   │   └── test_profiles.py
│   ├── integration/
│   │   ├── test_import_workflow.py
│   │   ├── test_export_workflow.py
│   │   └── test_full_pipeline.py
│   └── test_data/
│       ├── sample_files/ (XLS/XLSX/CSV/JSON test files)
│       └── expected_outputs/
│
├── docs/
│   ├── index.md
│   ├── installation.md
│   ├── user_guide/
│   │   ├── getting_started.md
│   │   ├── importing_data.md
│   │   ├── analysis_profiles.md
│   │   ├── plotting.md
│   │   ├── statistics.md
│   │   └── exporting.md
│   ├── developer_guide/
│   │   ├── architecture.md
│   │   ├── contributing.md
│   │   └── testing.md
│   ├── api/
│   │   └── reference.md
│   └── images/ (screenshots, example plots)
│
├── examples/
│   ├── example_data/
│   ├── example_profiles/
│   └── notebooks/
│       └── demo_analysis.ipynb
│
└── .github/
    ├── workflows/
    │   ├── tests.yml (CI/CD)
    │   └── release.yml
    └── ISSUE_TEMPLATE/
```

---

## DETAILED FEATURE SPECIFICATIONS

### 1. IMPORT FUNCTIONALITY

#### 1.1 Supported File Formats

**Requirements:**
- Support XLS, XLSX, CSV, and JSON files
- Unified interface regardless of file format
- Same parameter selection workflow for all formats
- Automatic format detection based on file extension

**File Naming Convention:**
```
Format: ExperimentIndex_Condition_ImageIndex[Marker].extension
Examples:
  - 001_Control_001.xlsx
  - 002_GST_005L.csv      (L = Liposome marker)
  - 003_Treatment_010T.json  (T = Tubule marker)
```

#### 1.2 File Scanner

**Implementation: `core/importers/file_scanner.py`**

```python
from pathlib import Path
from typing import List, Dict, Tuple
import re

class FileScanner:
    """Scans directories for morphology data files and extracts metadata."""
    
    def __init__(self, directory: Path):
        self.directory = directory
        # Updated pattern to include CSV and JSON
        self.file_pattern = re.compile(
            r'^(\d+)_([A-Za-z]+)_(\d+)([LT]?)\.(xlsx?|csv|json)$'
        )
        self.supported_extensions = {'.xls', '.xlsx', '.csv', '.json'}
    
    def scan_files(self) -> List[Dict[str, any]]:
        """
        Scan directory and return file metadata.
        
        Returns:
            List of dicts with: path, experiment_index, condition, 
            image_index, dataset_marker, file_format
        """
        files = []
        for ext in self.supported_extensions:
            for file_path in self.directory.glob(f'*{ext}'):
                metadata = self._parse_filename(file_path)
                if metadata:
                    files.append(metadata)
        return files
    
    def _parse_filename(self, file_path: Path) -> Dict[str, any]:
        """Parse filename to extract metadata."""
        match = self.file_pattern.match(file_path.name)
        if not match:
            return None
        
        return {
            'path': file_path,
            'experiment_index': int(match.group(1)),
            'condition': match.group(2),
            'image_index': int(match.group(3)),
            'dataset_marker': match.group(4) or None,  # 'L', 'T', or None
            'file_format': match.group(5)  # 'xls', 'xlsx', 'csv', 'json'
        }
    
    def detect_datasets(self, files: List[Dict]) -> List[str]:
        """
        Detect if L/T dataset markers are present.
        
        Returns:
            List of unique dataset markers found
        """
        markers = {f['dataset_marker'] for f in files if f['dataset_marker']}
        return sorted(markers)
```

#### 1.3 Header Scanner

**Implementation: `core/importers/file_scanner.py` (additional class)**

```python
import xlrd
from openpyxl import load_workbook
import pandas as pd
import json

class HeaderScanner:
    """Extracts column headers from various file formats."""
    
    @staticmethod
    def scan_headers(file_path: Path) -> List[str]:
        """
        Scan first file to get available column headers.
        
        Args:
            file_path: Path to data file
            
        Returns:
            List of column header names
        """
        ext = file_path.suffix.lower()
        
        if ext == '.xls':
            return HeaderScanner._scan_xls(file_path)
        elif ext == '.xlsx':
            return HeaderScanner._scan_xlsx(file_path)
        elif ext == '.csv':
            return HeaderScanner._scan_csv(file_path)
        elif ext == '.json':
            return HeaderScanner._scan_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    @staticmethod
    def _scan_xls(file_path: Path) -> List[str]:
        """Scan XLS file for headers."""
        workbook = xlrd.open_workbook(file_path)
        sheet = workbook.sheet_by_index(0)
        headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
        return [h for h in headers if h]
    
    @staticmethod
    def _scan_xlsx(file_path: Path) -> List[str]:
        """Scan XLSX file for headers."""
        workbook = load_workbook(file_path, read_only=True)
        sheet = workbook.active
        headers = [cell.value for cell in sheet[1]]
        return [h for h in headers if h]
    
    @staticmethod
    def _scan_csv(file_path: Path) -> List[str]:
        """Scan CSV file for headers."""
        # Try multiple delimiters
        for delimiter in [',', ';', '\t']:
            try:
                df = pd.read_csv(file_path, sep=delimiter, nrows=0)
                if len(df.columns) > 1:  # Successfully parsed
                    return list(df.columns)
            except:
                continue
        
        # Fallback to default comma delimiter
        df = pd.read_csv(file_path, nrows=0)
        return list(df.columns)
    
    @staticmethod
    def _scan_json(file_path: Path) -> List[str]:
        """Scan JSON file for headers (keys from first measurement)."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, dict) and 'measurements' in data:
            measurements_list = data['measurements']
        elif isinstance(data, list):
            measurements_list = data
        else:
            return []
        
        if measurements_list and len(measurements_list) > 0:
            return list(measurements_list[0].keys())
        return []
```

#### 1.4 Parameter Mapper

**Implementation: `core/importers/parameter_mapper.py`**

```python
from typing import List, Dict, Set

class ParameterMapper:
    """Manages dynamic parameter selection for import."""
    
    def __init__(self, available_headers: List[str]):
        self.available_headers = available_headers
        self.selected_parameters: Set[str] = set()
        self.custom_parameters: Set[str] = set()
    
    def select_parameters(self, parameters: List[str]) -> None:
        """
        Select parameters from available headers.
        
        Args:
            parameters: List of parameter names to select
        """
        for param in parameters:
            if param in self.available_headers:
                self.selected_parameters.add(param)
    
    def add_custom_parameter(self, parameter: str) -> None:
        """
        Add a custom parameter not in headers.
        
        Args:
            parameter: Custom parameter name
        """
        self.custom_parameters.add(parameter)
        self.selected_parameters.add(parameter)
    
    def get_all_parameters(self) -> List[str]:
        """Get all selected parameters (from headers + custom)."""
        return sorted(self.selected_parameters)
    
    def to_dict(self) -> Dict:
        """Export to dict for profile saving."""
        return {
            'available_headers': self.available_headers,
            'selected_parameters': list(self.selected_parameters),
            'custom_parameters': list(self.custom_parameters)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ParameterMapper':
        """Load from dict (profile loading)."""
        mapper = cls(data['available_headers'])
        mapper.selected_parameters = set(data['selected_parameters'])
        mapper.custom_parameters = set(data['custom_parameters'])
        return mapper
```

#### 1.5 Excel Importer

**Implementation: `core/importers/excel_importer.py`**

```python
import pandas as pd
from typing import Dict, List, Optional, Set
from pathlib import Path
import logging

class ExcelImporter:
    """Imports data from Excel files with duplicate prevention."""
    
    def __init__(self, parameter_mapper: ParameterMapper):
        self.parameter_mapper = parameter_mapper
        self.logger = logging.getLogger(__name__)
        self.imported_records: Set[tuple] = set()
    
    def import_file(self, file_metadata: Dict) -> List[Dict]:
        """
        Import data from single Excel file.
        
        Args:
            file_metadata: Dict with path, experiment_index, condition, etc.
            
        Returns:
            List of measurement records with origin tracking
        """
        file_path = file_metadata['path']
        parameters = self.parameter_mapper.get_all_parameters()
        
        # Read file
        if file_path.suffix == '.xls':
            df = pd.read_excel(file_path, engine='xlrd')
        else:
            df = pd.read_excel(file_path, engine='openpyxl')
        
        # Extract records
        records = []
        for idx, row in df.iterrows():
            record = {
                'experiment_index': file_metadata['experiment_index'],
                'condition': file_metadata['condition'],
                'image_index': file_metadata['image_index'],
                'dataset_marker': file_metadata['dataset_marker'],
                'origin_file': str(file_path),
                'origin_row': idx + 2,  # +2 for header and 0-indexing
                'measurements': {}
            }
            
            # Extract selected parameters
            for param in parameters:
                if param in df.columns:
                    value = row[param]
                    if pd.notna(value):
                        record['measurements'][param] = float(value)
            
            # Check for duplicates
            record_signature = self._create_signature(record)
            if record_signature not in self.imported_records:
                self.imported_records.add(record_signature)
                records.append(record)
            else:
                self.logger.warning(
                    f"Duplicate record skipped: {file_path}, row {idx+2}"
                )
        
        return records
    
    def _create_signature(self, record: Dict) -> tuple:
        """Create unique signature for duplicate detection."""
        measurements_tuple = tuple(sorted(record['measurements'].items()))
        return (
            record['experiment_index'],
            record['condition'],
            record['image_index'],
            measurements_tuple
        )
    
    def import_directory(self, files_metadata: List[Dict]) -> List[Dict]:
        """Import all files from directory."""
        all_records = []
        for file_meta in files_metadata:
            records = self.import_file(file_meta)
            all_records.extend(records)
        
        self.logger.info(
            f"Imported {len(all_records)} records from {len(files_metadata)} files"
        )
        return all_records
```

#### 1.6 CSV Importer

**Implementation: `core/importers/csv_importer.py`**

```python
import pandas as pd
from pathlib import Path
from typing import List, Dict, Set
import logging

class CSVImporter:
    """Imports data from CSV files."""
    
    def __init__(self, parameter_mapper: ParameterMapper):
        self.parameter_mapper = parameter_mapper
        self.logger = logging.getLogger(__name__)
        self.imported_records: Set[tuple] = set()
    
    def import_file(self, file_metadata: Dict) -> List[Dict]:
        """
        Import data from CSV file.
        
        Args:
            file_metadata: Dict with path, experiment_index, condition, etc.
            
        Returns:
            List of measurement records with origin tracking
        """
        file_path = file_metadata['path']
        parameters = self.parameter_mapper.get_all_parameters()
        
        # Read CSV with various delimiters
        df = self._read_csv_with_delimiter_detection(file_path)
        
        # Extract records (same logic as ExcelImporter)
        records = []
        for idx, row in df.iterrows():
            record = {
                'experiment_index': file_metadata['experiment_index'],
                'condition': file_metadata['condition'],
                'image_index': file_metadata['image_index'],
                'dataset_marker': file_metadata['dataset_marker'],
                'origin_file': str(file_path),
                'origin_row': idx + 2,
                'measurements': {}
            }
            
            for param in parameters:
                if param in df.columns:
                    value = row[param]
                    if pd.notna(value):
                        record['measurements'][param] = float(value)
            
            record_signature = self._create_signature(record)
            if record_signature not in self.imported_records:
                self.imported_records.add(record_signature)
                records.append(record)
            else:
                self.logger.warning(
                    f"Duplicate record skipped: {file_path}, row {idx+2}"
                )
        
        return records
    
    def _read_csv_with_delimiter_detection(self, file_path: Path) -> pd.DataFrame:
        """Try multiple delimiters to read CSV."""
        for delimiter in [',', ';', '\t']:
            try:
                df = pd.read_csv(file_path, sep=delimiter)
                if len(df.columns) > 1:  # Successfully parsed
                    return df
            except Exception as e:
                continue
        
        # Fallback to pandas default
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            self.logger.error(f"Could not parse CSV file: {file_path}")
            raise e
    
    def _create_signature(self, record: Dict) -> tuple:
        """Create unique signature for duplicate detection."""
        measurements_tuple = tuple(sorted(record['measurements'].items()))
        return (
            record['experiment_index'],
            record['condition'],
            record['image_index'],
            measurements_tuple
        )
```

#### 1.7 JSON Importer

**Implementation: `core/importers/json_importer.py`**

```python
import json
from pathlib import Path
from typing import List, Dict, Set
import logging

class JSONImporter:
    """Imports data from JSON files."""
    
    def __init__(self, parameter_mapper: ParameterMapper):
        self.parameter_mapper = parameter_mapper
        self.logger = logging.getLogger(__name__)
        self.imported_records: Set[tuple] = set()
    
    def import_file(self, file_metadata: Dict) -> List[Dict]:
        """
        Import data from JSON file.
        
        Expected JSON structure:
        {
            "measurements": [
                {"param1": value1, "param2": value2, ...},
                {"param1": value1, "param2": value2, ...}
            ]
        }
        
        OR flat structure:
        [
            {"param1": value1, "param2": value2, ...},
            {"param1": value1, "param2": value2, ...}
        ]
        """
        file_path = file_metadata['path']
        parameters = self.parameter_mapper.get_all_parameters()
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, dict) and 'measurements' in data:
            measurements_list = data['measurements']
        elif isinstance(data, list):
            measurements_list = data
        else:
            raise ValueError(f"Unsupported JSON structure in {file_path}")
        
        records = []
        for idx, measurement in enumerate(measurements_list):
            record = {
                'experiment_index': file_metadata['experiment_index'],
                'condition': file_metadata['condition'],
                'image_index': file_metadata['image_index'],
                'dataset_marker': file_metadata['dataset_marker'],
                'origin_file': str(file_path),
                'origin_row': idx + 1,
                'measurements': {}
            }
            
            for param in parameters:
                if param in measurement:
                    value = measurement[param]
                    if value is not None:
                        record['measurements'][param] = float(value)
            
            record_signature = self._create_signature(record)
            if record_signature not in self.imported_records:
                self.imported_records.add(record_signature)
                records.append(record)
            else:
                self.logger.warning(
                    f"Duplicate record skipped: {file_path}, record {idx+1}"
                )
        
        return records
    
    def _create_signature(self, record: Dict) -> tuple:
        """Create unique signature for duplicate detection."""
        measurements_tuple = tuple(sorted(record['measurements'].items()))
        return (
            record['experiment_index'],
            record['condition'],
            record['image_index'],
            measurements_tuple
        )
```

#### 1.8 Unified Importer

**Implementation: `core/importers/unified_importer.py`**

```python
from pathlib import Path
from typing import List, Dict

class UnifiedImporter:
    """Unified importer that handles all file formats."""
    
    def __init__(self, parameter_mapper: ParameterMapper):
        self.parameter_mapper = parameter_mapper
        self.excel_importer = ExcelImporter(parameter_mapper)
        self.csv_importer = CSVImporter(parameter_mapper)
        self.json_importer = JSONImporter(parameter_mapper)
    
    def import_file(self, file_metadata: Dict) -> List[Dict]:
        """
        Import file using appropriate importer based on extension.
        
        Args:
            file_metadata: Dict with path and metadata
            
        Returns:
            List of measurement records
        """
        file_path = Path(file_metadata['path'])
        extension = file_path.suffix.lower()
        
        if extension in ['.xls', '.xlsx']:
            return self.excel_importer.import_file(file_metadata)
        elif extension == '.csv':
            return self.csv_importer.import_file(file_metadata)
        elif extension == '.json':
            return self.json_importer.import_file(file_metadata)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def import_directory(self, files_metadata: List[Dict]) -> List[Dict]:
        """Import all files from directory."""
        all_records = []
        for file_meta in files_metadata:
            records = self.import_file(file_meta)
            all_records.extend(records)
        return all_records
```

---

### 2. DATABASE LAYER

#### 2.1 Abstract Database Interface

**Implementation: `core/database/base.py`**

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import pandas as pd

class DatabaseInterface(ABC):
    """Abstract base class for database operations."""
    
    @abstractmethod
    def connect(self, connection_string: str) -> None:
        """Establish database connection."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection."""
        pass
    
    @abstractmethod
    def create_schema(self) -> None:
        """Create database schema (tables, indices)."""
        pass
    
    @abstractmethod
    def insert_assay(self, assay_data: Dict) -> int:
        """Insert assay and return assay_id."""
        pass
    
    @abstractmethod
    def insert_measurements(self, assay_id: int, measurements: List[Dict]) -> None:
        """Insert measurements for an assay."""
        pass
    
    @abstractmethod
    def get_assays(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Retrieve assays with optional filtering."""
        pass
    
    @abstractmethod
    def get_measurements(self, assay_ids: List[int], 
                        parameters: Optional[List[str]] = None) -> pd.DataFrame:
        """Retrieve measurements as DataFrame."""
        pass
    
    @abstractmethod
    def get_available_parameters(self, assay_ids: List[int]) -> List[str]:
        """Get list of parameters present in specified assays."""
        pass
    
    @abstractmethod
    def get_conditions(self, assay_ids: List[int]) -> List[str]:
        """Get list of unique conditions in assays."""
        pass
```

#### 2.2 Database Schema

```sql
-- Assays table
CREATE TABLE assays (
    assay_id SERIAL PRIMARY KEY,
    experiment_index INTEGER NOT NULL,
    condition VARCHAR(100) NOT NULL,
    dataset_marker CHAR(1),  -- 'L', 'T', or NULL
    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Measurements table
CREATE TABLE measurements (
    measurement_id SERIAL PRIMARY KEY,
    assay_id INTEGER REFERENCES assays(assay_id) ON DELETE CASCADE,
    image_index INTEGER NOT NULL,
    origin_file VARCHAR(500),
    origin_row INTEGER,
    parameter_name VARCHAR(100) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    
    -- Prevent duplicates
    UNIQUE(assay_id, image_index, parameter_name, value)
);

-- Indices for performance
CREATE INDEX idx_measurements_assay ON measurements(assay_id);
CREATE INDEX idx_measurements_parameter ON measurements(parameter_name);
CREATE INDEX idx_assays_condition ON assays(condition);
CREATE INDEX idx_assays_marker ON assays(dataset_marker);
```

---

### 3. STATISTICAL ANALYSIS

#### 3.1 Statistics Engine

**Implementation: `core/processors/statistics.py`**

```python
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from typing import Dict, List, Tuple
import logging

class StatisticsEngine:
    """Performs statistical analysis on neuromorphological data."""
    
    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha
        self.logger = logging.getLogger(__name__)
    
    def test_normality(self, data: pd.Series) -> Tuple[bool, float]:
        """
        Test normality using Shapiro-Wilk test.
        
        Args:
            data: Series of values
            
        Returns:
            (is_normal, p_value)
        """
        if len(data) < 3:
            return False, np.nan
        
        statistic, p_value = stats.shapiro(data)
        is_normal = p_value > self.alpha
        
        return is_normal, p_value
    
    def anova_one_way(self, groups: Dict[str, pd.Series]) -> Dict:
        """
        Perform one-way ANOVA.
        
        Args:
            groups: Dict mapping condition names to data series
            
        Returns:
            Dict with f_statistic, p_value, is_significant
        """
        # Check normality for each group
        normality_results = {}
        for name, data in groups.items():
            is_normal, p_val = self.test_normality(data)
            normality_results[name] = {'is_normal': is_normal, 'p_value': p_val}
        
        # Perform ANOVA
        f_statistic, p_value = stats.f_oneway(*groups.values())
        
        result = {
            'f_statistic': f_statistic,
            'p_value': p_value,
            'is_significant': p_value < self.alpha,
            'normality_tests': normality_results
        }
        
        # Log warning if normality violated
        if not all(r['is_normal'] for r in normality_results.values()):
            self.logger.warning(
                "Normality assumption violated for one or more groups"
            )
        
        return result
    
    def tukey_hsd(self, data: pd.DataFrame, value_col: str, 
                  group_col: str) -> pd.DataFrame:
        """
        Perform Tukey HSD post-hoc test.
        
        Args:
            data: DataFrame with values and group labels
            value_col: Name of value column
            group_col: Name of group column
            
        Returns:
            DataFrame with pairwise comparisons
        """
        tukey = pairwise_tukeyhsd(
            endog=data[value_col],
            groups=data[group_col],
            alpha=self.alpha
        )
        
        # Convert to DataFrame
        results = pd.DataFrame(
            data=tukey.summary().data[1:], 
            columns=tukey.summary().data[0]
        )
        
        # Add significance column
        results['significant'] = results['p-adj'] < self.alpha
        
        # Only keep significant results
        results = results[results['significant']].copy()
        
        return results
    
    def pairwise_comparisons(self, groups: Dict[str, pd.Series]) -> List[Dict]:
        """
        Perform pairwise statistical comparisons.
        
        Args:
            groups: Dict mapping condition names to data series
            
        Returns:
            List of comparison results (only significant ones)
        """
        # Create DataFrame for Tukey
        data_list = []
        for name, series in groups.items():
            for value in series:
                data_list.append({'value': value, 'group': name})
        
        df = pd.DataFrame(data_list)
        
        # Run Tukey HSD
        tukey_results = self.tukey_hsd(df, 'value', 'group')
        
        # Format results
        comparisons = []
        for _, row in tukey_results.iterrows():
            comparisons.append({
                'group1': row['group1'],
                'group2': row['group2'],
                'mean_diff': row['meandiff'],
                'p_value': row['p-adj'],
                'significant': True  # Only significant ones in filtered results
            })
        
        return comparisons
    
    def calculate_summary_stats(self, data: pd.Series) -> Dict:
        """
        Calculate summary statistics for a dataset.
        
        Returns:
            Dict with mean, sem, std, median, n, etc.
        """
        return {
            'n': len(data),
            'mean': data.mean(),
            'sem': data.sem(),
            'std': data.std(),
            'median': data.median(),
            'min': data.min(),
            'max': data.max(),
            'q25': data.quantile(0.25),
            'q75': data.quantile(0.75)
        }
```

#### 3.2 Frequency Distribution Analyzer

**Implementation: `core/processors/statistics.py` (additional class)**

```python
class FrequencyAnalyzer:
    """Analyzes frequency distributions for morphological parameters."""
    
    def __init__(self, bin_size: float = 10.0):
        self.bin_size = bin_size
        self.stats_engine = StatisticsEngine()
    
    def create_frequency_distribution(self, data: pd.Series, 
                                      bin_size: Optional[float] = None) -> pd.DataFrame:
        """
        Create frequency distribution with specified bin size.
        
        Args:
            data: Series of values
            bin_size: Bin width (uses default if None)
            
        Returns:
            DataFrame with bin_start, bin_end, count, relative_freq
        """
        if bin_size is None:
            bin_size = self.bin_size
        
        # Create bins
        min_val = data.min()
        max_val = data.max()
        bins = np.arange(min_val, max_val + bin_size, bin_size)
        
        # Calculate histogram
        counts, bin_edges = np.histogram(data, bins=bins)
        
        # Create DataFrame
        freq_df = pd.DataFrame({
            'bin_start': bin_edges[:-1],
            'bin_end': bin_edges[1:],
            'count': counts,
            'relative_freq': counts / counts.sum()
        })
        
        return freq_df
    
    def compare_distributions_per_bin(self, 
                                      distributions: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Perform statistical comparisons per bin across conditions.
        
        Args:
            distributions: Dict mapping condition names to frequency DataFrames
            
        Returns:
            DataFrame with bin ranges and significance results
        """
        # Get common bins across all distributions
        all_bins = set()
        for dist in distributions.values():
            all_bins.update(zip(dist['bin_start'], dist['bin_end']))
        
        all_bins = sorted(all_bins)
        
        results = []
        for bin_start, bin_end in all_bins:
            # Extract counts for this bin from each condition
            bin_counts = {}
            for condition, dist in distributions.items():
                row = dist[(dist['bin_start'] == bin_start) & 
                          (dist['bin_end'] == bin_end)]
                if not row.empty:
                    bin_counts[condition] = row['count'].values[0]
                else:
                    bin_counts[condition] = 0
            
            # Perform chi-square test for this bin
            counts = list(bin_counts.values())
            if sum(counts) > 0:
                chi2, p_value = stats.chisquare(counts)
                significant = p_value < self.stats_engine.alpha
            else:
                chi2, p_value, significant = np.nan, np.nan, False
            
            results.append({
                'bin_start': bin_start,
                'bin_end': bin_end,
                'chi2': chi2,
                'p_value': p_value,
                'significant': significant,
                **bin_counts
            })
        
        return pd.DataFrame(results)
```

---

### 4. PLOTTING ENGINE

#### 4.1 Plot Configuration

**Implementation: `core/plotters/plot_config.py`**

**Key Concept - User-Configurable Condition Names:**
The `condition_names` dictionary allows users to define custom short→long name mappings for any condition. This is NOT hardcoded and should be configured per-analysis or saved in profiles.

Example usage:
- User has data with 'GST' condition → Sets full name to 'Gastrin Treatment'
- User has 'Ctrl' condition → Sets full name to 'Control Group'
- User has 'TreatA' condition → Sets full name to 'Treatment A: High Dose'

These mappings are:
- Configured through GUI/CLI
- Saved in analysis profiles
- Applied to plot labels and exports

```python
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors

class PlotConfig:
    """Configuration for plot styling and aesthetics."""
    
    DEFAULT_COLORS = {
        'Control': '#FFFFFF',  # White
        'GST': '#D3D3D3',      # Light grey
    }
    
    def __init__(self):
        self.condition_colors: Dict[str, str] = {}
        self.condition_names: Dict[str, str] = {}  # Short name -> Full display name
        self.plotting_order: List[str] = []
        self.plot_range: Optional[Tuple[float, float]] = None
        
        # Scatter plot settings
        self.show_scatter_dots: bool = True  # Default: show individual points
        self.scatter_alpha: float = 0.6  # Transparency
        self.scatter_size: int = 30  # Point size
        self.scatter_jitter: float = 0.1  # Jitter to prevent overlap
    
    def set_condition_color(self, condition: str, color: str) -> None:
        """
        Set color for a condition.
        
        Args:
            condition: Condition name
            color: Hex color code (e.g., '#FF0000')
        """
        # Validate color
        try:
            mcolors.hex2color(color)
            self.condition_colors[condition] = color
        except ValueError:
            raise ValueError(f"Invalid color code: {color}")
    
    def set_condition_colors_from_rgb(self, condition: str, 
                                     rgb: Tuple[int, int, int]) -> None:
        """
        Set color from RGB values (0-255).
        
        Args:
            condition: Condition name
            rgb: Tuple of (R, G, B) values
        """
        # Convert to hex
        hex_color = '#{:02x}{:02x}{:02x}'.format(*rgb)
        self.set_condition_color(condition, hex_color)
    
    def set_condition_name(self, short_name: str, full_name: str) -> None:
        """
        Map short condition name to full display name.
        
        This allows users to define custom aliases/expansions for condition names.
        For example: 'GST' -> 'Gastrin Treatment', 'Ctrl' -> 'Control Group'
        
        Args:
            short_name: Short condition code (as it appears in filenames/data)
            full_name: Full descriptive name for display in plots
        """
        self.condition_names[short_name] = full_name
    
    def set_plotting_order(self, order: List[str]) -> None:
        """Set order in which conditions appear in plots."""
        self.plotting_order = order
    
    def set_plot_range(self, y_min: float, y_max: float) -> None:
        """Set y-axis range for plots."""
        self.plot_range = (y_min, y_max)
    
    def set_scatter_settings(self, show: bool = True, alpha: float = 0.6,
                           size: int = 30, jitter: float = 0.1) -> None:
        """Configure scatter dot overlay settings."""
        self.show_scatter_dots = show
        self.scatter_alpha = alpha
        self.scatter_size = size
        self.scatter_jitter = jitter
    
    def get_color(self, condition: str) -> str:
        """Get color for condition (returns default if not set)."""
        if condition in self.condition_colors:
            return self.condition_colors[condition]
        elif condition in self.DEFAULT_COLORS:
            return self.DEFAULT_COLORS[condition]
        else:
            return self._generate_default_color(condition)
    
    def _generate_default_color(self, condition: str) -> str:
        """Generate a default color based on condition name hash."""
        hash_val = hash(condition) % 360
        return f'hsl({hash_val}, 70%, 60%)'
    
    def get_full_name(self, condition: str) -> str:
        """Get full display name for condition."""
        return self.condition_names.get(condition, condition)
    
    def apply_base_style(self, ax: plt.Axes) -> None:
        """
        Apply base styling to matplotlib axes.
        
        Args:
            ax: Matplotlib axes object
        """
        # Remove frame
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(True)
        
        # Remove x-axis ticks
        ax.tick_params(axis='x', which='both', bottom=False, top=False)
        
        # Keep y-axis ticks
        ax.tick_params(axis='y', which='both', left=True, right=False)
        
        # Apply plot range if set
        if self.plot_range:
            ax.set_ylim(self.plot_range)
    
    def to_dict(self) -> Dict:
        """Export to dict for profile saving."""
        return {
            'condition_colors': self.condition_colors,
            'condition_names': self.condition_names,
            'plotting_order': self.plotting_order,
            'plot_range': list(self.plot_range) if self.plot_range else None,
            'show_scatter_dots': self.show_scatter_dots,
            'scatter_alpha': self.scatter_alpha,
            'scatter_size': self.scatter_size,
            'scatter_jitter': self.scatter_jitter
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PlotConfig':
        """Load from dict (profile loading)."""
        config = cls()
        config.condition_colors = data.get('condition_colors', {})
        config.condition_names = data.get('condition_names', {})
        config.plotting_order = data.get('plotting_order', [])
        plot_range = data.get('plot_range')
        config.plot_range = tuple(plot_range) if plot_range else None
        config.show_scatter_dots = data.get('show_scatter_dots', True)
        config.scatter_alpha = data.get('scatter_alpha', 0.6)
        config.scatter_size = data.get('scatter_size', 30)
        config.scatter_jitter = data.get('scatter_jitter', 0.1)
        return config
```

**Workflow Example - Configuring Condition Names:**

```python
# User workflow for configuring condition display names

# 1. Create plot config
plot_config = PlotConfig()

# 2. User defines their condition name mappings
# (This would typically be done through the GUI ConditionNamesWidget)
plot_config.set_condition_name('Ctrl', 'Control Group')
plot_config.set_condition_name('GST', 'Gastrin Treatment')
plot_config.set_condition_name('TreatA', 'Treatment A: High Dose 100mg')
plot_config.set_condition_name('TreatB', 'Treatment B: Low Dose 50mg')

# 3. When creating plots, full names are used for labels
# Instead of "Ctrl" on x-axis, plot shows "Control Group"
# Instead of "GST" on x-axis, plot shows "Gastrin Treatment"

# 4. These mappings are saved in analysis profiles
profile = AnalysisProfile(
    name="My Gastrin Study",
    description="Standard analysis for gastrin experiments",
    plot_config=plot_config.to_dict(),  # Includes condition_names
    # ... other settings
)

# 5. Load profile in future analysis - condition names are restored
loaded_config = PlotConfig.from_dict(profile.plot_config)
# loaded_config.get_full_name('GST') returns 'Gastrin Treatment'
```


#### 4.2 Significance Annotator

**Implementation: `core/plotters/significance_annotator.py`**

```python
import matplotlib.pyplot as plt
from typing import List, Dict
import numpy as np

class SignificanceAnnotator:
    """Adds significance brackets and stars to plots."""
    
    @staticmethod
    def get_significance_stars(p_value: float) -> str:
        """Convert p-value to star notation."""
        if p_value < 0.001:
            return '***'
        elif p_value < 0.01:
            return '**'
        elif p_value < 0.05:
            return '*'
        else:
            return ''
    
    def add_brackets(self, ax: plt.Axes, comparisons: List[Dict], 
                    positions: Dict[str, int], height_offset: float = 1.0) -> None:
        """
        Add significance brackets to plot.
        
        Args:
            ax: Matplotlib axes
            comparisons: List of comparison dicts with group1, group2, p_value
            positions: Dict mapping condition names to x positions
            height_offset: Height offset for bracket placement
        """
        # Get current y-axis limits
        y_min, y_max = ax.get_ylim()
        y_range = y_max - y_min
        
        # Sort comparisons by distance between groups
        comparisons = sorted(
            comparisons, 
            key=lambda x: abs(positions[x['group1']] - positions[x['group2']])
        )
        
        # Track bracket heights to avoid overlaps
        bracket_level = 0
        for comp in comparisons:
            if not comp.get('significant', False):
                continue
            
            group1 = comp['group1']
            group2 = comp['group2']
            p_value = comp['p_value']
            
            # Get x positions
            x1 = positions[group1]
            x2 = positions[group2]
            
            # Calculate bracket height
            bracket_height = y_max + (bracket_level * 0.05 * y_range) + (0.02 * y_range)
            
            # Draw bracket
            self._draw_bracket(ax, x1, x2, bracket_height, y_range * 0.01)
            
            # Add stars
            stars = self.get_significance_stars(p_value)
            mid_x = (x1 + x2) / 2
            ax.text(mid_x, bracket_height + y_range * 0.01, stars,
                   ha='center', va='bottom', fontsize=12, fontweight='bold')
            
            bracket_level += 1
        
        # Adjust y-axis to accommodate brackets
        if bracket_level > 0:
            new_y_max = y_max + (bracket_level * 0.05 * y_range) + (0.05 * y_range)
            ax.set_ylim(y_min, new_y_max)
    
    def _draw_bracket(self, ax: plt.Axes, x1: float, x2: float, 
                     height: float, bar_height: float) -> None:
        """Draw a single significance bracket."""
        # Horizontal line
        ax.plot([x1, x2], [height, height], 'k-', linewidth=1.5)
        
        # Vertical lines
        ax.plot([x1, x1], [height - bar_height, height], 'k-', linewidth=1.5)
        ax.plot([x2, x2], [height - bar_height, height], 'k-', linewidth=1.5)
```

#### 4.3 Box Plot Generator

**Implementation: `core/plotters/box_plotter.py`**

```python
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, List
import numpy as np

class BoxPlotter:
    """Creates box plots with SEM and significance annotations."""
    
    def __init__(self, plot_config: PlotConfig, stats_engine: StatisticsEngine):
        self.config = plot_config
        self.stats = stats_engine
        self.annotator = SignificanceAnnotator()
    
    def create_boxplot(self, data: Dict[str, pd.Series], 
                       title: str, ylabel: str,
                       comparisons: List[Dict]) -> plt.Figure:
        """
        Create box plot with significance brackets and optional scatter overlay.
        
        Args:
            data: Dict mapping condition names to data series
            title: Plot title
            ylabel: Y-axis label
            comparisons: Statistical comparison results
            
        Returns:
            Matplotlib figure
        """
        # Determine order
        if self.config.plotting_order:
            conditions = [c for c in self.config.plotting_order if c in data]
        else:
            conditions = sorted(data.keys())
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Prepare data for plotting
        plot_data = [data[cond] for cond in conditions]
        positions = list(range(len(conditions)))
        position_map = {cond: i for i, cond in enumerate(conditions)}
        
        # Create box plot
        bp = ax.boxplot(plot_data, positions=positions, widths=0.6,
                       patch_artist=True, showmeans=True,
                       meanprops=dict(marker='D', markerfacecolor='red', 
                                    markeredgecolor='red', markersize=6))
        
        # Color boxes
        for patch, condition in zip(bp['boxes'], conditions):
            color = self.config.get_color(condition)
            patch.set_facecolor(color)
            patch.set_edgecolor('black')
            patch.set_linewidth(1.5)
        
        # Add SEM error bars
        for i, condition in enumerate(conditions):
            series = data[condition]
            mean = series.mean()
            sem = series.sem()
            
            ax.errorbar(i, mean, yerr=sem, fmt='none', ecolor='black',
                       elinewidth=2, capsize=5, capthick=2)
        
        # Add scatter dots if enabled
        if self.config.show_scatter_dots:
            for i, condition in enumerate(conditions):
                series = data[condition]
                
                # Add jitter to x-coordinates
                np.random.seed(42)  # Reproducible jitter
                x_jitter = np.random.normal(
                    i, self.config.scatter_jitter, size=len(series)
                )
                
                # Plot individual points
                ax.scatter(x_jitter, series, 
                          alpha=self.config.scatter_alpha,
                          s=self.config.scatter_size,
                          c='black',
                          edgecolors='black',
                          linewidths=0.5,
                          zorder=3)  # Ensure dots appear on top
        
        # Add n-numbers
        for i, condition in enumerate(conditions):
            n = len(data[condition])
            ax.text(i, ax.get_ylim()[0], f'n={n}',
                   ha='center', va='top', fontsize=10)
        
        # Set x-axis labels (use full names)
        ax.set_xticks(positions)
        ax.set_xticklabels(
            [self.config.get_full_name(c) for c in conditions],
            rotation=45, ha='right'
        )
        
        # Set labels
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Apply base styling
        self.config.apply_base_style(ax)
        
        # Add significance brackets
        self.annotator.add_brackets(ax, comparisons, position_map)
        
        plt.tight_layout()
        return fig
```

#### 4.4 Bar Plot Generator

**Implementation: `core/plotters/bar_plotter.py`**

```python
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, List
import numpy as np

class BarPlotter:
    """Creates bar plots with SEM and significance annotations."""
    
    def __init__(self, plot_config: PlotConfig, stats_engine: StatisticsEngine):
        self.config = plot_config
        self.stats = stats_engine
        self.annotator = SignificanceAnnotator()
    
    def create_barplot(self, data: Dict[str, pd.Series], 
                       title: str, ylabel: str,
                       comparisons: List[Dict]) -> plt.Figure:
        """
        Create bar plot with significance brackets and optional scatter overlay.
        
        Args:
            data: Dict mapping condition names to data series
            title: Plot title
            ylabel: Y-axis label
            comparisons: Statistical comparison results
            
        Returns:
            Matplotlib figure
        """
        # Determine order
        if self.config.plotting_order:
            conditions = [c for c in self.config.plotting_order if c in data]
        else:
            conditions = sorted(data.keys())
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Calculate means and SEMs
        means = [data[cond].mean() for cond in conditions]
        sems = [data[cond].sem() for cond in conditions]
        
        # Create positions
        positions = np.arange(len(conditions))
        position_map = {cond: i for i, cond in enumerate(conditions)}
        
        # Create bars
        bars = ax.bar(positions, means, width=0.6, edgecolor='black', linewidth=1.5)
        
        # Color bars
        for bar, condition in zip(bars, conditions):
            color = self.config.get_color(condition)
            bar.set_facecolor(color)
        
        # Add SEM error bars (both directions)
        ax.errorbar(positions, means, yerr=sems, fmt='none', ecolor='black',
                   elinewidth=2, capsize=5, capthick=2)
        
        # Add scatter dots if enabled
        if self.config.show_scatter_dots:
            for i, condition in enumerate(conditions):
                series = data[condition]
                
                # Add jitter
                np.random.seed(42)
                x_jitter = np.random.normal(
                    i, self.config.scatter_jitter, size=len(series)
                )
                
                # Plot individual points
                ax.scatter(x_jitter, series, 
                          alpha=self.config.scatter_alpha,
                          s=self.config.scatter_size,
                          c='black',
                          edgecolors='white',
                          linewidths=1,
                          zorder=3)
        
        # Add n-numbers
        for i, condition in enumerate(conditions):
            n = len(data[condition])
            ax.text(i, ax.get_ylim()[0], f'n={n}',
                   ha='center', va='top', fontsize=10)
        
        # Set x-axis labels
        ax.set_xticks(positions)
        ax.set_xticklabels(
            [self.config.get_full_name(c) for c in conditions],
            rotation=45, ha='right'
        )
        
        # Set labels
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Apply base styling
        self.config.apply_base_style(ax)
        
        # Add significance brackets
        self.annotator.add_brackets(ax, comparisons, position_map)
        
        plt.tight_layout()
        return fig
```

#### 4.5 Frequency Distribution Plotter

**Implementation: `core/plotters/frequency_plotter.py`**

```python
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, Optional
import numpy as np

class FrequencyPlotter:
    """Creates frequency distribution plots."""
    
    def __init__(self, plot_config: PlotConfig):
        self.config = plot_config
        self.annotator = SignificanceAnnotator()
    
    def create_frequency_plot(self, distributions: Dict[str, pd.DataFrame],
                            title: str, value_type: str = 'count',
                            bin_comparisons: Optional[pd.DataFrame] = None) -> plt.Figure:
        """
        Create frequency distribution plot.
        
        Args:
            distributions: Dict mapping conditions to frequency DataFrames
            title: Plot title
            value_type: 'count' or 'relative'
            bin_comparisons: DataFrame with per-bin significance results
            
        Returns:
            Matplotlib figure
        """
        # Determine order
        if self.config.plotting_order:
            conditions = [c for c in self.config.plotting_order if c in distributions]
        else:
            conditions = sorted(distributions.keys())
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Get all bins
        all_bins = set()
        for dist in distributions.values():
            all_bins.update(zip(dist['bin_start'], dist['bin_end']))
        all_bins = sorted(all_bins)
        
        # Create grouped bar chart
        n_conditions = len(conditions)
        n_bins = len(all_bins)
        bar_width = 0.8 / n_conditions
        
        x = np.arange(n_bins)
        
        for i, condition in enumerate(conditions):
            dist = distributions[condition]
            
            # Extract values for each bin
            values = []
            for bin_start, bin_end in all_bins:
                row = dist[(dist['bin_start'] == bin_start) & 
                          (dist['bin_end'] == bin_end)]
                if not row.empty:
                    if value_type == 'count':
                        values.append(row['count'].values[0])
                    else:
                        values.append(row['relative_freq'].values[0])
                else:
                    values.append(0)
            
            # Plot bars
            offset = (i - n_conditions/2 + 0.5) * bar_width
            color = self.config.get_color(condition)
            ax.bar(x + offset, values, bar_width, 
                  label=self.config.get_full_name(condition),
                  color=color, edgecolor='black', linewidth=1)
        
        # Set x-axis labels (bin ranges)
        bin_labels = [f'{start:.0f}-{end:.0f}' for start, end in all_bins]
        ax.set_xticks(x)
        ax.set_xticklabels(bin_labels, rotation=45, ha='right')
        
        # Labels
        ax.set_xlabel('Bin Range', fontsize=12, fontweight='bold')
        ylabel = 'Count' if value_type == 'count' else 'Relative Frequency'
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Legend
        ax.legend(frameon=False)
        
        # Apply base styling
        self.config.apply_base_style(ax)
        
        # Add significance markers if provided
        if bin_comparisons is not None:
            self._add_bin_significance_markers(ax, bin_comparisons, x)
        
        plt.tight_layout()
        return fig
    
    def _add_bin_significance_markers(self, ax: plt.Axes, 
                                     bin_comparisons: pd.DataFrame,
                                     bin_positions: np.ndarray) -> None:
        """Add significance markers above bins."""
        y_max = ax.get_ylim()[1]
        
        for idx, row in bin_comparisons.iterrows():
            if row['significant']:
                stars = self.annotator.get_significance_stars(row['p_value'])
                if stars:
                    ax.text(bin_positions[idx], y_max * 0.95, stars,
                           ha='center', va='top', fontsize=10, fontweight='bold')
```

#### 4.6 Plot Exporter (High Resolution)

**Implementation: `core/plotters/plot_exporter.py`**

```python
from pathlib import Path
import matplotlib.pyplot as plt
from typing import List, Dict

class PlotExporter:
    """Exports plots in high-resolution formats."""
    
    DEFAULT_DPI = 800
    SUPPORTED_FORMATS = ['png', 'tif', 'tiff', 'pdf', 'svg']
    
    def __init__(self, output_dir: Path, dpi: int = DEFAULT_DPI):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi
    
    def export_figure(self, fig: plt.Figure, 
                     base_name: str,
                     formats: List[str] = ['png', 'tif']) -> List[Path]:
        """
        Export matplotlib figure in multiple formats at 800 DPI.
        
        Args:
            fig: Matplotlib figure to export
            base_name: Base filename (without extension)
            formats: List of formats to export ['png', 'tif', 'pdf', 'svg']
            
        Returns:
            List of paths to exported files
        """
        exported_files = []
        
        for fmt in formats:
            if fmt not in self.SUPPORTED_FORMATS:
                raise ValueError(f"Unsupported format: {fmt}")
            
            # Normalize format name
            if fmt == 'tiff':
                fmt = 'tif'
            
            output_path = self.output_dir / f"{base_name}.{fmt}"
            
            # Export with high DPI
            fig.savefig(output_path, 
                       dpi=self.dpi,
                       format=fmt,
                       bbox_inches='tight',
                       facecolor='white',
                       edgecolor='none',
                       transparent=False)
            
            exported_files.append(output_path)
        
        return exported_files
    
    def export_multiple_figures(self, figures: Dict[str, plt.Figure],
                                formats: List[str] = ['png', 'tif']) -> Dict[str, List[Path]]:
        """
        Export multiple figures at once.
        
        Args:
            figures: Dict mapping base names to figures
            formats: Export formats
            
        Returns:
            Dict mapping base names to lists of exported file paths
        """
        results = {}
        for name, fig in figures.items():
            results[name] = self.export_figure(fig, name, formats)
        return results
```

---

### 5. EXPORT FUNCTIONALITY

#### 5.1 Export Configuration

**Implementation: `core/exporters/export_config.py`**

```python
from dataclasses import dataclass
from typing import List, Set, Optional, Dict

@dataclass
class ExportConfig:
    """Configuration for export operations."""
    
    # Format toggles
    export_excel: bool = True
    export_graphpad: bool = False  # Toggle GraphPad export
    export_csv: bool = False
    export_statistics_tables: bool = True
    
    # Plot toggles
    export_plots: bool = True
    plot_formats: List[str] = None  # ['png', 'tif']
    plot_dpi: int = 800
    
    # Plot type selection
    plot_types: Set[str] = None  # {'boxplot', 'barplot', 'frequency_count', etc.}
    
    # Condition selection
    selected_conditions: Optional[List[str]] = None  # None = all conditions
    
    # Parameter selection
    selected_parameters: List[str] = None
    
    # Dataset splitting
    split_by_marker: bool = False
    marker_names: Optional[Dict[str, str]] = None  # {'L': 'Liposomes', 'T': 'Tubules'}
    
    def __post_init__(self):
        """Set defaults."""
        if self.plot_formats is None:
            self.plot_formats = ['png', 'tif']
        
        if self.plot_types is None:
            self.plot_types = {
                'boxplot_total',
                'boxplot_relative',
                'barplot_total',
                'barplot_relative',
                'frequency_count',
                'frequency_relative'
            }
    
    def should_export_plot_type(self, plot_type: str) -> bool:
        """Check if a plot type should be exported."""
        return plot_type in self.plot_types
    
    def should_include_condition(self, condition: str) -> bool:
        """Check if a condition should be included in export."""
        if self.selected_conditions is None:
            return True  # Include all
        return condition in self.selected_conditions
    
    def get_active_plot_types(self) -> List[str]:
        """Get list of active plot types."""
        return sorted(self.plot_types)
```

#### 5.2 Parameter Selector for Export

**Implementation: `core/exporters/parameter_selector.py`**

```python
from typing import List, Set

class ExportParameterSelector:
    """Manages parameter selection for export."""
    
    def __init__(self, database: DatabaseInterface):
        self.database = database
        self.selected_parameters: Set[str] = set()
    
    def get_available_parameters(self, assay_ids: List[int]) -> List[str]:
        """Get all parameters available in specified assays."""
        return self.database.get_available_parameters(assay_ids)
    
    def select_parameters(self, parameters: List[str]) -> None:
        """Select parameters for export."""
        self.selected_parameters = set(parameters)
    
    def select_all(self, assay_ids: List[int]) -> None:
        """Select all available parameters."""
        all_params = self.get_available_parameters(assay_ids)
        self.selected_parameters = set(all_params)
    
    def get_selected(self) -> List[str]:
        """Get currently selected parameters."""
        return sorted(self.selected_parameters)
```

#### 5.3 Statistics Table Exporter

**Implementation: `core/exporters/statistics_table_exporter.py`**

```python
import pandas as pd
from pathlib import Path
from typing import Dict, List
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

class StatisticsTableExporter:
    """Exports comprehensive statistical results as formatted tables."""
    
    def __init__(self, stats_engine: StatisticsEngine):
        self.stats = stats_engine
    
    def create_statistics_tables(self, data: Dict[str, pd.Series],
                                 parameter_name: str) -> Dict[str, pd.DataFrame]:
        """
        Create comprehensive statistical tables.
        
        Returns:
            Dict with 'summary', 'anova', 'pairwise' DataFrames
        """
        tables = {}
        
        # 1. Summary statistics table
        tables['summary'] = self._create_summary_table(data, parameter_name)
        
        # 2. ANOVA results table
        tables['anova'] = self._create_anova_table(data, parameter_name)
        
        # 3. Pairwise comparisons table
        tables['pairwise'] = self._create_pairwise_table(data, parameter_name)
        
        return tables
    
    def _create_summary_table(self, data: Dict[str, pd.Series],
                             parameter_name: str) -> pd.DataFrame:
        """Create summary statistics table with values."""
        rows = []
        
        for condition, series in data.items():
            stats = self.stats.calculate_summary_stats(series)
            rows.append({
                'Parameter': parameter_name,
                'Condition': condition,
                'N': stats['n'],
                'Mean': f"{stats['mean']:.3f}",
                'SEM': f"{stats['sem']:.3f}",
                'SD': f"{stats['std']:.3f}",
                'Median': f"{stats['median']:.3f}",
                'Min': f"{stats['min']:.3f}",
                'Max': f"{stats['max']:.3f}",
                'Q25': f"{stats['q25']:.3f}",
                'Q75': f"{stats['q75']:.3f}"
            })
        
        return pd.DataFrame(rows)
    
    def _create_anova_table(self, data: Dict[str, pd.Series],
                           parameter_name: str) -> pd.DataFrame:
        """Create ANOVA results table."""
        anova_result = self.stats.anova_one_way(data)
        
        rows = [{
            'Parameter': parameter_name,
            'Test': 'One-way ANOVA',
            'F-statistic': f"{anova_result['f_statistic']:.4f}",
            'p-value': f"{anova_result['p_value']:.4e}",
            'Significant': 'Yes' if anova_result['is_significant'] else 'No',
            'Alpha': self.stats.alpha
        }]
        
        # Add normality test results
        for condition, norm_result in anova_result['normality_tests'].items():
            rows.append({
                'Parameter': parameter_name,
                'Test': f'Normality ({condition})',
                'F-statistic': '-',
                'p-value': f"{norm_result['p_value']:.4e}",
                'Significant': 'Normal' if norm_result['is_normal'] else 'Non-normal',
                'Alpha': self.stats.alpha
            })
        
        return pd.DataFrame(rows)
    
    def _create_pairwise_table(self, data: Dict[str, pd.Series],
                              parameter_name: str) -> pd.DataFrame:
        """Create pairwise comparisons table."""
        comparisons = self.stats.pairwise_comparisons(data)
        
        if not comparisons:
            return pd.DataFrame({
                'Parameter': [parameter_name],
                'Group 1': ['No significant'],
                'Group 2': ['differences found'],
                'Mean Difference': ['-'],
                'p-value': ['-'],
                'Significant': ['No']
            })
        
        rows = []
        for comp in comparisons:
            rows.append({
                'Parameter': parameter_name,
                'Group 1': comp['group1'],
                'Group 2': comp['group2'],
                'Mean Difference': f"{comp['mean_diff']:.3f}",
                'p-value': f"{comp['p_value']:.4e}",
                'Significant': self._get_significance_level(comp['p_value'])
            })
        
        return pd.DataFrame(rows)
    
    def _get_significance_level(self, p_value: float) -> str:
        """Convert p-value to significance level."""
        if p_value < 0.001:
            return '*** (p<0.001)'
        elif p_value < 0.01:
            return '** (p<0.01)'
        elif p_value < 0.05:
            return '* (p<0.05)'
        else:
            return 'ns (p≥0.05)'
    
    def export_to_excel(self, tables: Dict[str, pd.DataFrame],
                       output_path: Path) -> None:
        """Export statistical tables to formatted Excel file."""
        wb = Workbook()
        wb.remove(wb.active)
        
        # Create worksheets for each table type
        for table_name, df in tables.items():
            ws = wb.create_sheet(table_name.capitalize())
            
            # Write header
            for col_idx, col_name in enumerate(df.columns, 1):
                cell = ws.cell(row=1, column=col_idx, value=col_name)
                cell.font = Font(bold=True, size=12, color='FFFFFF')
                cell.fill = PatternFill(
                    start_color='366092', end_color='366092', fill_type='solid'
                )
                cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # Write data
            for row_idx, row in enumerate(df.itertuples(index=False), 2):
                for col_idx, value in enumerate(row, 1):
                    cell = ws.cell(row=row_idx, column=col_idx, value=value)
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                    
                    # Highlight significant results
                    if col_idx == len(row) and 'Significant' in df.columns:
                        if isinstance(value, str):
                            if value.startswith('***'):
                                cell.fill = PatternFill(
                                    start_color='FF6B6B', end_color='FF6B6B', 
                                    fill_type='solid'
                                )
                            elif value.startswith('**'):
                                cell.fill = PatternFill(
                                    start_color='FFA07A', end_color='FFA07A', 
                                    fill_type='solid'
                                )
                            elif value.startswith('*'):
                                cell.fill = PatternFill(
                                    start_color='FFD700', end_color='FFD700', 
                                    fill_type='solid'
                                )
            
            # Auto-adjust column widths
            for col in ws.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column].width = adjusted_width
        
        wb.save(output_path)
```

#### 5.4 Excel Exporter (Comprehensive)

**Implementation: `core/exporters/excel_exporter.py`**

```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

class ExcelExporter:
    """Exports comprehensive analysis results to Excel."""
    
    def __init__(self, parameter_selector: ExportParameterSelector,
                 stats_engine: StatisticsEngine):
        self.param_selector = parameter_selector
        self.stats = stats_engine
    
    def export(self, assay_ids: List[int], output_dir: Path,
               database: DatabaseInterface,
               dataset_split: Optional[Dict[str, str]] = None) -> Path:
        """
        Export comprehensive Excel file with all parameters and statistics.
        
        Args:
            assay_ids: List of assay IDs to export
            output_dir: Output directory
            database: Database interface
            dataset_split: Optional dict mapping markers to full names
            
        Returns:
            Path to created Excel file
        """
        # Get data
        parameters = self.param_selector.get_selected()
        df = database.get_measurements(assay_ids, parameters)
        
        # Create workbook
        wb = Workbook()
        wb.remove(wb.active)  # Remove default sheet
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        assay_indices = '_'.join(str(aid) for aid in sorted(assay_ids))
        filename = f'analysis_{timestamp}_assays{assay_indices}.xlsx'
        
        # Create sheets
        self._create_raw_data_sheet(wb, df)
        self._create_summary_stats_sheet(wb, df, parameters)
        self._create_frequency_sheets(wb, df, parameters)
        
        # Save
        output_path = output_dir / filename
        wb.save(output_path)
        
        return output_path
    
    def _create_raw_data_sheet(self, wb: Workbook, df: pd.DataFrame) -> None:
        """Create raw data worksheet."""
        ws = wb.create_sheet('Raw Data')
        
        # Write DataFrame to worksheet
        for r_idx, row in enumerate(df.itertuples(index=False), 1):
            for c_idx, value in enumerate(row, 1):
                ws.cell(row=r_idx, column=c_idx, value=value)
        
        # Style header
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color='CCCCCC', fill_type='solid')
    
    def _create_summary_stats_sheet(self, wb: Workbook, 
                                   df: pd.DataFrame,
                                   parameters: List[str]) -> None:
        """Create worksheet with statistical summaries."""
        ws = wb.create_sheet('Summary Statistics')
        
        # Headers
        ws.append(['Parameter', 'Condition', 'N', 'Mean', 'SEM', 'SD', 
                  'Median', 'Min', 'Max'])
        
        # Style headers
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color='CCCCCC', fill_type='solid')
        
        # Calculate stats for each parameter and condition
        for param in parameters:
            param_data = df[df['parameter_name'] == param]
            conditions = param_data['condition'].unique()
            
            for condition in sorted(conditions):
                cond_data = param_data[
                    param_data['condition'] == condition
                ]['value']
                stats = self.stats.calculate_summary_stats(cond_data)
                
                ws.append([
                    param,
                    condition,
                    stats['n'],
                    stats['mean'],
                    stats['sem'],
                    stats['std'],
                    stats['median'],
                    stats['min'],
                    stats['max']
                ])
    
    def _create_frequency_sheets(self, wb: Workbook, 
                                 df: pd.DataFrame,
                                 parameters: List[str]) -> None:
        """Create frequency distribution worksheets."""
        # Implementation depends on specific frequency distribution requirements
        pass
```

#### 5.5 GraphPad Prism Exporter

**Implementation: `core/exporters/graphpad_exporter.py`**

```python
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import pandas as pd

class GraphPadExporter:
    """Exports data in GraphPad Prism .pzfx format."""
    
    def __init__(self, parameter_selector: ExportParameterSelector):
        self.param_selector = parameter_selector
    
    def export(self, assay_ids: List[int], output_dir: Path,
               database: DatabaseInterface) -> Path:
        """
        Export .pzfx file for GraphPad Prism.
        
        Args:
            assay_ids: List of assay IDs to export
            output_dir: Output directory
            database: Database interface
            
        Returns:
            Path to created .pzfx file
        """
        # Get data
        parameters = self.param_selector.get_selected()
        df = database.get_measurements(assay_ids, parameters)
        
        # Create XML structure
        root = ET.Element('GraphPadPrismFile', {
            'xmlns': 'http://graphpad.com/prism/Prism.htm',
            'PrismXMLVersion': '5.00'
        })
        
        # Add tables for each parameter
        for param in parameters:
            self._add_parameter_table(root, df, param)
        
        # Format and save
        xml_str = self._prettify_xml(root)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        assay_indices = '_'.join(str(aid) for aid in sorted(assay_ids))
        filename = f'graphpad_{timestamp}_assays{assay_indices}.pzfx'
        output_path = output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_str)
        
        return output_path
    
    def _add_parameter_table(self, root: ET.Element, 
                            df: pd.DataFrame, parameter: str) -> None:
        """Add a table for a specific parameter."""
        # Filter data for this parameter
        param_data = df[df['parameter_name'] == parameter]
        conditions = sorted(param_data['condition'].unique())
        
        # Create table element
        table = ET.SubElement(root, 'Table', {
            'ID': f'Table_{parameter}',
            'XFormat': 'none',
            'TableType': 'OneWay',
            'EVFormat': 'AsteriskAfterNumber'
        })
        
        title = ET.SubElement(table, 'Title')
        title.text = parameter
        
        # Add columns for each condition
        for condition in conditions:
            cond_data = param_data[
                param_data['condition'] == condition
            ]['value']
            
            col = ET.SubElement(table, 'YColumn', {
                'Width': '81',
                'Decimals': '2',
                'Subcolumns': '1'
            })
            
            col_title = ET.SubElement(col, 'Title')
            col_title.text = condition
            
            # Add values
            for value in cond_data:
                subcolumn = ET.SubElement(col, 'Subcolumn')
                d = ET.SubElement(subcolumn, 'd')
                d.text = str(value)
    
    def _prettify_xml(self, elem: ET.Element) -> str:
        """Return a pretty-printed XML string."""
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
```

---

### 6. ANALYSIS PROFILES

#### 6.1 Profile Schema

**Implementation: `core/profiles/profile_schema.py`**

```python
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import json

@dataclass
class AnalysisProfile:
    """Complete analysis pipeline configuration."""
    
    name: str
    description: str
    
    # Import settings
    import_parameters: List[str]
    custom_parameters: List[str]
    supported_formats: List[str] = None  # ['xls', 'xlsx', 'csv', 'json']
    
    # Plot settings
    plot_config: Dict  # PlotConfig.to_dict()
    show_scatter_dots: bool = True
    scatter_alpha: float = 0.6
    scatter_size: int = 30
    scatter_jitter: float = 0.1
    
    # Export settings
    export_config: Dict  # ExportConfig dict
    export_parameters: List[str] = None
    
    # Condition selection
    selected_conditions: Optional[List[str]] = None  # None = all
    
    # Statistics settings
    alpha: float = 0.05
    normality_test: bool = True
    post_hoc_test: str = 'tukey'
    
    # Frequency distribution settings
    frequency_bin_size: float = 10.0
    
    # Density calculation settings
    calculate_density: bool = False
    area_per_image: float = 3.5021  # μm²
    
    # Metadata
    created_date: Optional[str] = None
    modified_date: Optional[str] = None
    
    def __post_init__(self):
        """Set defaults."""
        if self.supported_formats is None:
            self.supported_formats = ['xls', 'xlsx', 'csv', 'json']
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AnalysisProfile':
        """Load from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AnalysisProfile':
        """Load from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
```

#### 6.2 Profile Manager

**Implementation: `core/profiles/profile_manager.py`**

```python
from pathlib import Path
from typing import List, Optional
import json
from datetime import datetime

class ProfileManager:
    """Manages analysis profiles (save/load/edit/delete)."""
    
    def __init__(self, profiles_dir: Path):
        self.profiles_dir = profiles_dir
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.current_profile: Optional[AnalysisProfile] = None
    
    def save_profile(self, profile: AnalysisProfile, 
                    overwrite: bool = False) -> Path:
        """
        Save analysis profile to disk.
        
        Args:
            profile: AnalysisProfile to save
            overwrite: Allow overwriting existing profile
            
        Returns:
            Path to saved profile file
        """
        # Set timestamps
        now = datetime.now().isoformat()
        if not profile.created_date:
            profile.created_date = now
        profile.modified_date = now
        
        # Generate filename
        safe_name = profile.name.replace(' ', '_').replace('/', '_')
        filename = f'{safe_name}.json'
        filepath = self.profiles_dir / filename
        
        # Check if exists
        if filepath.exists() and not overwrite:
            raise FileExistsError(f"Profile already exists: {filename}")
        
        # Save
        with open(filepath, 'w') as f:
            f.write(profile.to_json())
        
        return filepath
    
    def load_profile(self, name: str) -> AnalysisProfile:
        """
        Load profile by name.
        
        Args:
            name: Profile name
            
        Returns:
            Loaded AnalysisProfile
        """
        safe_name = name.replace(' ', '_').replace('/', '_')
        filename = f'{safe_name}.json'
        filepath = self.profiles_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Profile not found: {name}")
        
        with open(filepath, 'r') as f:
            profile = AnalysisProfile.from_json(f.read())
        
        self.current_profile = profile
        return profile
    
    def list_profiles(self) -> List[str]:
        """Get list of available profile names."""
        profiles = []
        for file_path in self.profiles_dir.glob('*.json'):
            profiles.append(file_path.stem.replace('_', ' '))
        return sorted(profiles)
    
    def delete_profile(self, name: str) -> None:
        """Delete a profile."""
        safe_name = name.replace(' ', '_').replace('/', '_')
        filename = f'{safe_name}.json'
        filepath = self.profiles_dir / filename
        
        if filepath.exists():
            filepath.unlink()
    
    def duplicate_profile(self, source_name: str, 
                         new_name: str) -> AnalysisProfile:
        """Duplicate an existing profile with new name."""
        profile = self.load_profile(source_name)
        profile.name = new_name
        profile.created_date = None  # Will be set on save
        self.save_profile(profile)
        return profile
```

---

### 7. REPRESENTATIVE FILE ANALYSIS

**Implementation: `core/processors/representative_files.py`**

```python
import pandas as pd
import numpy as np
from typing import Dict, List
from scipy.spatial.distance import euclidean
from pathlib import Path

class RepresentativeFileAnalyzer:
    """Finds most representative files per condition."""
    
    def __init__(self, database: DatabaseInterface):
        self.database = database
    
    def analyze(self, assay_ids: List[int], 
                parameters: List[str]) -> pd.DataFrame:
        """
        Find representative files for each condition.
        
        Args:
            assay_ids: List of assay IDs to analyze
            parameters: Parameters to consider
            
        Returns:
            DataFrame with ranked files per condition
        """
        # Get all measurements
        df = self.database.get_measurements(assay_ids, parameters)
        
        results = []
        
        # Process each condition
        for condition in df['condition'].unique():
            cond_data = df[df['condition'] == condition]
            
            # Calculate average values for each parameter
            averages = {}
            for param in parameters:
                param_data = cond_data[cond_data['parameter_name'] == param]
                averages[param] = param_data['value'].mean()
            
            # Calculate distance for each file
            files = cond_data['origin_file'].unique()
            file_distances = []
            
            for file in files:
                file_data = cond_data[cond_data['origin_file'] == file]
                
                # Build vector of parameter values
                file_vector = []
                for param in parameters:
                    param_values = file_data[
                        file_data['parameter_name'] == param
                    ]['value']
                    if len(param_values) > 0:
                        file_vector.append(param_values.mean())
                    else:
                        file_vector.append(0)
                
                # Build average vector
                avg_vector = [averages.get(param, 0) for param in parameters]
                
                # Calculate Euclidean distance
                distance = euclidean(file_vector, avg_vector)
                
                file_distances.append({
                    'condition': condition,
                    'file': file,
                    'distance_from_average': distance
                })
            
            # Sort by distance (ascending = most representative first)
            file_distances_sorted = sorted(
                file_distances, 
                key=lambda x: x['distance_from_average']
            )
            
            # Add rank
            for rank, item in enumerate(file_distances_sorted, 1):
                item['rank'] = rank
                results.append(item)
        
        return pd.DataFrame(results)
    
    def export_to_csv(self, results: pd.DataFrame, output_path: Path) -> None:
        """Export representative files list to CSV."""
        results.to_csv(output_path, index=False)
```

---

### 8. GUI COMPONENTS

#### 8.1 Condition Names Manager Widget

**Implementation: `gui/widgets/condition_names_widget.py`**

This widget allows users to configure short→long name mappings for conditions.

```python
import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable, Optional

class ConditionNamesWidget(ttk.Frame):
    """Widget for configuring condition short→long name mappings."""
    
    def __init__(self, parent, conditions: List[str], 
                 callback: Optional[Callable] = None):
        super().__init__(parent)
        self.conditions = conditions
        self.callback = callback
        self.name_entries: Dict[str, tk.StringVar] = {}
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create input fields for each condition."""
        ttk.Label(
            self, text="Condition Display Names:", 
            font=('TkDefaultFont', 10, 'bold')
        ).grid(row=0, column=0, columnspan=3, sticky='w', pady=5)
        
        ttk.Label(self, text="Short Name").grid(row=1, column=0, sticky='w', padx=5)
        ttk.Label(self, text="Full Display Name").grid(row=1, column=1, sticky='w', padx=5)
        
        # Create row for each condition
        for idx, condition in enumerate(self.conditions, start=2):
            # Short name (read-only)
            ttk.Label(self, text=condition).grid(row=idx, column=0, sticky='w', padx=5, pady=2)
            
            # Full name (editable)
            name_var = tk.StringVar(value=condition)  # Default to short name
            self.name_entries[condition] = name_var
            
            entry = ttk.Entry(self, textvariable=name_var, width=40)
            entry.grid(row=idx, column=1, sticky='ew', padx=5, pady=2)
            entry.bind('<FocusOut>', lambda e: self._on_change())
            
            # Reset button
            ttk.Button(
                self, text="Reset", 
                command=lambda c=condition: self._reset_condition(c),
                width=8
            ).grid(row=idx, column=2, padx=5, pady=2)
        
        self.columnconfigure(1, weight=1)
    
    def _reset_condition(self, condition: str):
        """Reset condition to its short name."""
        self.name_entries[condition].set(condition)
        self._on_change()
    
    def _on_change(self):
        """Called when any entry changes."""
        if self.callback:
            self.callback()
    
    def get_condition_names(self) -> Dict[str, str]:
        """Get dictionary of short→full name mappings."""
        mappings = {}
        for short_name, var in self.name_entries.items():
            full_name = var.get().strip()
            if full_name and full_name != short_name:
                mappings[short_name] = full_name
        return mappings
    
    def set_condition_names(self, mappings: Dict[str, str]):
        """Set condition names from dictionary."""
        for short_name, full_name in mappings.items():
            if short_name in self.name_entries:
                self.name_entries[short_name].set(full_name)
    
    def update_conditions(self, new_conditions: List[str]):
        """Update available conditions."""
        # Clear existing
        for widget in self.winfo_children():
            widget.destroy()
        
        self.conditions = new_conditions
        self.name_entries = {}
        self._create_widgets()
```

**Usage Example in Main GUI:**
```python
# In plot configuration dialog
condition_names_widget = ConditionNamesWidget(
    parent=dialog,
    conditions=['Control', 'GST', 'TreatmentA'],
    callback=self.on_names_changed
)

# Get mappings for PlotConfig
mappings = condition_names_widget.get_condition_names()
for short, full in mappings.items():
    plot_config.set_condition_name(short, full)
```

#### 8.2 Color Picker Widget

**Implementation: `gui/widgets/color_picker.py`**

```python
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

class ColorPickerWidget(ttk.Frame):
    """RGB color picker with live preview."""
    
    def __init__(self, parent, initial_color: str = '#FFFFFF', 
                 callback: Optional[Callable] = None):
        super().__init__(parent)
        self.callback = callback
        self.current_color = initial_color
        
        # RGB sliders
        self.r_var = tk.IntVar(value=255)
        self.g_var = tk.IntVar(value=255)
        self.b_var = tk.IntVar(value=255)
        
        self._create_widgets()
        self._set_color_from_hex(initial_color)
    
    def _create_widgets(self):
        """Create RGB sliders and preview."""
        # R slider
        ttk.Label(self, text='R:').grid(row=0, column=0, sticky='w')
        r_slider = ttk.Scale(
            self, from_=0, to=255, orient='horizontal',
            variable=self.r_var, command=self._on_color_change
        )
        r_slider.grid(row=0, column=1, sticky='ew', padx=5)
        ttk.Label(self, textvariable=self.r_var).grid(row=0, column=2)
        
        # G slider
        ttk.Label(self, text='G:').grid(row=1, column=0, sticky='w')
        g_slider = ttk.Scale(
            self, from_=0, to=255, orient='horizontal',
            variable=self.g_var, command=self._on_color_change
        )
        g_slider.grid(row=1, column=1, sticky='ew', padx=5)
        ttk.Label(self, textvariable=self.g_var).grid(row=1, column=2)
        
        # B slider
        ttk.Label(self, text='B:').grid(row=2, column=0, sticky='w')
        b_slider = ttk.Scale(
            self, from_=0, to=255, orient='horizontal',
            variable=self.b_var, command=self._on_color_change
        )
        b_slider.grid(row=2, column=1, sticky='ew', padx=5)
        ttk.Label(self, textvariable=self.b_var).grid(row=2, column=2)
        
        # Hex display
        self.hex_label = ttk.Label(self, text='#FFFFFF', font=('Courier', 12))
        self.hex_label.grid(row=3, column=0, columnspan=3, pady=5)
        
        # Color preview
        self.preview = tk.Canvas(self, width=100, height=50, bg='white')
        self.preview.grid(row=4, column=0, columnspan=3, pady=5)
    
    def _on_color_change(self, *args):
        """Update preview when sliders change."""
        r = self.r_var.get()
        g = self.g_var.get()
        b = self.b_var.get()
        
        hex_color = f'#{r:02x}{g:02x}{b:02x}'
        self.current_color = hex_color
        
        # Update preview
        self.preview.configure(bg=hex_color)
        self.hex_label.configure(text=hex_color)
        
        # Callback
        if self.callback:
            self.callback(hex_color)
    
    def _set_color_from_hex(self, hex_color: str):
        """Set sliders from hex color."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        self.r_var.set(r)
        self.g_var.set(g)
        self.b_var.set(b)
    
    def get_color(self) -> str:
        """Get current color as hex."""
        return self.current_color
```

#### 8.3 Export Configuration Widget

**Implementation: `gui/widgets/export_config_widget.py`**

```python
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

class ExportConfigWidget(ttk.Frame):
    """Widget for configuring export options."""
    
    def __init__(self, parent, callback: Optional[Callable] = None):
        super().__init__(parent)
        self.callback = callback
        
        # Variables
        self.export_excel_var = tk.BooleanVar(value=True)
        self.export_graphpad_var = tk.BooleanVar(value=False)
        self.export_csv_var = tk.BooleanVar(value=False)
        self.export_stats_var = tk.BooleanVar(value=True)
        self.export_plots_var = tk.BooleanVar(value=True)
        
        # Plot type variables
        self.plot_boxplot_total_var = tk.BooleanVar(value=True)
        self.plot_boxplot_relative_var = tk.BooleanVar(value=True)
        self.plot_barplot_total_var = tk.BooleanVar(value=True)
        self.plot_barplot_relative_var = tk.BooleanVar(value=True)
        self.plot_freq_count_var = tk.BooleanVar(value=True)
        self.plot_freq_relative_var = tk.BooleanVar(value=True)
        
        # Plot format variables
        self.plot_png_var = tk.BooleanVar(value=True)
        self.plot_tif_var = tk.BooleanVar(value=True)
        self.plot_pdf_var = tk.BooleanVar(value=False)
        self.plot_svg_var = tk.BooleanVar(value=False)
        
        self.plot_dpi_var = tk.IntVar(value=800)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create all widgets."""
        # Export Formats Section
        formats_frame = ttk.LabelFrame(self, text="Export Formats", padding=10)
        formats_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        ttk.Checkbutton(
            formats_frame, text="Excel (.xlsx)", 
            variable=self.export_excel_var
        ).grid(row=0, column=0, sticky='w')
        ttk.Checkbutton(
            formats_frame, text="GraphPad Prism (.pzfx)", 
            variable=self.export_graphpad_var
        ).grid(row=1, column=0, sticky='w')
        ttk.Checkbutton(
            formats_frame, text="CSV", 
            variable=self.export_csv_var
        ).grid(row=2, column=0, sticky='w')
        ttk.Checkbutton(
            formats_frame, text="Statistical Tables", 
            variable=self.export_stats_var
        ).grid(row=3, column=0, sticky='w')
        
        # Plot Types Section
        plots_frame = ttk.LabelFrame(self, text="Plot Types", padding=10)
        plots_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        
        ttk.Checkbutton(
            plots_frame, text="Export Plots", 
            variable=self.export_plots_var,
            command=self._toggle_plot_options
        ).grid(row=0, column=0, columnspan=2, sticky='w')
        
        self.plot_options_frame = ttk.Frame(plots_frame)
        self.plot_options_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=20)
        
        ttk.Checkbutton(
            self.plot_options_frame, text="Box Plot - Total Length", 
            variable=self.plot_boxplot_total_var
        ).grid(row=0, column=0, sticky='w')
        ttk.Checkbutton(
            self.plot_options_frame, text="Box Plot - Relative Length", 
            variable=self.plot_boxplot_relative_var
        ).grid(row=1, column=0, sticky='w')
        ttk.Checkbutton(
            self.plot_options_frame, text="Bar Plot - Total Length", 
            variable=self.plot_barplot_total_var
        ).grid(row=2, column=0, sticky='w')
        ttk.Checkbutton(
            self.plot_options_frame, text="Bar Plot - Relative Length", 
            variable=self.plot_barplot_relative_var
        ).grid(row=3, column=0, sticky='w')
        ttk.Checkbutton(
            self.plot_options_frame, text="Frequency Distribution - Count", 
            variable=self.plot_freq_count_var
        ).grid(row=4, column=0, sticky='w')
        ttk.Checkbutton(
            self.plot_options_frame, text="Frequency Distribution - Relative", 
            variable=self.plot_freq_relative_var
        ).grid(row=5, column=0, sticky='w')
        
        # Plot Format Section
        format_frame = ttk.LabelFrame(
            self.plot_options_frame, text="Plot Formats", padding=5
        )
        format_frame.grid(row=6, column=0, sticky='ew', pady=5)
        
        ttk.Checkbutton(
            format_frame, text="PNG", 
            variable=self.plot_png_var
        ).grid(row=0, column=0, sticky='w')
        ttk.Checkbutton(
            format_frame, text="TIF", 
            variable=self.plot_tif_var
        ).grid(row=0, column=1, sticky='w')
        ttk.Checkbutton(
            format_frame, text="PDF", 
            variable=self.plot_pdf_var
        ).grid(row=1, column=0, sticky='w')
        ttk.Checkbutton(
            format_frame, text="SVG", 
            variable=self.plot_svg_var
        ).grid(row=1, column=1, sticky='w')
        
        # DPI Setting
        dpi_frame = ttk.Frame(format_frame)
        dpi_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=5)
        ttk.Label(dpi_frame, text="DPI:").grid(row=0, column=0, sticky='w')
        ttk.Entry(
            dpi_frame, textvariable=self.plot_dpi_var, width=10
        ).grid(row=0, column=1, sticky='w', padx=5)
    
    def _toggle_plot_options(self):
        """Enable/disable plot options based on export_plots checkbox."""
        state = 'normal' if self.export_plots_var.get() else 'disabled'
        for child in self.plot_options_frame.winfo_children():
            if isinstance(child, (ttk.Checkbutton, ttk.LabelFrame)):
                try:
                    child.configure(state=state)
                except:
                    pass
    
    def get_config(self) -> ExportConfig:
        """Get ExportConfig from widget state."""
        plot_types = set()
        if self.plot_boxplot_total_var.get():
            plot_types.add('boxplot_total')
        if self.plot_boxplot_relative_var.get():
            plot_types.add('boxplot_relative')
        if self.plot_barplot_total_var.get():
            plot_types.add('barplot_total')
        if self.plot_barplot_relative_var.get():
            plot_types.add('barplot_relative')
        if self.plot_freq_count_var.get():
            plot_types.add('frequency_count')
        if self.plot_freq_relative_var.get():
            plot_types.add('frequency_relative')
        
        plot_formats = []
        if self.plot_png_var.get():
            plot_formats.append('png')
        if self.plot_tif_var.get():
            plot_formats.append('tif')
        if self.plot_pdf_var.get():
            plot_formats.append('pdf')
        if self.plot_svg_var.get():
            plot_formats.append('svg')
        
        return ExportConfig(
            export_excel=self.export_excel_var.get(),
            export_graphpad=self.export_graphpad_var.get(),
            export_csv=self.export_csv_var.get(),
            export_statistics_tables=self.export_stats_var.get(),
            export_plots=self.export_plots_var.get(),
            plot_types=plot_types,
            plot_formats=plot_formats,
            plot_dpi=self.plot_dpi_var.get()
        )
```

#### 8.4 Condition Selector Widget

**Implementation: `gui/widgets/condition_selector_widget.py`**

```python
import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Optional

class ConditionSelectorWidget(ttk.Frame):
    """Widget for selecting which conditions to include in analysis/export."""
    
    def __init__(self, parent, conditions: List[str], 
                 callback: Optional[Callable] = None):
        super().__init__(parent)
        self.conditions = conditions
        self.callback = callback
        self.condition_vars = {}
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create checkboxes for each condition."""
        ttk.Label(
            self, text="Select Conditions:", 
            font=('TkDefaultFont', 10, 'bold')
        ).grid(row=0, column=0, sticky='w', pady=5)
        
        # Select All / Deselect All buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=1, column=0, sticky='ew', pady=5)
        
        ttk.Button(
            button_frame, text="Select All", 
            command=self._select_all
        ).grid(row=0, column=0, padx=5)
        ttk.Button(
            button_frame, text="Deselect All", 
            command=self._deselect_all
        ).grid(row=0, column=1, padx=5)
        
        # Condition checkboxes
        checkbox_frame = ttk.Frame(self)
        checkbox_frame.grid(row=2, column=0, sticky='ew')
        
        for idx, condition in enumerate(self.conditions):
            var = tk.BooleanVar(value=True)  # All selected by default
            self.condition_vars[condition] = var
            
            ttk.Checkbutton(
                checkbox_frame, text=condition, 
                variable=var,
                command=self._on_change
            ).grid(row=idx, column=0, sticky='w', pady=2)
    
    def _select_all(self):
        """Select all conditions."""
        for var in self.condition_vars.values():
            var.set(True)
        if self.callback:
            self.callback()
    
    def _deselect_all(self):
        """Deselect all conditions."""
        for var in self.condition_vars.values():
            var.set(False)
        if self.callback:
            self.callback()
    
    def _on_change(self):
        """Called when checkbox state changes."""
        if self.callback:
            self.callback()
    
    def get_selected_conditions(self) -> List[str]:
        """Get list of selected conditions."""
        return [cond for cond, var in self.condition_vars.items() if var.get()]
    
    def update_conditions(self, new_conditions: List[str]):
        """Update available conditions."""
        # Clear existing
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    child.destroy()
        
        self.conditions = new_conditions
        self.condition_vars = {}
        self._create_widgets()
```

---

## IMPLEMENTATION ROADMAP

### **Release v0.1.0 - Core Functionality (Week 1-2)**

**Goals:**
- Functional import with parameter selection (all formats)
- Database layer working
- Basic export to Excel

**Tasks:**
1. Set up project structure
2. Implement database layer (PostgreSQL + SQLite)
3. Implement file scanner and header scanner (XLS/XLSX/CSV/JSON)
4. Implement parameter mapper
5. Implement all importers (Excel, CSV, JSON, Unified)
6. Basic Excel exporter (all parameters)
7. Basic GUI for import
8. Unit tests for core modules

**Deliverables:**
- Can import data from XLS/XLSX/CSV/JSON with parameter selection
- Data stored in database with duplicate prevention
- Export to Excel with all parameters

---

### **Release v0.2.0 - Statistics & Plotting (Week 3-4)**

**Goals:**
- Complete statistical analysis
- All plot types implemented
- Significance annotations
- 800 DPI export in PNG/TIF

**Tasks:**
1. Implement StatisticsEngine (normality, ANOVA, Tukey HSD)
2. Implement FrequencyAnalyzer
3. Implement PlotConfig (with scatter dot settings)
4. Implement SignificanceAnnotator
5. Implement BoxPlotter (with scatter overlay)
6. Implement BarPlotter (with scatter overlay)
7. Implement FrequencyPlotter
8. Implement PlotExporter (800 DPI, PNG/TIF)
9. GUI: plot preview and customization
10. Tests for statistics and plotting

**Deliverables:**
- Publication-quality plots at 800 DPI
- Statistical analysis with ANOVA and post-hoc
- Significance brackets on plots
- Scatter dot overlay option
- PNG and TIF export

---

### **Release v0.3.0 - Advanced Export & Profiles (Week 5-6)**

**Goals:**
- GraphPad export with toggle
- Analysis profiles
- Representative file analysis
- Statistics tables

**Tasks:**
1. Implement GraphPadExporter
2. Implement ExportParameterSelector
3. Implement StatisticsTableExporter
4. Implement ExportConfig dataclass
5. Implement comprehensive ExcelExporter
6. Implement AnalysisProfile schema
7. Implement ProfileManager
8. Implement RepresentativeFileAnalyzer
9. GUI: profile management
10. GUI: export parameter selection
11. GUI: export configuration widget
12. GUI: condition selector widget
13. Tests for exporters and profiles

**Deliverables:**
- .pzfx export for GraphPad (toggleable)
- Save/load analysis pipelines
- Representative file ranking
- Formatted statistics tables
- Condition and plot type selection

---

### **Release v0.4.0 - Architecture & Quality (Week 7-8)**

**Goals:**
- Refactor to adapter pattern
- Comprehensive testing
- CLI implementation

**Tasks:**
1. Refactor GUI to use adapter
2. Implement CLI interface
3. Implement CLIAdapter
4. Comprehensive test suite (>80% coverage)
5. Integration tests for full workflows
6. CI/CD with GitHub Actions
7. Code cleanup and PEP 8 compliance
8. Type hints throughout

**Deliverables:**
- Clean adapter architecture
- Both GUI and CLI working
- Automated testing
- CI/CD pipeline

---

### **Release v1.0.0 - JOSS Publication (Week 9-10)**

**Goals:**
- JOSS-compliant repository
- Complete documentation
- Community features

**Tasks:**
1. Write paper.md (JOSS manuscript)
2. Create comprehensive README.md
3. Write user guide documentation
4. Write developer guide
5. Create example notebooks
6. Add CITATION.cff
7. Add CONTRIBUTING.md
8. Add CODE_OF_CONDUCT.md
9. Create executable builds (.exe for Windows)
10. Final testing and polish

**Deliverables:**
- JOSS submission-ready repository
- Complete documentation
- Windows/Mac/Linux executables
- Example data and tutorials

---

## TESTING STRATEGY

### Unit Tests

**Coverage targets:** >80% for core modules

**Key test files:**
- `test_database.py`: Database operations
- `test_importers.py`: All importers (Excel, CSV, JSON, Unified)
- `test_statistics.py`: All statistical functions
- `test_plotters.py`: Plot generation (mocked matplotlib)
- `test_exporters.py`: Excel, GraphPad, Statistics tables
- `test_profiles.py`: Profile save/load/manage

### Integration Tests

**Full workflow tests:**
- Import (all formats) → Database → Export
- Import → Statistics → Plots → Export
- Profile save → Load → Apply → Verify
- Multi-format import workflow

### CI/CD Pipeline

**GitHub Actions workflow (.github/workflows/tests.yml):**
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: pytest --cov=src --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## DOCUMENTATION REQUIREMENTS

### README.md Structure

```markdown
# Neuromorphological Data Analyzer

[![Tests](https://github.com/username/repo/workflows/Tests/badge.svg)](link)
[![Coverage](https://codecov.io/gh/username/repo/branch/main/graph/badge.svg)](link)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](link)

## Overview
Comprehensive Python tool for neuromorphological data analysis with statistical analysis, publication-quality plotting, and multi-format export.

## Features
- **Import:** XLS, XLSX, CSV, JSON with dynamic parameter selection
- **Statistics:** Normality testing, ANOVA, Tukey HSD post-hoc
- **Plotting:** Box plots, bar plots, frequency distributions (800 DPI PNG/TIF)
- **Export:** Excel, GraphPad Prism (.pzfx), statistical tables
- **Profiles:** Save/load complete analysis pipelines
- **GUI & CLI:** Both interfaces supported

## Installation
```bash
pip install neuromorpho-analyzer
```

## Quick Start
```python
from neuromorpho_analyzer import Analyzer

analyzer = Analyzer()
analyzer.import_data('path/to/data/')
analyzer.analyze()
analyzer.export_all()
```

## Documentation
- [User Guide](docs/user_guide/)
- [API Reference](docs/api/)
- [Developer Guide](docs/developer_guide/)

## Citation
```bibtex
@software{neuromorpho_analyzer,
  author = {Your Name},
  title = {Neuromorphological Data Analyzer},
  year = {2025},
  url = {https://github.com/username/repo}
}
```

## License
MIT License - see LICENSE file
```

### User Guide Topics

1. **Getting Started**
   - Installation
   - Basic workflow
   - Understanding the interface

2. **Importing Data**
   - Supported formats (XLS, XLSX, CSV, JSON)
   - File naming conventions
   - Parameter selection
   - Dataset markers (L/T)

3. **Statistical Analysis**
   - Normality testing
   - ANOVA
   - Post-hoc tests
   - Interpreting results

4. **Creating Plots**
   - Plot types
   - Customization (colors, order, scatter dots)
   - Significance annotations
   - Export settings (DPI, formats)

5. **Exporting Results**
   - Excel export
   - GraphPad Prism export
   - Statistical tables
   - Representative files

6. **Analysis Profiles**
   - Creating profiles
   - Loading profiles
   - Managing profiles

### Developer Guide Topics

1. **Architecture Overview**
   - Adapter pattern
   - Core logic separation
   - Database abstraction

2. **Contributing Guidelines**
   - Code style (PEP 8)
   - Type hints
   - Testing requirements
   - Pull request process

3. **Testing**
   - Running tests
   - Writing tests
   - Coverage requirements

4. **Adding New Features**
   - File format support
   - Plot types
   - Export formats

---

## CODING STANDARDS

### Type Hints
All functions must have type hints:
```python
def process_data(input: pd.DataFrame, 
                 parameters: List[str]) -> Dict[str, pd.Series]:
    """Process data and return results by condition."""
    pass
```

### Docstrings
All public functions/classes need docstrings (Google style):
```python
def calculate_statistics(data: pd.Series) -> Dict:
    """
    Calculate summary statistics for dataset.
    
    Args:
        data: Series of numerical values
        
    Returns:
        Dict containing mean, sem, std, etc.
        
    Raises:
        ValueError: If data is empty
    """
    pass
```

### Logging
Use logging instead of print:
```python
import logging

logger = logging.getLogger(__name__)
logger.info("Processing started")
logger.warning("Normality assumption violated")
logger.error("Failed to import file")
```

### Error Handling
Specific exceptions with informative messages:
```python
try:
    data = import_file(path)
except FileNotFoundError:
    logger.error(f"File not found: {path}")
    raise
except Exception as e:
    logger.error(f"Error reading file: {e}")
    raise ValueError(f"Invalid file: {path}")
```

---

## COMPLETE IMPLEMENTATION CHECKLIST

### Phase 1: Foundation
- [ ] Set up project structure
- [ ] Implement database abstract interface
- [ ] Implement PostgreSQL backend
- [ ] Implement SQLite backend
- [ ] Implement FileScanner (XLS/XLSX/CSV/JSON)
- [ ] Implement HeaderScanner (all formats)
- [ ] Implement ParameterMapper
- [ ] Implement ExcelImporter
- [ ] Implement CSVImporter
- [ ] Implement JSONImporter
- [ ] Implement UnifiedImporter
- [ ] Basic tests for import modules

### Phase 2: Analysis Core
- [ ] Implement StatisticsEngine (normality, ANOVA, Tukey HSD)
- [ ] Implement FrequencyAnalyzer
- [ ] Implement PlotConfig (with scatter settings)
- [ ] Implement SignificanceAnnotator
- [ ] Implement BoxPlotter (with scatter overlay)
- [ ] Implement BarPlotter (with scatter overlay)
- [ ] Implement FrequencyPlotter
- [ ] Implement PlotExporter (800 DPI PNG/TIF)
- [ ] Tests for statistics and plotting

### Phase 3: Export & Profiles
- [ ] Implement ExportConfig dataclass
- [ ] Implement ExportParameterSelector
- [ ] Implement StatisticsTableExporter
- [ ] Implement comprehensive ExcelExporter
- [ ] Implement GraphPadExporter
- [ ] Implement AnalysisProfile schema
- [ ] Implement ProfileManager
- [ ] Implement RepresentativeFileAnalyzer
- [ ] Tests for exporters and profiles

### Phase 4: Interfaces
- [ ] Implement GUIAdapter
- [ ] Create main GUI window
- [ ] Implement ParameterSelectorWidget
- [ ] Implement ConditionNamesWidget (for configuring short→long name mappings)
- [ ] Implement ColorPickerWidget
- [ ] Implement PlotPreviewWidget
- [ ] Implement ProfileManagerWidget
- [ ] Implement ExportConfigWidget
- [ ] Implement ConditionSelectorWidget
- [ ] Implement CLIAdapter
- [ ] Create CLI commands (import, export, analyze, plot)
- [ ] Tests for adapters

### Phase 5: Quality & Documentation
- [ ] Comprehensive unit test suite (>80% coverage)
- [ ] Integration tests for full workflows
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] README.md with badges
- [ ] User guide (all sections)
- [ ] Developer guide (all sections)
- [ ] API reference documentation
- [ ] JOSS paper.md
- [ ] CITATION.cff
- [ ] CONTRIBUTING.md
- [ ] CODE_OF_CONDUCT.md
- [ ] Example data and notebooks
- [ ] Executable builds (.exe, .app, Linux binary)

---

## KEY SUCCESS METRICS

### Code Quality
- [ ] >80% test coverage
- [ ] All tests passing
- [ ] No linting errors (flake8)
- [ ] Type hints throughout
- [ ] Comprehensive docstrings

### Functionality
- [ ] Import from XLS/XLSX/CSV/JSON ✓
- [ ] Dynamic parameter selection ✓
- [ ] All plot types working (box, bar, frequency) ✓
- [ ] Scatter dot overlay toggle ✓
- [ ] 800 DPI PNG/TIF export ✓
- [ ] Statistical analysis complete (ANOVA, post-hoc) ✓
- [ ] Statistics tables export ✓
- [ ] Excel export working ✓
- [ ] GraphPad export working (toggleable) ✓
- [ ] Profiles save/load working ✓
- [ ] Representative files analysis ✓
- [ ] Condition selection ✓
- [ ] Plot type selection ✓

### User Experience
- [ ] GUI intuitive and responsive
- [ ] CLI clear and documented
- [ ] Error messages helpful
- [ ] Examples and tutorials available
- [ ] Documentation complete

### Publication Readiness
- [ ] JOSS manuscript complete
- [ ] All JOSS requirements met
- [ ] Example data included
- [ ] Citation file present
- [ ] Community guidelines present
- [ ] MIT license included

---

## QUICK REFERENCE: Feature Summary

| Feature | Implementation Location |
|---------|------------------------|
| **XLS/XLSX Import** | `core/importers/excel_importer.py` |
| **CSV Import** | `core/importers/csv_importer.py` |
| **JSON Import** | `core/importers/json_importer.py` |
| **Unified Import** | `core/importers/unified_importer.py` |
| **Parameter Selection** | `core/importers/parameter_mapper.py` |
| **Database (Abstract)** | `core/database/base.py` |
| **PostgreSQL** | `core/database/postgres.py` |
| **SQLite** | `core/database/sqlite.py` |
| **Statistics Engine** | `core/processors/statistics.py` |
| **Frequency Analysis** | `core/processors/statistics.py` |
| **Plot Config** | `core/plotters/plot_config.py` |
| **Box Plots** | `core/plotters/box_plotter.py` |
| **Bar Plots** | `core/plotters/bar_plotter.py` |
| **Frequency Plots** | `core/plotters/frequency_plotter.py` |
| **Significance Brackets** | `core/plotters/significance_annotator.py` |
| **800 DPI Export** | `core/plotters/plot_exporter.py` |
| **Excel Export** | `core/exporters/excel_exporter.py` |
| **GraphPad Export** | `core/exporters/graphpad_exporter.py` |
| **Statistics Tables** | `core/exporters/statistics_table_exporter.py` |
| **Export Config** | `core/exporters/export_config.py` |
| **Analysis Profiles** | `core/profiles/profile_schema.py` |
| **Profile Manager** | `core/profiles/profile_manager.py` |
| **Representative Files** | `core/processors/representative_files.py` |
| **GUI Adapter** | `adapters/gui_adapter.py` |
| **CLI Adapter** | `adapters/cli_adapter.py` |
| **Condition Names Widget** | `gui/widgets/condition_names_widget.py` |
| **Color Picker Widget** | `gui/widgets/color_picker.py` |
| **Export Config Widget** | `gui/widgets/export_config_widget.py` |
| **Condition Selector** | `gui/widgets/condition_selector_widget.py` |

---

## DEFAULT VALUES & CONSTANTS

```python
# core/utils/constants.py

# Default colors
DEFAULT_COLORS = {
    'Control': '#FFFFFF',  # White
    'GST': '#D3D3D3',      # Light grey
}

# Plot settings
DEFAULT_DPI = 800
DEFAULT_PLOT_FORMATS = ['png', 'tif']
DEFAULT_SCATTER_ALPHA = 0.6
DEFAULT_SCATTER_SIZE = 30
DEFAULT_SCATTER_JITTER = 0.1

# Statistics settings
DEFAULT_ALPHA = 0.05
DEFAULT_POST_HOC = 'tukey'

# Frequency distribution
DEFAULT_BIN_SIZE = 10.0

# Density calculation
DEFAULT_AREA_PER_IMAGE = 3.5021  # μm²

# Supported file formats
SUPPORTED_FORMATS = ['.xls', '.xlsx', '.csv', '.json']

# Database schemas
DB_SCHEMA_VERSION = '1.0'
```

---

## END OF GUIDE

This comprehensive guide provides all necessary specifications, code examples, and implementation details for Claude Code to build the complete neuromorphological data analysis tool. Follow the roadmap step-by-step, implementing features in the order specified, with testing at each phase.

**Remember:**
1. Start with Phase 1 (Foundation)
2. Test each module before moving to the next
3. Follow the adapter pattern strictly
4. Maintain >80% test coverage
5. Document everything
6. Aim for JOSS publication quality

Good luck with the implementation!
