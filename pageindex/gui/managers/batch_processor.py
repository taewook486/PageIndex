"""
Batch Processor for PageIndex GUI.

This module provides functionality to process multiple files in batch mode.
Implements M9.2 of SPEC-GUI-002.
"""

import os
import queue
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Callable, Optional, Dict, Any


@dataclass
class BatchItem:
    """Represents a single item in the batch queue.

    Attributes:
        file_path: Path to the file to process
        file_type: Type of file ('pdf' or 'markdown')
        config: Configuration for processing
        status: Current status ('pending', 'processing', 'completed', 'error')
        result: Processing result (if completed)
        error: Error message (if failed)
    """
    file_path: str
    file_type: str
    config: Dict[str, Any]
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None

    @property
    def processing_time(self) -> float:
        """Get processing time in seconds.

        Returns:
            Processing time or 0 if not completed
        """
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        return 0.0


class BatchProcessor:
    """Manages batch processing of multiple files.

    Processes files sequentially from a queue, tracking results
    and providing progress updates.
    """

    def __init__(
        self,
        on_progress: Optional[Callable[[int, int, str], None]] = None,
        on_item_complete: Optional[Callable[[BatchItem], None]] = None,
        on_batch_complete: Optional[Callable[[List[BatchItem]], None]] = None
    ):
        """Initialize the batch processor.

        Args:
            on_progress: Callback(current, total, status) for progress updates
            on_item_complete: Callback(BatchItem) when each item completes
            on_batch_complete: Callback(List[BatchItem]) when all items complete
        """
        self.queue: queue.Queue[BatchItem] = queue.Queue()
        self.results: List[BatchItem] = []
        self.is_processing = False
        self.should_stop = False
        self.processing_thread: Optional[threading.Thread] = None

        self.on_progress = on_progress
        self.on_item_complete = on_item_complete
        self.on_batch_complete = on_batch_complete

    def add_file(self, file_path: str, file_type: str, config: Dict[str, Any]) -> None:
        """Add a file to the batch queue.

        Args:
            file_path: Path to the file
            file_type: Type of file ('pdf' or 'markdown')
            config: Configuration for processing
        """
        item = BatchItem(
            file_path=file_path,
            file_type=file_type,
            config=config
        )
        self.queue.put(item)

    def get_queue_size(self) -> int:
        """Get the current queue size.

        Returns:
            Number of items in queue
        """
        return self.queue.qsize()

    def get_results(self) -> List[BatchItem]:
        """Get all completed results.

        Returns:
            List of BatchItem objects
        """
        return self.results.copy()

    def clear_queue(self) -> None:
        """Clear all pending items from the queue."""
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except queue.Empty:
                break

    def clear_results(self) -> None:
        """Clear all results."""
        self.results.clear()

    def remove_item(self, file_path: str) -> bool:
        """Remove an item from the queue by file path.

        Args:
            file_path: Path of the file to remove

        Returns:
            True if item was found and removed
        """
        # Create a temporary queue
        temp_queue = queue.Queue()
        found = False

        while not self.queue.empty():
            try:
                item = self.queue.get_nowait()
                if item.file_path == file_path:
                    found = True
                else:
                    temp_queue.put(item)
            except queue.Empty:
                break

        # Put remaining items back
        while not temp_queue.empty():
            try:
                self.queue.put(temp_queue.get_nowait())
            except queue.Empty:
                break

        return found

    def start_processing(self) -> bool:
        """Start batch processing.

        Returns:
            True if processing started successfully
        """
        if self.is_processing:
            return False

        if self.queue.empty():
            return False

        self.is_processing = True
        self.should_stop = False
        self.results.clear()

        # Start processing thread
        self.processing_thread = threading.Thread(
            target=self._process_queue,
            daemon=True
        )
        self.processing_thread.start()

        return True

    def stop_processing(self) -> None:
        """Stop batch processing."""
        self.should_stop = True

    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """Wait for processing to complete.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if completed within timeout
        """
        if self.processing_thread:
            self.processing_thread.join(timeout=timeout)
            return not self.processing_thread.is_alive()
        return True

    def _process_queue(self) -> None:
        """Process all items in the queue (runs in separate thread)."""
        total_items = self.queue.qsize()
        completed = 0

        while not self.queue.empty() and not self.should_stop:
            try:
                # Get next item
                item = self.queue.get(timeout=0.1)
                completed += 1

                # Update progress
                if self.on_progress:
                    status = f"Processing {os.path.basename(item.file_path)}..."
                    self.on_progress(completed, total_items, status)

                # Process the item
                self._process_item(item)

                # Add to results
                self.results.append(item)

                # Notify completion
                if self.on_item_complete:
                    self.on_item_complete(item)

            except queue.Empty:
                continue
            except Exception as e:
                # Log error and continue
                if self.on_progress:
                    self.on_progress(completed, total_items, f"Error: {str(e)}")

        # Batch complete
        self.is_processing = False

        if self.on_batch_complete and not self.should_stop:
            self.on_batch_complete(self.results)

    def _process_item(self, item: BatchItem) -> None:
        """Process a single batch item.

        Args:
            item: BatchItem to process
        """
        item.status = "processing"
        item.start_time = time.time()

        try:
            # Import here to avoid circular imports
            from pageindex.gui.processing import process_file

            # Process the file
            result = process_file(
                item.file_path,
                item.file_type,
                item.config
            )

            item.status = "completed"
            item.result = result

        except Exception as e:
            item.status = "error"
            item.error = str(e)

        finally:
            item.end_time = time.time()

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of batch processing.

        Returns:
            Dictionary with summary statistics
        """
        total = len(self.results)
        success = sum(1 for r in self.results if r.status == "completed")
        error = sum(1 for r in self.results if r.status == "error")
        total_time = sum(r.processing_time for r in self.results)

        return {
            "total": total,
            "success": success,
            "error": error,
            "total_time": total_time,
            "avg_time": total_time / total if total > 0 else 0
        }
