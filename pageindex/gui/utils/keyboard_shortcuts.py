"""
Keyboard Shortcuts Manager for PageIndex GUI.

This module provides functionality to manage keyboard shortcuts.
Implements keyboard shortcuts for M9 (Additional UX Enhancements).
"""

from typing import Callable, Dict, Optional

import customtkinter as ctk


class KeyboardShortcuts:
    """Manages keyboard shortcuts for the application."""

    # Default shortcuts mapping
    DEFAULT_SHORTCUTS = {
        "Ctrl+o": "open_file",
        "Ctrl+O": "open_file",
        "Ctrl+s": "save_result",
        "Ctrl+S": "save_result",
        "Ctrl+,": "open_settings",
        "F1": "show_help",
        "Escape": "close_dialog",
        "Ctrl+q": "quit",
        "Ctrl+Q": "quit",
    }

    def __init__(self, root: ctk.CTk):
        """Initialize keyboard shortcuts manager.

        Args:
            root: Root window to bind shortcuts to
        """
        self.root = root
        self.handlers: Dict[str, Callable[[], None]] = {}
        self._bind_default_shortcuts()

    def _bind_default_shortcuts(self) -> None:
        """Bind default keyboard shortcuts."""
        # Note: Actual handlers will be registered by the application
        # This just sets up the structure
        pass

    def register_handler(self, shortcut: str, handler: Callable[[], None]) -> None:
        """Register a handler for a keyboard shortcut.

        Args:
            shortcut: Keyboard shortcut (e.g., "Ctrl+o", "F1")
            handler: Function to call when shortcut is pressed
        """
        self.handlers[shortcut] = handler

        # Bind the shortcut
        self._parse_and_bind(shortcut, handler)

    def _parse_and_bind(self, shortcut: str, handler: Callable[[], None]) -> None:
        """Parse shortcut and bind to root.

        Args:
            shortcut: Keyboard shortcut string
            handler: Handler function
        """
        # Parse shortcut
        parts = shortcut.lower().split("+")

        # Handle function keys
        if shortcut.startswith("F") and shortcut[1:].isdigit():
            key = shortcut.lower()
            self.root.bind(f"<{key}>", lambda e: handler())
            return

        # Handle modifiers + key combinations
        modifiers = []
        key = None

        for part in parts:
            if part in ["ctrl", "control"]:
                modifiers.append("control")
            elif part == "shift":
                modifiers.append("shift")
            elif part == "alt":
                modifiers.append("alt")
            else:
                key = part

        if not key:
            return

        # Build binding string
        if modifiers:
            modifier_str = "-".join(modifiers)
            # Bind both lowercase and uppercase versions
            self.root.bind(f"<{modifier_str}-{key}>", lambda e: handler())
            self.root.bind(f"<{modifier_str}-{key.upper()}>", lambda e: handler())
        else:
            self.root.bind(f"<{key}>", lambda e: handler())

    def get_shortcut_display(self, shortcut: str) -> str:
        """Get human-readable display string for a shortcut.

        Args:
            shortcut: Internal shortcut string

        Returns:
            Display string (e.g., "Ctrl+O")
        """
        # Capitalize first letter of each part
        parts = shortcut.split("+")
        parts = [p.upper() if len(p) == 1 else p.capitalize() for p in parts]
        return "+".join(parts)

    def unregister_handler(self, shortcut: str) -> None:
        """Unregister a keyboard shortcut handler.

        Args:
            shortcut: Keyboard shortcut to unregister
        """
        if shortcut in self.handlers:
            del self.handlers[shortcut]

        # Unbind the shortcut
        self._parse_and_unbind(shortcut)

    def _parse_and_unbind(self, shortcut: str) -> None:
        """Parse shortcut and unbind from root.

        Args:
            shortcut: Keyboard shortcut string
        """
        # Parse shortcut
        parts = shortcut.lower().split("+")

        # Handle function keys
        if shortcut.startswith("F") and shortcut[1:].isdigit():
            key = shortcut.lower()
            self.root.unbind(f"<{key}>")
            return

        # Handle modifiers + key combinations
        modifiers = []
        key = None

        for part in parts:
            if part in ["ctrl", "control"]:
                modifiers.append("control")
            elif part == "shift":
                modifiers.append("shift")
            elif part == "alt":
                modifiers.append("alt")
            else:
                key = part

        if not key:
            return

        # Build binding string and unbind
        if modifiers:
            modifier_str = "-".join(modifiers)
            self.root.unbind(f"<{modifier_str}-{key}>")
            self.root.unbind(f"<{modifier_str}-{key.upper()}>")
        else:
            self.root.unbind(f"<{key}>")
