"""
History Manager for PageIndex GUI.

This module provides functionality to track and manage recently processed files.
Implements M6 of SPEC-GUI-002.
"""

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class HistoryEntry:
    """Represents a single entry in the recent files history.

    Attributes:
        path: File path
        timestamp: ISO format timestamp of processing
        status: Processing status ('success' or 'error')
        processing_time: Time taken to process in seconds
        file_type: Type of file ('pdf' or 'markdown')
    """

    path: str
    timestamp: str
    status: str
    processing_time: float
    file_type: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the entry
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "HistoryEntry":
        """Create HistoryEntry from dictionary.

        Args:
            data: Dictionary containing entry data

        Returns:
            HistoryEntry instance
        """
        return cls(**data)


class HistoryManager:
    """Manages recent files history for PageIndex GUI.

    Implements FIFO queue with maximum 10 entries.
    Stores history in ~/.pageIndex/history.json
    """

    MAX_ENTRIES = 10
    HISTORY_FILE = Path.home() / ".pageIndex" / "history.json"

    def __init__(self, max_entries: int = MAX_ENTRIES):
        """Initialize the history manager.

        Args:
            max_entries: Maximum number of entries to keep (default: 10)
        """
        self.max_entries = max_entries
        self._history: List[HistoryEntry] = []
        self._load_history()

    def add_entry(
        self,
        path: str,
        status: str = "success",
        processing_time: float = 0.0,
        file_type: str = "pdf"
    ) -> None:
        """Add a new entry to the history.

        Args:
            path: File path that was processed
            status: Processing status ('success' or 'error')
            processing_time: Time taken in seconds
            file_type: Type of file ('pdf' or 'markdown')
        """
        # Remove existing entry with same path (if any)
        self._history = [e for e in self._history if e.path != path]

        # Create new entry
        entry = HistoryEntry(
            path=path,
            timestamp=datetime.now().isoformat(),
            status=status,
            processing_time=processing_time,
            file_type=file_type
        )

        # Add to beginning of list
        self._history.insert(0, entry)

        # Trim to max entries
        if len(self._history) > self.max_entries:
            self._history = self._history[:self.max_entries]

        # Save to disk
        self._save_history()

    def get_recent_files(self) -> List[HistoryEntry]:
        """Get list of recent files, filtering out non-existent files.

        Returns:
            List of HistoryEntry objects for existing files
        """
        # Filter out non-existent files
        existing_files = []
        for entry in self._history:
            if os.path.exists(entry.path):
                existing_files.append(entry)
            else:
                # Remove non-existent entries from history
                self._history.remove(entry)

        # Save if we removed any entries
        if len(existing_files) != len(self._history):
            self._save_history()

        return existing_files

    def clear_history(self) -> None:
        """Clear all history entries."""
        self._history.clear()
        self._save_history()

    def is_empty(self) -> bool:
        """Check if history is empty.

        Returns:
            True if no recent files exist
        """
        return len(self.get_recent_files()) == 0

    def _load_history(self) -> None:
        """Load history from disk."""
        if not self.HISTORY_FILE.exists():
            return

        try:
            with open(self.HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Parse entries
            history_data = data.get('recent_files', [])
            self._history = [
                HistoryEntry.from_dict(entry) for entry in history_data
            ]
        except (json.JSONDecodeError, KeyError, TypeError):
            # Corrupted file, start fresh
            self._history = []

    def _save_history(self) -> None:
        """Save history to disk."""
        # Ensure directory exists
        self.HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Prepare data
        data = {
            'recent_files': [entry.to_dict() for entry in self._history]
        }

        # Write to file
        with open(self.HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
