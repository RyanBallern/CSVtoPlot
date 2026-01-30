"""Dynamic parameter selection and mapping for data import."""

from typing import List, Dict, Set, Optional


class ParameterMapper:
    """Manages dynamic parameter selection for import."""

    def __init__(self, available_headers: List[str]):
        """
        Initialize the ParameterMapper.

        Args:
            available_headers: List of column headers available in the data files
        """
        self.available_headers = list(available_headers)
        self.selected_parameters: Set[str] = set()
        self.custom_parameters: Set[str] = set()
        self.parameter_aliases: Dict[str, str] = {}  # Maps alias -> original name

    def select_parameters(self, parameters: List[str]) -> None:
        """
        Select parameters from available headers.

        Args:
            parameters: List of parameter names to select
        """
        for param in parameters:
            if param in self.available_headers:
                self.selected_parameters.add(param)

    def select_all_parameters(self) -> None:
        """Select all available parameters."""
        self.selected_parameters = set(self.available_headers)

    def deselect_parameter(self, parameter: str) -> None:
        """
        Deselect a parameter.

        Args:
            parameter: Parameter name to deselect
        """
        self.selected_parameters.discard(parameter)

    def clear_selection(self) -> None:
        """Clear all selected parameters."""
        self.selected_parameters.clear()

    def add_custom_parameter(self, parameter: str) -> None:
        """
        Add a custom parameter not in headers.

        Args:
            parameter: Custom parameter name
        """
        self.custom_parameters.add(parameter)
        self.selected_parameters.add(parameter)

    def add_parameter_alias(self, original_name: str, alias: str) -> None:
        """
        Add an alias for a parameter (e.g., "Len" -> "Length").

        Args:
            original_name: Original parameter name from headers
            alias: Alias/short name to use
        """
        if original_name in self.available_headers or original_name in self.custom_parameters:
            self.parameter_aliases[alias] = original_name

    def get_all_parameters(self) -> List[str]:
        """
        Get all selected parameters (from headers + custom).

        Returns:
            Sorted list of all selected parameters
        """
        return sorted(self.selected_parameters)

    def get_standard_parameters(self) -> List[str]:
        """
        Get selected parameters from headers only (excluding custom).

        Returns:
            Sorted list of standard parameters
        """
        standard = self.selected_parameters - self.custom_parameters
        return sorted(standard)

    def get_custom_parameters(self) -> List[str]:
        """
        Get custom parameters only.

        Returns:
            Sorted list of custom parameters
        """
        return sorted(self.custom_parameters)

    def is_parameter_selected(self, parameter: str) -> bool:
        """
        Check if a parameter is selected.

        Args:
            parameter: Parameter name to check

        Returns:
            True if parameter is selected, False otherwise
        """
        return parameter in self.selected_parameters

    def get_parameter_count(self) -> int:
        """
        Get count of selected parameters.

        Returns:
            Number of selected parameters
        """
        return len(self.selected_parameters)

    def resolve_alias(self, alias: str) -> Optional[str]:
        """
        Resolve an alias to its original parameter name.

        Args:
            alias: Alias to resolve

        Returns:
            Original parameter name or None if alias not found
        """
        return self.parameter_aliases.get(alias)

    def to_dict(self) -> Dict:
        """
        Serialize to dictionary for saving.

        Returns:
            Dictionary representation of the mapper state
        """
        return {
            'available_headers': self.available_headers,
            'selected_parameters': list(self.selected_parameters),
            'custom_parameters': list(self.custom_parameters),
            'parameter_aliases': self.parameter_aliases
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ParameterMapper':
        """
        Deserialize from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            ParameterMapper instance
        """
        mapper = cls(data['available_headers'])
        mapper.selected_parameters = set(data['selected_parameters'])
        mapper.custom_parameters = set(data['custom_parameters'])
        mapper.parameter_aliases = data['parameter_aliases']
        return mapper

    def __repr__(self) -> str:
        """String representation of the mapper."""
        return (f"ParameterMapper(available={len(self.available_headers)}, "
                f"selected={len(self.selected_parameters)}, "
                f"custom={len(self.custom_parameters)})")
