"""
Manager classes for PageIndex GUI.

This package provides manager classes for various GUI features.
"""

from .history_manager import HistoryManager, HistoryEntry
from .settings_manager import SettingsManager
from .batch_processor import BatchProcessor, BatchItem
from .export_manager import ExportManager

__all__ = [
    "HistoryManager",
    "HistoryEntry",
    "SettingsManager",
    "BatchProcessor",
    "BatchItem",
    "ExportManager",
]
