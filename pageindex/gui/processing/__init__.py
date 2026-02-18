"""
Processing package for PageIndex GUI.

This package handles background processing of files.
"""

from .processor import (
    ProcessingCallbacks,
    BackgroundProcessor,
    save_result_to_file
)

__all__ = [
    "ProcessingCallbacks",
    "BackgroundProcessor",
    "save_result_to_file"
]
