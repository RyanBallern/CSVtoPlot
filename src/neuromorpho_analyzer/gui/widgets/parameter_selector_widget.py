"""Widget for selecting which parameters to include in analysis/export."""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Callable, Optional


class ParameterSelectorWidget(ttk.Frame):
    """Widget for selecting which parameters to include in analysis/export.

    Provides a listbox with multiple selection support for choosing parameters.

    Example:
        widget = ParameterSelectorWidget(
            parent=root,
            parameters=['Length', 'Volume', 'Branch Points', 'Surface Area'],
            callback=on_selection_change
        )
        selected = widget.get_selected_parameters()
        # ['Length', 'Volume'] if those are selected
    """

    def __init__(self, parent, parameters: List[str],
                 callback: Optional[Callable] = None,
                 show_checkboxes: bool = True):
        """Initialize parameter selector widget.

        Args:
            parent: Parent tkinter widget
            parameters: List of parameter names
            callback: Optional callback when selection changes
            show_checkboxes: If True, use checkboxes; if False, use listbox
        """
        super().__init__(parent)
        self.parameters = parameters
        self.callback = callback
        self.show_checkboxes = show_checkboxes
        self.param_vars: Dict[str, tk.BooleanVar] = {}

        self._create_widgets()

    def _create_widgets(self):
        """Create selection widgets."""
        ttk.Label(
            self, text="Select Parameters:",
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

        if self.show_checkboxes:
            self._create_checkboxes()
        else:
            self._create_listbox()

    def _create_checkboxes(self):
        """Create checkbox for each parameter."""
        # Scrollable frame for checkboxes
        canvas = tk.Canvas(self, height=200)
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)
        self.checkbox_frame = ttk.Frame(canvas)

        self.checkbox_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )

        canvas.create_window((0, 0), window=self.checkbox_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=2, column=0, sticky='nsew')
        scrollbar.grid(row=2, column=1, sticky='ns')

        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

        # Create checkboxes
        for idx, param in enumerate(self.parameters):
            var = tk.BooleanVar(value=True)  # All selected by default
            self.param_vars[param] = var

            ttk.Checkbutton(
                self.checkbox_frame, text=param,
                variable=var,
                command=self._on_change
            ).grid(row=idx, column=0, sticky='w', pady=1)

    def _create_listbox(self):
        """Create listbox for parameter selection."""
        list_frame = ttk.Frame(self)
        list_frame.grid(row=2, column=0, sticky='nsew')

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')

        self.listbox = tk.Listbox(
            list_frame,
            selectmode='multiple',
            height=10,
            yscrollcommand=scrollbar.set
        )
        self.listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.listbox.yview)

        for param in self.parameters:
            self.listbox.insert('end', param)
            self.listbox.selection_set('end')  # Select all by default

        self.listbox.bind('<<ListboxSelect>>', lambda e: self._on_change())

        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

    def _select_all(self):
        """Select all parameters."""
        if self.show_checkboxes:
            for var in self.param_vars.values():
                var.set(True)
        else:
            self.listbox.selection_set(0, 'end')
        self._on_change()

    def _deselect_all(self):
        """Deselect all parameters."""
        if self.show_checkboxes:
            for var in self.param_vars.values():
                var.set(False)
        else:
            self.listbox.selection_clear(0, 'end')
        self._on_change()

    def _on_change(self):
        """Called when selection changes."""
        if self.callback:
            self.callback()

    def get_selected_parameters(self) -> List[str]:
        """Get list of selected parameters.

        Returns:
            List of parameter names that are selected
        """
        if self.show_checkboxes:
            return [param for param, var in self.param_vars.items() if var.get()]
        else:
            indices = self.listbox.curselection()
            return [self.parameters[i] for i in indices]

    def get_excluded_parameters(self) -> List[str]:
        """Get list of excluded (unselected) parameters.

        Returns:
            List of parameter names that are not selected
        """
        selected = set(self.get_selected_parameters())
        return [p for p in self.parameters if p not in selected]

    def is_selected(self, parameter: str) -> bool:
        """Check if a specific parameter is selected.

        Args:
            parameter: Parameter name to check

        Returns:
            True if parameter is selected
        """
        return parameter in self.get_selected_parameters()

    def set_selected(self, parameters: List[str]):
        """Set which parameters are selected.

        Args:
            parameters: List of parameter names to select (others will be deselected)
        """
        if self.show_checkboxes:
            for param, var in self.param_vars.items():
                var.set(param in parameters)
        else:
            self.listbox.selection_clear(0, 'end')
            for i, param in enumerate(self.parameters):
                if param in parameters:
                    self.listbox.selection_set(i)
        self._on_change()

    def update_parameters(self, new_parameters: List[str],
                          preserve_selection: bool = True):
        """Update available parameters.

        Args:
            new_parameters: New list of parameter names
            preserve_selection: If True, preserve selection state for parameters
                               that exist in both old and new lists
        """
        # Remember current selection
        old_selection = set(self.get_selected_parameters()) if preserve_selection else set()

        self.parameters = new_parameters

        if self.show_checkboxes:
            # Clear existing checkboxes
            for widget in self.checkbox_frame.winfo_children():
                widget.destroy()

            self.param_vars = {}

            # Create new checkboxes
            for idx, param in enumerate(self.parameters):
                selected = param in old_selection if preserve_selection else True
                var = tk.BooleanVar(value=selected)
                self.param_vars[param] = var

                ttk.Checkbutton(
                    self.checkbox_frame, text=param,
                    variable=var,
                    command=self._on_change
                ).grid(row=idx, column=0, sticky='w', pady=1)
        else:
            self.listbox.delete(0, 'end')
            for param in self.parameters:
                self.listbox.insert('end', param)

            if preserve_selection:
                for i, param in enumerate(self.parameters):
                    if param in old_selection:
                        self.listbox.selection_set(i)

    def get_selection_count(self) -> int:
        """Get number of selected parameters.

        Returns:
            Number of selected parameters
        """
        return len(self.get_selected_parameters())

    def has_selection(self) -> bool:
        """Check if at least one parameter is selected.

        Returns:
            True if at least one parameter is selected
        """
        return self.get_selection_count() > 0
