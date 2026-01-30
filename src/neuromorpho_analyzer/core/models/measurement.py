"""Measurement data model."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Measurement:
    """
    Represents a single neuromorphological measurement.

    Measurements contain the actual data values (parameters) for a specific
    observation, along with metadata about its source and condition.
    """

    assay_id: int
    parameters: Dict[str, Any]
    source_file: Optional[str] = None
    condition: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = field(default_factory=datetime.now)

    def __repr__(self) -> str:
        """String representation of measurement."""
        param_count = len(self.parameters) if self.parameters else 0
        return f"Measurement(id={self.id}, assay_id={self.assay_id}, params={param_count})"

    def get_parameter(self, param_name: str, default: Any = None) -> Any:
        """
        Get parameter value.

        Args:
            param_name: Parameter name
            default: Default value if parameter not found

        Returns:
            Parameter value or default
        """
        return self.parameters.get(param_name, default)

    def set_parameter(self, param_name: str, value: Any) -> None:
        """
        Set parameter value.

        Args:
            param_name: Parameter name
            value: Parameter value
        """
        self.parameters[param_name] = value

    def has_parameter(self, param_name: str) -> bool:
        """
        Check if parameter exists.

        Args:
            param_name: Parameter name

        Returns:
            True if parameter exists, False otherwise
        """
        return param_name in self.parameters

    def to_dict(self) -> dict:
        """
        Convert measurement to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'assay_id': self.assay_id,
            'source_file': self.source_file,
            'condition': self.condition,
            'parameters': self.parameters,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Measurement':
        """
        Create Measurement from dictionary.

        Args:
            data: Dictionary with measurement data

        Returns:
            Measurement instance
        """
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return cls(
            assay_id=data['assay_id'],
            parameters=data['parameters'],
            source_file=data.get('source_file'),
            condition=data.get('condition'),
            id=data.get('id'),
            created_at=created_at
        )
