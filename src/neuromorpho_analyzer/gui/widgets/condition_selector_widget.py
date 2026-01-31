"""Widget for selecting which conditions to include in analysis/export."""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Callable, Optional


class ConditionSelectorWidget(ttk.Frame):
    """Widget for selecting which conditions to include in analysis/export.

    Provides checkboxes for each condition with Select All / Deselect All buttons.

    Example:
        widget = ConditionSelectorWidget(
            parent=root,
            conditions=['Control', 'Treatment A', 'Treatment B'],
            callback=on_selection_change
        )
        selected = widget.get_selected_conditions()
        # ['Control', 'Treatment A'] if Treatment B unchecked
    """

    def __init__(self, parent, conditions: List[str],
                 callback: Optional[Callable] = None):
        """Initialize condition selector widget.

        Args:
            parent: Parent tkinter widget
            conditions: List of condition names
            callback: Optional callback when selection changes
        """
        super().__init__(parent)
        self.conditions = conditions
        self.callback = callback
        self.condition_vars: Dict[str, tk.BooleanVar] = {}

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
        self.checkbox_frame = ttk.Frame(self)
        self.checkbox_frame.grid(row=2, column=0, sticky='ew')

        self._create_checkboxes()

    def _create_checkboxes(self):
        """Create checkbox for each condition."""
        for idx, condition in enumerate(self.conditions):
            var = tk.BooleanVar(value=True)  # All selected by default
            self.condition_vars[condition] = var

            ttk.Checkbutton(
                self.checkbox_frame, text=condition,
                variable=var,
                command=self._on_change
            ).grid(row=idx, column=0, sticky='w', pady=2)

    def _select_all(self):
        """Select all conditions."""
        for var in self.condition_vars.values():
            var.set(True)
        self._on_change()

    def _deselect_all(self):
        """Deselect all conditions."""
        for var in self.condition_vars.values():
            var.set(False)
        self._on_change()

    def _on_change(self):
        """Called when checkbox state changes."""
        if self.callback:
            self.callback()

    def get_selected_conditions(self) -> List[str]:
        """Get list of selected conditions.

        Returns:
            List of condition names that are selected
        """
        return [cond for cond, var in self.condition_vars.items() if var.get()]

    def get_excluded_conditions(self) -> List[str]:
        """Get list of excluded (unselected) conditions.

        Returns:
            List of condition names that are not selected
        """
        return [cond for cond, var in self.condition_vars.items() if not var.get()]

    def is_selected(self, condition: str) -> bool:
        """Check if a specific condition is selected.

        Args:
            condition: Condition name to check

        Returns:
            True if condition is selected
        """
        if condition in self.condition_vars:
            return self.condition_vars[condition].get()
        return False

    def set_selected(self, conditions: List[str]):
        """Set which conditions are selected.

        Args:
            conditions: List of condition names to select (others will be deselected)
        """
        for cond, var in self.condition_vars.items():
            var.set(cond in conditions)
        self._on_change()

    def update_conditions(self, new_conditions: List[str],
                          preserve_selection: bool = True):
        """Update available conditions.

        Args:
            new_conditions: New list of condition names
            preserve_selection: If True, preserve selection state for conditions
                               that exist in both old and new lists
        """
        # Remember current selection
        old_selection = set(self.get_selected_conditions()) if preserve_selection else set()

        # Clear existing checkboxes
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()

        self.conditions = new_conditions
        self.condition_vars = {}
        self._create_checkboxes()

        # Restore selection for conditions that still exist
        if preserve_selection:
            for cond, var in self.condition_vars.items():
                var.set(cond in old_selection)

    def get_selection_count(self) -> int:
        """Get number of selected conditions.

        Returns:
            Number of selected conditions
        """
        return len(self.get_selected_conditions())

    def has_selection(self) -> bool:
        """Check if at least one condition is selected.

        Returns:
            True if at least one condition is selected
        """
        return self.get_selection_count() > 0
