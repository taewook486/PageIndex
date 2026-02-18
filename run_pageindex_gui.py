#!/usr/bin/env python
"""
PageIndex GUI Entry Point.

This script launches the PageIndex graphical user interface.
Use this script to start the GUI application instead of the CLI.

Usage:
    python run_pageindex_gui.py
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from pageindex.gui.main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication closed by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting GUI: {e}")
        sys.exit(1)
