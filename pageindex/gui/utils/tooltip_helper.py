"""
Tooltip Helper for PageIndex GUI.

This module provides functionality to add tooltips to widgets.
Implements tooltips for M9 (Additional UX Enhancements).
"""

import time
from typing import Optional

import customtkinter as ctk


class TooltipHelper:
    """Helper class for creating and managing tooltips."""

    def __init__(
        self,
        widget: ctk.CTk,
        text: str,
        delay: float = 0.5,
        bg_color: str = "#FFFFE0",
        fg_color: str = "black",
        font: Optional[tuple] = None
    ):
        """Initialize a tooltip for a widget.

        Args:
            widget: Widget to attach tooltip to
            text: Tooltip text to display
            delay: Delay in seconds before showing tooltip
            bg_color: Background color of tooltip
            fg_color: Foreground (text) color of tooltip
            font: Font tuple for tooltip text
        """
        self.widget = widget
        self.text = text
        self.delay = delay
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.font = font or ("Arial", 10)

        self.tooltip_window: Optional[ctk.CTkToplevel] = None
        self.after_id: Optional[str] = None

        # Bind events
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
        self.widget.bind("<Motion>", self._on_motion)

    def _on_enter(self, event=None) -> None:
        """Handle mouse enter event."""
        self.schedule_show()

    def _on_leave(self, event=None) -> None:
        """Handle mouse leave event."""
        self.hide()
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None

    def _on_motion(self, event=None) -> None:
        """Handle mouse motion event."""
        # Reset timer when mouse moves
        if self.after_id:
            self.widget.after_cancel(self.after_id)
        self.schedule_show()

    def schedule_show(self) -> None:
        """Schedule the tooltip to be shown after delay."""
        self.after_id = self.widget.after(int(self.delay * 1000), self.show)

    def show(self) -> None:
        """Show the tooltip window."""
        if self.tooltip_window or not self.widget.winfo_exists():
            return

        # Get widget position
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25

        # Create tooltip window
        self.tooltip_window = ctk.CTkToplevel(self.widget)

        # Configure window
        self.tooltip_window.wm_overrideredirect(True)  # Remove window decorations
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        self.tooltip_window.configure(fg_color=self.bg_color)

        # Create tooltip label
        label = ctk.CTkLabel(
            self.tooltip_window,
            text=self.text,
            fg_color=self.bg_color,
            text_color=self.fg_color,
            font=self.font,
            anchor="w",
            justify="left",
            padx=5,
            pady=3
        )
        label.pack()

        # Keep tooltip on top
        self.tooltip_window.lift()

    def hide(self) -> None:
        """Hide the tooltip window."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


def add_tooltip(
    widget: ctk.CTk,
    text: str,
    delay: float = 0.5,
    bg_color: str = "#FFFFE0",
    fg_color: str = "black"
) -> TooltipHelper:
    """Add a tooltip to a widget.

    Args:
        widget: Widget to attach tooltip to
        text: Tooltip text to display
        delay: Delay in seconds before showing tooltip
        bg_color: Background color of tooltip
        fg_color: Foreground (text) color of tooltip

    Returns:
        TooltipHelper instance
    """
    return TooltipHelper(widget, text, delay, bg_color, fg_color)
