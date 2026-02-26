"""
Unit tests for HistoryManager.

Tests M6: Recent Files Management functionality.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from pageindex.gui.managers.history_manager import HistoryManager, HistoryEntry


@pytest.fixture
def temp_history_file():
    """Create a temporary history file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = Path(f.name)
    yield temp_path
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def history_manager(temp_history_file):
    """Create a HistoryManager with a temporary file."""
    with patch.object(HistoryManager, 'HISTORY_FILE', temp_history_file):
        manager = HistoryManager()
        yield manager


class TestHistoryEntry:
    """Test HistoryEntry dataclass."""

    def test_create_entry(self):
        """Test creating a HistoryEntry."""
        entry = HistoryEntry(
            path="/path/to/file.pdf",
            timestamp="2026-02-26T10:30:00",
            status="success",
            processing_time=45.2,
            file_type="pdf"
        )

        assert entry.path == "/path/to/file.pdf"
        assert entry.timestamp == "2026-02-26T10:30:00"
        assert entry.status == "success"
        assert entry.processing_time == 45.2
        assert entry.file_type == "pdf"

    def test_to_dict(self):
        """Test converting entry to dictionary."""
        entry = HistoryEntry(
            path="/path/to/file.pdf",
            timestamp="2026-02-26T10:30:00",
            status="success",
            processing_time=45.2,
            file_type="pdf"
        )

        data = entry.to_dict()

        assert data["path"] == "/path/to/file.pdf"
        assert data["timestamp"] == "2026-02-26T10:30:00"
        assert data["status"] == "success"
        assert data["processing_time"] == 45.2
        assert data["file_type"] == "pdf"

    def test_from_dict(self):
        """Test creating entry from dictionary."""
        data = {
            "path": "/path/to/file.pdf",
            "timestamp": "2026-02-26T10:30:00",
            "status": "success",
            "processing_time": 45.2,
            "file_type": "pdf"
        }

        entry = HistoryEntry.from_dict(data)

        assert entry.path == "/path/to/file.pdf"
        assert entry.timestamp == "2026-02-26T10:30:00"
        assert entry.status == "success"
        assert entry.processing_time == 45.2
        assert entry.file_type == "pdf"


class TestHistoryManager:
    """Test HistoryManager class."""

    def test_init_empty(self, history_manager):
        """Test initialization with no existing history."""
        assert history_manager.is_empty()
        assert len(history_manager.get_recent_files()) == 0

    def test_add_entry(self, history_manager):
        """Test adding a history entry."""
        # Mock os.path.exists to return True
        with patch('os.path.exists', return_value=True):
            history_manager.add_entry(
                path="/path/to/file.pdf",
                status="success",
                processing_time=45.0,
                file_type="pdf"
            )

            recent = history_manager.get_recent_files()
            assert len(recent) == 1
            assert recent[0].path == "/path/to/file.pdf"

    def test_max_entries(self, history_manager):
        """Test that history respects max entries limit."""
        max_entries = history_manager.max_entries

        # Add more than max entries
        for i in range(max_entries + 5):
            history_manager.add_entry(
                path=f"/path/to/file{i}.pdf",
                status="success",
                file_type="pdf"
            )

        recent = history_manager.get_recent_files()
        assert len(recent) <= max_entries

    def test_fifo_order(self, history_manager):
        """Test FIFO ordering of entries."""
        # Mock os.path.exists to return True
        with patch('os.path.exists', return_value=True):
            # Add entries
            history_manager.add_entry(path="/file1.pdf", status="success", file_type="pdf")
            history_manager.add_entry(path="/file2.pdf", status="success", file_type="pdf")
            history_manager.add_entry(path="/file3.pdf", status="success", file_type="pdf")

            recent = history_manager.get_recent_files()
            assert recent[0].path == "/file3.pdf"  # Most recent first
            assert recent[1].path == "/file2.pdf"
            assert recent[2].path == "/file1.pdf"

    def test_duplicate_path_replaces(self, history_manager):
        """Test that adding same path replaces existing entry."""
        with patch('os.path.exists', return_value=True):
            history_manager.add_entry(path="/file.pdf", status="error", file_type="pdf")
            history_manager.add_entry(path="/file.pdf", status="success", file_type="pdf")

            recent = history_manager.get_recent_files()
            assert len(recent) == 1
            assert recent[0].status == "success"

    def test_clear_history(self, history_manager):
        """Test clearing history."""
        history_manager.add_entry(path="/file1.pdf", status="success", file_type="pdf")
        history_manager.add_entry(path="/file2.pdf", status="success", file_type="pdf")

        history_manager.clear_history()

        assert history_manager.is_empty()

    def test_persistence(self, history_manager, temp_history_file):
        """Test that history persists across manager instances."""
        with patch('os.path.exists', return_value=True):
            # Add entry
            history_manager.add_entry(path="/file.pdf", status="success", file_type="pdf")

        # Create new manager instance
        with patch.object(HistoryManager, 'HISTORY_FILE', temp_history_file):
            with patch('os.path.exists', return_value=True):
                new_manager = HistoryManager()

                recent = new_manager.get_recent_files()
                assert len(recent) == 1
                assert recent[0].path == "/file.pdf"

    def test_filter_nonexistent_files(self, history_manager):
        """Test that non-existent files are filtered out."""
        # First, we need to add entries directly to history since os.path.exists is checked during get_recent_files
        from pageindex.gui.managers.history_manager import HistoryEntry

        # Add entries directly to history
        history_manager._history = [
            HistoryEntry(
                path="/existent.pdf",
                timestamp="2026-02-26T10:30:00",
                status="success",
                processing_time=0,
                file_type="pdf"
            ),
            HistoryEntry(
                path="/nonexistent.pdf",
                timestamp="2026-02-26T10:31:00",
                status="success",
                processing_time=0,
                file_type="pdf"
            )
        ]

        # Mock exists check - return True only for /existent.pdf
        def mock_exists(path):
            return path == "/existent.pdf"

        with patch('os.path.exists', side_effect=mock_exists):
            recent = history_manager.get_recent_files()

        assert len(recent) == 1
        assert recent[0].path == "/existent.pdf"
