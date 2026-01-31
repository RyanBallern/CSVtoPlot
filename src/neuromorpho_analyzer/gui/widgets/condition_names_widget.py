"""Widget for configuring condition short→long name mappings."""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Callable, Optional


class ConditionNamesWidget(ttk.Frame):
    """Widget for configuring condition short→long name mappings.

    Allows users to specify display names for conditions that differ
    from their short names used in the data files.

    Example:
        widget = ConditionNamesWidget(
            parent=root,
            conditions=['GST', 'HXT', 'ctrl'],
            callback=on_names_changed
        )
        # User edits: GST → "GST Treatment", ctrl → "Control"
        mappings = widget.get_condition_names()
        # {'GST': 'GST Treatment', 'ctrl': 'Control'}
    """

    def __init__(self, parent, conditions: List[str],
                 callback: Optional[Callable] = None):
        """Initialize condition names widget.

        Args:
            parent: Parent tkinter widget
            conditions: List of condition short names
            callback: Optional callback when names change
        """
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
            entry.bind('<Return>', lambda e: self._on_change())

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
        """Get dictionary of short→full name mappings.

        Only returns mappings where full name differs from short name.

        Returns:
            Dictionary mapping short names to full display names
        """
        mappings = {}
        for short_name, var in self.name_entries.items():
            full_name = var.get().strip()
            if full_name and full_name != short_name:
                mappings[short_name] = full_name
        return mappings

    def get_all_names(self) -> Dict[str, str]:
        """Get all condition names (including unchanged ones).

        Returns:
            Dictionary mapping short names to display names
        """
        return {short: var.get().strip() or short
                for short, var in self.name_entries.items()}

    def set_condition_names(self, mappings: Dict[str, str]):
        """Set condition names from dictionary.

        Args:
            mappings: Dictionary of short→full name mappings
        """
        for short_name, full_name in mappings.items():
            if short_name in self.name_entries:
                self.name_entries[short_name].set(full_name)

    def update_conditions(self, new_conditions: List[str]):
        """Update available conditions.

        Args:
            new_conditions: New list of condition names
        """
        # Clear existing
        for widget in self.winfo_children():
            widget.destroy()

        self.conditions = new_conditions
        self.name_entries = {}
        self._create_widgets()

    def reset_all(self):
        """Reset all conditions to their short names."""
        for condition in self.conditions:
            self._reset_condition(condition)
