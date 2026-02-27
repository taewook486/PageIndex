"""
Processing package for PageIndex GUI.

This package handles background processing of files with support for
progress tracking, cancellation, and data integrity.
"""

from .processor import BackgroundProcessor, ProcessingCallbacks, save_result_to_file
from .progress_calculator import ProgressCalculator
from .progress_updater import ProgressUpdater
from .status_formatter import StatusMessageFormatter
from .stop_event_checker import CancellationException, StopEventChecker
from .temp_file_manager import TempFileManager, atomic_write_json

__all__ = [
    # Original exports
    "ProcessingCallbacks",
    "BackgroundProcessor",
    "save_result_to_file",
    # New exports for SPEC-GUI-003
    "StopEventChecker",
    "CancellationException",
    "ProgressCalculator",
    "ProgressUpdater",
    "TempFileManager",
    "atomic_write_json",
    "StatusMessageFormatter",
]
