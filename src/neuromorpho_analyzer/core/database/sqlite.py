"""SQLite database backend for single-user workflows."""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any
import pandas as pd
import json
from datetime import datetime

from .base import DatabaseBase


class SQLiteDatabase(DatabaseBase):
    """SQLite database implementation for single-user workflows."""

    def __init__(self, db_path: Path = None):
        """
        Initialize SQLite database.

        Args:
            db_path: Path to SQLite database file (default: ./data.db)
        """
        if db_path is None:
            db_path = Path.cwd() / 'data.db'
        self.db_path = Path(db_path)
        self.connection = None

    def connect(self) -> None:
        """Establish database connection."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Enable column access by name
        self.create_tables()

    def disconnect(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def create_tables(self) -> None:
        """Create necessary database tables."""
        cursor = self.connection.cursor()

        # Create assays table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create measurements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assay_id INTEGER NOT NULL,
                source_file TEXT,
                condition TEXT,
                parameters TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (assay_id) REFERENCES assays(id) ON DELETE CASCADE
            )
        ''')

        # Create index on assay_id for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_measurements_assay
            ON measurements(assay_id)
        ''')

        # Create index on condition for faster filtering
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_measurements_condition
            ON measurements(condition)
        ''')

        self.connection.commit()

    def insert_assay(self, name: str, description: Optional[str] = None) -> int:
        """
        Insert a new assay.

        Args:
            name: Assay name
            description: Optional assay description

        Returns:
            Assay ID
        """
        cursor = self.connection.cursor()
        cursor.execute(
            'INSERT INTO assays (name, description) VALUES (?, ?)',
            (name, description)
        )
        self.connection.commit()
        return cursor.lastrowid

    def get_assay(self, assay_id: int) -> Optional[Dict[str, Any]]:
        """
        Get assay by ID.

        Args:
            assay_id: Assay ID

        Returns:
            Assay data dictionary or None if not found
        """
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM assays WHERE id = ?', (assay_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None

    def get_assay_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get assay by name.

        Args:
            name: Assay name

        Returns:
            Assay data dictionary or None if not found
        """
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM assays WHERE name = ?', (name,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None

    def list_assays(self) -> List[Dict[str, Any]]:
        """
        List all assays.

        Returns:
            List of assay dictionaries
        """
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM assays ORDER BY created_at DESC')
        return [dict(row) for row in cursor.fetchall()]

    def insert_measurements(
        self,
        assay_id: int,
        measurements: pd.DataFrame,
        source_file: Optional[str] = None,
        condition: Optional[str] = None,
        check_duplicates: bool = True
    ) -> int:
        """
        Insert measurements for an assay.

        Args:
            assay_id: Assay ID
            measurements: DataFrame with measurement data
            source_file: Source file name
            condition: Experimental condition
            check_duplicates: Whether to check for duplicate measurements

        Returns:
            Number of measurements inserted
        """
        if check_duplicates:
            # Check for duplicates based on source_file and condition
            existing = self.get_measurements(assay_id, condition=condition)
            if not existing.empty and source_file:
                # Filter existing measurements from same source file
                existing_sources = self._get_measurement_sources(assay_id, condition)
                if source_file in existing_sources:
                    # Duplicate detected - skip insertion
                    return 0

        cursor = self.connection.cursor()
        inserted_count = 0

        # Insert each measurement row
        for _, row in measurements.iterrows():
            # Convert row to JSON for storage
            parameters_json = row.to_json()

            cursor.execute('''
                INSERT INTO measurements (assay_id, source_file, condition, parameters)
                VALUES (?, ?, ?, ?)
            ''', (assay_id, source_file, condition, parameters_json))
            inserted_count += 1

        self.connection.commit()
        return inserted_count

    def _get_measurement_sources(self, assay_id: int, condition: Optional[str] = None) -> List[str]:
        """
        Get list of source files for an assay.

        Args:
            assay_id: Assay ID
            condition: Filter by condition (optional)

        Returns:
            List of source file names
        """
        cursor = self.connection.cursor()

        if condition:
            cursor.execute('''
                SELECT DISTINCT source_file FROM measurements
                WHERE assay_id = ? AND condition = ?
            ''', (assay_id, condition))
        else:
            cursor.execute('''
                SELECT DISTINCT source_file FROM measurements
                WHERE assay_id = ?
            ''', (assay_id,))

        return [row[0] for row in cursor.fetchall() if row[0]]

    def get_measurements(
        self,
        assay_id: int,
        condition: Optional[str] = None,
        parameters: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Get measurements for an assay.

        Args:
            assay_id: Assay ID
            condition: Filter by condition (optional)
            parameters: List of parameters to retrieve (None = all)

        Returns:
            DataFrame with measurements
        """
        cursor = self.connection.cursor()

        if condition:
            cursor.execute('''
                SELECT parameters, source_file, condition FROM measurements
                WHERE assay_id = ? AND condition = ?
            ''', (assay_id, condition))
        else:
            cursor.execute('''
                SELECT parameters, source_file, condition FROM measurements
                WHERE assay_id = ?
            ''', (assay_id,))

        rows = cursor.fetchall()

        if not rows:
            return pd.DataFrame()

        # Parse JSON parameters back into DataFrame
        data = []
        for row in rows:
            params = json.loads(row[0])
            params['source_file'] = row[1]
            params['condition'] = row[2]
            data.append(params)

        df = pd.DataFrame(data)

        # Filter to selected parameters if specified
        if parameters:
            available_params = [p for p in parameters if p in df.columns]
            metadata_cols = ['source_file', 'condition']
            cols_to_keep = available_params + [c for c in metadata_cols if c in df.columns]
            df = df[cols_to_keep]

        return df

    def delete_assay(self, assay_id: int) -> None:
        """
        Delete an assay and all its measurements.

        Args:
            assay_id: Assay ID
        """
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM measurements WHERE assay_id = ?', (assay_id,))
        cursor.execute('DELETE FROM assays WHERE id = ?', (assay_id,))
        self.connection.commit()

    def get_measurement_count(self, assay_id: int) -> int:
        """
        Get count of measurements for an assay.

        Args:
            assay_id: Assay ID

        Returns:
            Number of measurements
        """
        cursor = self.connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM measurements WHERE assay_id = ?', (assay_id,))
        return cursor.fetchone()[0]

    def get_conditions(self, assay_id: int) -> List[str]:
        """
        Get list of conditions for an assay.

        Args:
            assay_id: Assay ID

        Returns:
            List of condition names
        """
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT DISTINCT condition FROM measurements
            WHERE assay_id = ? AND condition IS NOT NULL
            ORDER BY condition
        ''', (assay_id,))
        return [row[0] for row in cursor.fetchall()]

    def get_parameters(self, assay_id: int) -> List[str]:
        """
        Get list of parameters stored for an assay.

        Args:
            assay_id: Assay ID

        Returns:
            List of parameter names
        """
        # Get one measurement and extract parameter names
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT parameters FROM measurements
            WHERE assay_id = ?
            LIMIT 1
        ''', (assay_id,))

        row = cursor.fetchone()
        if row:
            params = json.loads(row[0])
            return list(params.keys())
        return []
