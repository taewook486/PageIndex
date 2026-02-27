"""
Progress Updater with throttling for UI updates.

This module provides throttled progress updates to avoid excessive
UI calls that could impact performance.

@MX:SPEC: SPEC-GUI-003 - REQ-2
"""

import time
from typing import Callable, Optional


class ProgressUpdater:
    """Throttled progress updater for UI updates.

    Ensures that progress updates don't happen too frequently to avoid
    performance degradation while still allowing significant changes
    to be reported immediately.

    @MX:NOTE: Throttling is essential to prevent UI freezing during
    rapid processing updates.
    """

    # Default minimum interval between updates (in milliseconds)
    DEFAULT_MIN_INTERVAL_MS = 100

    # Minimum progress change that bypasses throttling
    SIGNIFICANT_CHANGE_THRESHOLD = 5

    def __init__(
        self,
        callback: Callable[[int, str], None],
        min_interval_ms: int = DEFAULT_MIN_INTERVAL_MS
    ):
        """Initialize the progress updater.

        Args:
            callback: Function to call with (percentage, message).
            min_interval_ms: Minimum milliseconds between throttled updates.
        """
        self._callback = callback
        self._min_interval_s = min_interval_ms / 1000.0
        self._last_update_time: Optional[float] = None
        self._last_percentage: int = 0
        self._last_message: str = ""

    def update(self, percentage: int, message: str) -> bool:
        """Update progress with throttling.

        Updates are throttled to avoid excessive calls, but significant
        progress changes (>=5%) bypass throttling.

        Args:
            percentage: Progress percentage (0-100).
            message: Status message to display.

        Returns:
            True if the update was sent, False if throttled.
        """
        current_time = time.time()

        # Check for significant change (bypasses throttling)
        is_significant = abs(percentage - self._last_percentage) >= self.SIGNIFICANT_CHANGE_THRESHOLD

        # Check if enough time has passed
        can_update = (
            self._last_update_time is None or
            (current_time - self._last_update_time) >= self._min_interval_s
        )

        if is_significant or can_update:
            self._callback(percentage, message)
            self._last_update_time = current_time
            self._last_percentage = percentage
            self._last_message = message
            return True

        return False

    def force_update(self, percentage: int, message: str) -> None:
        """Force an update bypassing throttling.

        Use for important updates that must be shown immediately.

        Args:
            percentage: Progress percentage (0-100).
            message: Status message to display.
        """
        self._callback(percentage, message)
        self._last_update_time = time.time()
        self._last_percentage = percentage
        self._last_message = message

    def reset(self) -> None:
        """Reset the throttling state for a new processing run."""
        self._last_update_time = None
        self._last_percentage = 0
        self._last_message = ""
