"""Abstract base class for database operations."""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from pathlib import Path
import pandas as pd


class DatabaseBase(ABC):
    """Abstract base class for database backends."""

    @abstractmethod
    def connect(self) -> None:
        """Establish database connection."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection."""
        pass

    @abstractmethod
    def create_tables(self) -> None:
        """Create necessary database tables."""
        pass

    @abstractmethod
    def insert_assay(self, name: str, description: Optional[str] = None) -> int:
        """
        Insert a new assay.

        Args:
            name: Assay name
            description: Optional assay description

        Returns:
            Assay ID
        """
        pass

    @abstractmethod
    def get_assay(self, assay_id: int) -> Optional[Dict[str, Any]]:
        """
        Get assay by ID.

        Args:
            assay_id: Assay ID

        Returns:
            Assay data dictionary or None if not found
        """
        pass

    @abstractmethod
    def get_assay_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get assay by name.

        Args:
            name: Assay name

        Returns:
            Assay data dictionary or None if not found
        """
        pass

    @abstractmethod
    def list_assays(self) -> List[Dict[str, Any]]:
        """
        List all assays.

        Returns:
            List of assay dictionaries
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def delete_assay(self, assay_id: int) -> None:
        """
        Delete an assay and all its measurements.

        Args:
            assay_id: Assay ID
        """
        pass

    @abstractmethod
    def get_measurement_count(self, assay_id: int) -> int:
        """
        Get count of measurements for an assay.

        Args:
            assay_id: Assay ID

        Returns:
            Number of measurements
        """
        pass

    @abstractmethod
    def get_conditions(self, assay_id: int) -> List[str]:
        """
        Get list of conditions for an assay.

        Args:
            assay_id: Assay ID

        Returns:
            List of condition names
        """
        pass

    @abstractmethod
    def get_parameters(self, assay_id: int) -> List[str]:
        """
        Get list of parameters stored for an assay.

        Args:
            assay_id: Assay ID

        Returns:
            List of parameter names
        """
        pass

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
