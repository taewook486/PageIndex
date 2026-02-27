"""
Stop Event Checker for cancellation support.

This module provides a standardized way to check for stop events
across both synchronous and asynchronous processing paths.

@MX:SPEC: SPEC-GUI-003 - REQ-1, REQ-5
"""

import threading
from typing import Optional


class CancellationException(Exception):
    """Exception raised when processing is cancelled.

    @MX:NOTE: This exception signals that processing was intentionally
    cancelled by user request, not due to an error.
    """
    pass


class StopEventChecker:
    """Utility class for checking stop events during processing.

    Provides both synchronous and asynchronous methods for checking
    cancellation state, enabling consistent cancellation behavior
    across PDF (sync) and Markdown (async) processing paths.

    @MX:ANCHOR: Core cancellation mechanism used across all processors
    @MX:REASON: This class is called from multiple processing paths
                (PDF sync, Markdown async, AI inference) making it
                a high fan_in component requiring stable interface.
    """

    def __init__(self, stop_event: Optional[threading.Event] = None):
        """Initialize the stop event checker.

        Args:
            stop_event: Threading event to check for stop signals.
                       If None, creates a new event.
        """
        self._stop_event = stop_event or threading.Event()

    @property
    def stop_event(self) -> threading.Event:
        """Get the underlying stop event."""
        return self._stop_event

    def is_stopped(self) -> bool:
        """Check if processing should stop.

        Returns:
            True if cancellation has been requested, False otherwise.
        """
        return self._stop_event.is_set()

    def check_if_stopped(self) -> None:
        """Check if stopped and raise CancellationException if so.

        Raises:
            CancellationException: If cancellation has been requested.
        """
        if self._stop_event.is_set():
            raise CancellationException("Processing cancelled by user")

    async def check_if_stopped_async(self) -> None:
        """Async version of check_if_stopped.

        This method provides the same functionality as check_if_stopped
        but can be used in async contexts without blocking.

        Raises:
            CancellationException: If cancellation has been requested.
        """
        if self._stop_event.is_set():
            raise CancellationException("Processing cancelled by user")

    def set_stopped(self) -> None:
        """Signal that processing should stop."""
        self._stop_event.set()

    def reset(self) -> None:
        """Reset the stop event for a new processing run."""
        self._stop_event.clear()
