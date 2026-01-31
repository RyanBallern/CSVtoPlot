"""RGB color picker widget with live preview."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Tuple


class ColorPickerWidget(ttk.Frame):
    """RGB color picker with live preview.

    Provides sliders for R, G, B values with a live color preview
    and hex value display.

    Example:
        picker = ColorPickerWidget(
            parent=root,
            initial_color='#3366FF',
            callback=on_color_change
        )
        color = picker.get_color()  # Returns '#3366ff'
    """

    def __init__(self, parent, initial_color: str = '#FFFFFF',
                 callback: Optional[Callable[[str], None]] = None):
        """Initialize color picker widget.

        Args:
            parent: Parent tkinter widget
            initial_color: Initial color as hex string (e.g., '#FF0000')
            callback: Optional callback when color changes, receives hex string
        """
        super().__init__(parent)
        self.callback = callback
        self.current_color = initial_color

        # RGB variables
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
        self.r_label = ttk.Label(self, text='255', width=4)
        self.r_label.grid(row=0, column=2)

        # G slider
        ttk.Label(self, text='G:').grid(row=1, column=0, sticky='w')
        g_slider = ttk.Scale(
            self, from_=0, to=255, orient='horizontal',
            variable=self.g_var, command=self._on_color_change
        )
        g_slider.grid(row=1, column=1, sticky='ew', padx=5)
        self.g_label = ttk.Label(self, text='255', width=4)
        self.g_label.grid(row=1, column=2)

        # B slider
        ttk.Label(self, text='B:').grid(row=2, column=0, sticky='w')
        b_slider = ttk.Scale(
            self, from_=0, to=255, orient='horizontal',
            variable=self.b_var, command=self._on_color_change
        )
        b_slider.grid(row=2, column=1, sticky='ew', padx=5)
        self.b_label = ttk.Label(self, text='255', width=4)
        self.b_label.grid(row=2, column=2)

        # Hex entry
        hex_frame = ttk.Frame(self)
        hex_frame.grid(row=3, column=0, columnspan=3, pady=5)
        ttk.Label(hex_frame, text='Hex:').pack(side='left')
        self.hex_var = tk.StringVar(value='#FFFFFF')
        self.hex_entry = ttk.Entry(hex_frame, textvariable=self.hex_var, width=10)
        self.hex_entry.pack(side='left', padx=5)
        self.hex_entry.bind('<Return>', self._on_hex_entry)
        self.hex_entry.bind('<FocusOut>', self._on_hex_entry)

        # Color preview
        self.preview = tk.Canvas(self, width=100, height=40, bg='white',
                                  highlightthickness=1, highlightbackground='gray')
        self.preview.grid(row=4, column=0, columnspan=3, pady=5)

        self.columnconfigure(1, weight=1)

    def _on_color_change(self, *args):
        """Update preview when sliders change."""
        r = int(self.r_var.get())
        g = int(self.g_var.get())
        b = int(self.b_var.get())

        # Update labels
        self.r_label.configure(text=str(r))
        self.g_label.configure(text=str(g))
        self.b_label.configure(text=str(b))

        hex_color = f'#{r:02x}{g:02x}{b:02x}'
        self.current_color = hex_color

        # Update hex entry
        self.hex_var.set(hex_color.upper())

        # Update preview
        self.preview.configure(bg=hex_color)

        # Callback
        if self.callback:
            self.callback(hex_color)

    def _on_hex_entry(self, event=None):
        """Handle hex value entry."""
        hex_value = self.hex_var.get().strip()
        if self._is_valid_hex(hex_value):
            self._set_color_from_hex(hex_value)

    def _is_valid_hex(self, hex_color: str) -> bool:
        """Check if string is a valid hex color."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return False
        try:
            int(hex_color, 16)
            return True
        except ValueError:
            return False

    def _set_color_from_hex(self, hex_color: str):
        """Set sliders from hex color.

        Args:
            hex_color: Hex color string (e.g., '#FF0000' or 'FF0000')
        """
        hex_color = hex_color.lstrip('#')
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)

            self.r_var.set(r)
            self.g_var.set(g)
            self.b_var.set(b)

            self._on_color_change()
        except (ValueError, IndexError):
            pass  # Invalid hex, ignore

    def get_color(self) -> str:
        """Get current color as hex string.

        Returns:
            Hex color string (e.g., '#ff0000')
        """
        return self.current_color

    def get_rgb(self) -> Tuple[int, int, int]:
        """Get current color as RGB tuple.

        Returns:
            Tuple of (R, G, B) values (0-255)
        """
        return (int(self.r_var.get()),
                int(self.g_var.get()),
                int(self.b_var.get()))

    def set_color(self, hex_color: str):
        """Set color from hex string.

        Args:
            hex_color: Hex color string (e.g., '#FF0000')
        """
        self._set_color_from_hex(hex_color)

    def set_rgb(self, r: int, g: int, b: int):
        """Set color from RGB values.

        Args:
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
        """
        self.r_var.set(max(0, min(255, r)))
        self.g_var.set(max(0, min(255, g)))
        self.b_var.set(max(0, min(255, b)))
        self._on_color_change()
