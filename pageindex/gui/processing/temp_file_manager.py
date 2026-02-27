"""
Temporary File Manager for data integrity.

This module manages temporary files during processing to ensure
data integrity on cancellation.

@MX:SPEC: SPEC-GUI-003 - REQ-3
"""

import contextlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Optional


class TempFileManager:
    """Manage temporary files for safe processing.

    Ensures that incomplete output files are cleaned up on cancellation
    and that file writes are atomic to prevent corruption.

    @MX:NOTE: Uses temp files to ensure output files are never
    left in a partially-written state.
    """

    def __init__(self, temp_dir: Optional[str] = None):
        """Initialize the temp file manager.

        Args:
            temp_dir: Directory for temp files. If None, uses system temp.
        """
        self._temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir())
        self._temp_files: list[Path] = []

    def create_temp_file(self, name: str, suffix: Optional[str] = None) -> str:
        """Create a temporary file for output.

        Args:
            name: Base name for the temp file.
            suffix: File suffix (e.g., '.json'). If None, extracted from name.

        Returns:
            Path to the created temp file.
        """
        if suffix is None:
            suffix = ''.join(Path(name).suffixes) or '.tmp'

        # Create unique temp file
        fd, temp_str = tempfile.mkstemp(
            suffix=suffix,
            prefix=f"pageindex_{Path(name).stem}_",
            dir=str(self._temp_dir)
        )
        os.close(fd)

        temp_path: Path = Path(temp_str)
        self._temp_files.append(temp_path)

        return str(temp_path)

    def commit(self, temp_path: str, final_path: str) -> None:
        """Move temp file to final destination.

        Args:
            temp_path: Path to the temp file.
            final_path: Final destination path.
        """
        temp = Path(temp_path)
        final = Path(final_path)

        # Ensure parent directory exists
        final.parent.mkdir(parents=True, exist_ok=True)

        # Move temp to final location
        shutil.move(str(temp), str(final))

        # Remove from tracking
        if temp in self._temp_files:
            self._temp_files.remove(temp)

    def cleanup_on_cancel(self) -> None:
        """Clean up all temporary files on cancellation.

        Removes all tracked temp files that were not committed.
        """
        for temp_path in self._temp_files[:]:
            try:
                if temp_path.exists():
                    temp_path.unlink()
            except OSError:
                pass  # Ignore cleanup errors

        self._temp_files.clear()

    def cleanup(self) -> None:
        """Clean up all temporary files.

        Alias for cleanup_on_cancel for clarity.
        """
        self.cleanup_on_cancel()

    def __enter__(self) -> 'TempFileManager':
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager and clean up."""
        # Only cleanup if there was an exception (cancellation)
        # or if files weren't committed
        if exc_type is not None:
            self.cleanup_on_cancel()
        else:
            # Clean up any remaining uncommitted files
            self.cleanup_on_cancel()


def atomic_write_json(path: str, data: dict[str, Any]) -> None:
    """Write JSON data atomically.

    Writes to a temp file first, then moves to final location
    to ensure atomicity.

    @MX:ANCHOR: Critical for data integrity during cancellation
    @MX:REASON: This function is called from multiple processing
                paths when saving results, making it a high fan_in
                component that must be stable.

    Args:
        path: Final destination path for the JSON file.
        data: Dictionary to write as JSON.
    """
    path_obj = Path(path)
    temp_path: Optional[Path] = None

    try:
        # Create temp file in same directory for atomic move
        fd, temp_str = tempfile.mkstemp(
            suffix='.json',
            prefix=f"{path_obj.stem}_",
            dir=str(path_obj.parent) if path_obj.parent.exists() else None
        )
        temp_path = Path(temp_str)

        # Write data to temp file
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Atomic move to final location
        shutil.move(str(temp_path), str(path_obj))

    except Exception:
        # Clean up temp file on failure
        if temp_path and temp_path.exists():
            with contextlib.suppress(OSError):
                temp_path.unlink()
        raise
