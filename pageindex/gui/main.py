"""
PageIndex GUI Main Entry Point.

This module provides the main entry point for launching the PageIndex GUI application.
"""

import sys
import customtkinter as ctk
from .main_window import PageIndexMainWindow


def main():
    """Launch the PageIndex GUI application."""
    # Set appearance mode and default color theme
    ctk.set_appearance_mode("dark")  # Modes: system, dark, light
    ctk.set_default_color_theme("blue")  # Themes: blue, dark-blue, green

    # Create the main application window
    app = PageIndexMainWindow()

    # Start the application main loop
    app.mainloop()


if __name__ == "__main__":
    main()
