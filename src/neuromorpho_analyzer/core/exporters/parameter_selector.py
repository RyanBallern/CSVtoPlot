"""Parameter selection for export operations."""

from typing import List, Set
from ..database.base import DatabaseBase


class ExportParameterSelector:
    """Manages parameter selection for export."""

    def __init__(self, database: DatabaseBase):
        """Initialize parameter selector.

        Args:
            database: Database interface for accessing parameter data
        """
        self.database = database
        self.selected_parameters: Set[str] = set()

    def get_available_parameters(self, assay_ids: List[int]) -> List[str]:
        """Get all parameters available in specified assays.

        Args:
            assay_ids: List of assay IDs

        Returns:
            List of available parameter names
        """
        # Collect parameters from all assays
        all_params = set()
        for assay_id in assay_ids:
            params = self.database.get_parameters(assay_id)
            all_params.update(params)
        return sorted(all_params)

    def select_parameters(self, parameters: List[str]) -> None:
        """Select parameters for export.

        Args:
            parameters: List of parameter names to select
        """
        self.selected_parameters = set(parameters)

    def select_all(self, assay_ids: List[int]) -> None:
        """Select all available parameters.

        Args:
            assay_ids: List of assay IDs
        """
        all_params = self.get_available_parameters(assay_ids)
        self.selected_parameters = set(all_params)

    def get_selected(self) -> List[str]:
        """Get currently selected parameters.

        Returns:
            Sorted list of selected parameter names
        """
        return sorted(self.selected_parameters)

    def clear_selection(self) -> None:
        """Clear all selected parameters."""
        self.selected_parameters.clear()

    def is_selected(self, parameter: str) -> bool:
        """Check if a parameter is selected.

        Args:
            parameter: Parameter name

        Returns:
            True if parameter is selected
        """
        return parameter in self.selected_parameters

    def toggle_parameter(self, parameter: str) -> None:
        """Toggle parameter selection.

        Args:
            parameter: Parameter name
        """
        if parameter in self.selected_parameters:
            self.selected_parameters.remove(parameter)
        else:
            self.selected_parameters.add(parameter)
