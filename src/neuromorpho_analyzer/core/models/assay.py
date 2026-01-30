"""Assay data model."""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Assay:
    """
    Represents a neuromorphological assay/experiment.

    An assay groups related measurements together, typically representing
    a single experiment or analysis session.
    """

    name: str
    description: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = field(default_factory=datetime.now)

    def __repr__(self) -> str:
        """String representation of assay."""
        return f"Assay(id={self.id}, name='{self.name}')"

    def to_dict(self) -> dict:
        """
        Convert assay to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Assay':
        """
        Create Assay from dictionary.

        Args:
            data: Dictionary with assay data

        Returns:
            Assay instance
        """
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return cls(
            name=data['name'],
            description=data.get('description'),
            id=data.get('id'),
            created_at=created_at
        )
