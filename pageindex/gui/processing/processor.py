"""
Background Processing Module for PageIndex GUI.

This module handles file processing in background threads to keep
the GUI responsive during long-running operations.

@MX:SPEC: SPEC-GUI-003 - Enhanced with cancellation, progress tracking, and data integrity
"""

import asyncio
import os
import threading
from pathlib import Path
from typing import Any, Callable, Optional

from .progress_calculator import ProgressCalculator
from .progress_updater import ProgressUpdater
from .status_formatter import StatusMessageFormatter

# Import new utilities for SPEC-GUI-003
from .stop_event_checker import CancellationException, StopEventChecker
from .temp_file_manager import TempFileManager, atomic_write_json


class ProcessingCallbacks:
    """Callback functions for processing updates."""

    def __init__(
        self,
        on_progress: Callable[[int, str], None],
        on_complete: Callable[[dict[str, Any]], None],
        on_error: Callable[[str], None]
    ):
        """Initialize callbacks.

        Args:
            on_progress: Called with (percentage, status_message)
            on_complete: Called with result dictionary
            on_error: Called with error message
        """
        self.on_progress = on_progress
        self.on_complete = on_complete
        self.on_error = on_error


class BackgroundProcessor(threading.Thread):
    """Process files in background thread with event loop.

    @MX:NOTE: Enhanced with cancellation support, progress tracking,
    and data integrity features per SPEC-GUI-003.
    """

    def __init__(
        self,
        file_path: str,
        file_type: str,
        config: dict[str, Any],
        callbacks: ProcessingCallbacks
    ):
        """Initialize background processor.

        Args:
            file_path: Path to file to process
            file_type: Type of file ('pdf' or 'markdown')
            config: Configuration dictionary
            callbacks: Callback functions for updates
        """
        super().__init__(daemon=True)
        self.file_path = file_path
        self.file_type = file_type
        self.config = config
        self.callbacks = callbacks
        self._stop_event = threading.Event()

        # Initialize new utilities for SPEC-GUI-003
        self._stop_checker = StopEventChecker(self._stop_event)
        self._progress_calculator = ProgressCalculator()
        self._progress_updater = ProgressUpdater(
            callbacks.on_progress,
            min_interval_ms=100
        )
        self._status_formatter = StatusMessageFormatter()
        self._temp_manager: Optional[TempFileManager] = None

    def run(self):
        """Run the processing in background thread."""
        try:
            # Initialize temp file manager for this run
            self._temp_manager = TempFileManager()

            # Check if processing is synchronous or async
            if self.file_type == 'pdf':
                # PDF processing is synchronous (uses asyncio.run() internally)
                result = self._process_pdf_sync()
            else:
                # Markdown processing is async
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(self._process_file())
                finally:
                    loop.close()

            # Notify completion
            self.callbacks.on_complete(result)

        except CancellationException:
            # Handle cancellation gracefully
            self._handle_cancellation()
        except Exception as e:
            # Notify error with full traceback for debugging
            import traceback
            error_details = f"{str(e)}\n\n{traceback.format_exc()}"
            self.callbacks.on_error(error_details)
        finally:
            # Clean up temp files if not committed
            if self._temp_manager:
                self._temp_manager.cleanup_on_cancel()

    def stop(self):
        """Stop the processing.

        @MX:NOTE: Sets the stop event which will be checked during processing.
        """
        self._stop_event.set()

    def _handle_cancellation(self):
        """Handle graceful cancellation.

        @MX:NOTE: Cleans up temp files and notifies UI of cancellation.
        """
        # Clean up any temp files
        if self._temp_manager:
            self._temp_manager.cleanup_on_cancel()

        # Notify with cancellation message
        cancel_msg = self._status_formatter.format_cancelled()
        self._progress_updater.force_update(0, cancel_msg)

        # Call error callback with cancellation info
        self.callbacks.on_error("Processing cancelled by user")

    def _check_stopped(self):
        """Check if processing should stop.

        @MX:NOTE: Raises CancellationException if stop requested.
        """
        self._stop_checker.check_if_stopped()

    async def _check_stopped_async(self):
        """Async version of _check_stopped."""
        await self._stop_checker.check_if_stopped_async()

    def _update_progress(self, percentage: int, message: str):
        """Update progress with throttling."""
        self._progress_updater.update(percentage, message)

    def _force_progress_update(self, percentage: int, message: str):
        """Force progress update bypassing throttling."""
        self._progress_updater.force_update(percentage, message)

    def _process_pdf_sync(self) -> dict[str, Any]:
        """Process PDF file synchronously.

        PDF processing uses asyncio.run() internally, so we can't
        call it from within an event loop. This method handles it
        synchronously.

        @MX:NOTE: Enhanced with cancellation checkpoints and progress tracking.

        Returns:
            Dictionary with processing results
        """
        from pageindex.page_index import page_index_main
        from pageindex.utils import ConfigLoader

        # Check for cancellation at start
        self._check_stopped()

        # Load configuration
        loader = ConfigLoader()
        user_config = {
            'model': self.config.get('model', 'glm-5'),
            'toc_check_page_num': self.config.get('toc_check_pages', 20),
            'max_page_num_each_node': self.config.get('max_pages', 10),
            'max_token_num_each_node': self.config.get('max_tokens', 20000),
            'if_add_node_id': 'yes' if self.config.get('add_node_id', True) else 'no',
            'if_add_node_summary': 'yes' if self.config.get('add_node_summary', True) else 'no',
            'if_add_doc_description': 'yes' if self.config.get('add_doc_description', False) else 'no',
            'if_add_node_text': 'yes' if self.config.get('add_node_text', False) else 'no',
        }

        # Add base_url if provided
        if self.config.get('base_url'):
            os.environ['OPENAI_BASE_URL'] = self.config['base_url']

        opt = loader.load(user_config)

        # Update progress - Loading stage (0-10%)
        progress = self._progress_calculator.calculate_pdf_progress("loading", 0, 1)
        msg = self._status_formatter.format_pdf_status("loading")
        self._force_progress_update(progress, msg)

        # Check for cancellation before main processing
        self._check_stopped()

        # Update progress - Starting extraction (10-20%)
        progress = self._progress_calculator.calculate_pdf_progress("page_processing", 0, 1)
        msg = self._status_formatter.format_pdf_status("page_processing", current=0, total=1)
        self._update_progress(progress, msg)

        # Process the PDF (synchronous - uses asyncio.run() internally)
        # Note: The actual PDF processing happens inside page_index_main
        # which doesn't support interruption. We can only check before/after.
        result = page_index_main(self.file_path, opt)

        # Check for cancellation after processing
        self._check_stopped()

        # Update progress - Complete
        progress = self._progress_calculator.calculate_pdf_progress("ai_inference", 1, 1)
        msg = self._status_formatter.format_complete()
        self._force_progress_update(progress, msg)

        return {
            'success': True,
            'file_type': 'pdf',
            'file_path': self.file_path,
            'result': result,
            'output_file': self._get_output_path(self.file_path)
        }

    async def _process_file(self) -> dict[str, Any]:
        """Process the file asynchronously.

        @MX:NOTE: Enhanced with cancellation support.

        Returns:
            Dictionary with processing results
        """
        # Check for cancellation at start
        await self._check_stopped_async()

        # Notify start
        msg = self._status_formatter.format_status("loading")
        self._force_progress_update(0, msg)

        if self.file_type == 'pdf':
            return await self._process_pdf()
        elif self.file_type == 'markdown':
            return await self._process_markdown()
        else:
            raise ValueError(f"Unsupported file type: {self.file_type}")

    async def _process_pdf(self) -> dict[str, Any]:
        """Process PDF file.

        @MX:NOTE: Enhanced with cancellation checkpoints.

        Returns:
            Dictionary with processing results
        """
        from pageindex.page_index import page_index_main
        from pageindex.utils import ConfigLoader

        # Check for cancellation
        await self._check_stopped_async()

        # Load configuration
        loader = ConfigLoader()
        user_config = {
            'model': self.config.get('model', 'glm-5'),
            'toc_check_page_num': self.config.get('toc_check_pages', 20),
            'max_page_num_each_node': self.config.get('max_pages', 10),
            'max_token_num_each_node': self.config.get('max_tokens', 20000),
            'if_add_node_id': 'yes' if self.config.get('add_node_id', True) else 'no',
            'if_add_node_summary': 'yes' if self.config.get('add_node_summary', True) else 'no',
            'if_add_doc_description': 'yes' if self.config.get('add_doc_description', False) else 'no',
            'if_add_node_text': 'yes' if self.config.get('add_node_text', False) else 'no',
        }

        # Add base_url if provided
        if self.config.get('base_url'):
            os.environ['OPENAI_BASE_URL'] = self.config['base_url']

        opt = loader.load(user_config)

        # Update progress - Loading stage
        progress = self._progress_calculator.calculate_pdf_progress("loading", 0, 1)
        msg = self._status_formatter.format_pdf_status("loading")
        self._force_progress_update(progress, msg)

        # Check for cancellation
        await self._check_stopped_async()

        # Update progress - Starting extraction
        progress = self._progress_calculator.calculate_pdf_progress("page_processing", 0, 1)
        msg = self._status_formatter.format_pdf_status("page_processing", current=0, total=1)
        self._update_progress(progress, msg)

        # Process the PDF
        result = page_index_main(self.file_path, opt)

        # Check for cancellation
        await self._check_stopped_async()

        # Update progress - Complete
        progress = self._progress_calculator.calculate_pdf_progress("ai_inference", 1, 1)
        msg = self._status_formatter.format_complete()
        self._force_progress_update(progress, msg)

        return {
            'success': True,
            'file_type': 'pdf',
            'file_path': self.file_path,
            'result': result,
            'output_file': self._get_output_path(self.file_path)
        }

    async def _process_markdown(self) -> dict[str, Any]:
        """Process Markdown file.

        @MX:NOTE: Enhanced with cancellation checkpoints and progress tracking.

        Returns:
            Dictionary with processing results
        """
        from pageindex.page_index_md import md_to_tree
        from pageindex.utils import ConfigLoader

        # Check for cancellation at start
        await self._check_stopped_async()

        # Load configuration
        loader = ConfigLoader()
        user_config = {
            'model': self.config.get('model', 'glm-5'),
            'if_add_node_id': 'yes' if self.config.get('add_node_id', True) else 'no',
            'if_add_node_summary': 'yes' if self.config.get('add_node_summary', True) else 'no',
            'if_add_doc_description': 'yes' if self.config.get('add_doc_description', False) else 'no',
            'if_add_node_text': 'yes' if self.config.get('add_node_text', False) else 'no',
        }

        # Add base_url if provided
        if self.config.get('base_url'):
            os.environ['OPENAI_BASE_URL'] = self.config['base_url']

        opt = loader.load(user_config)

        # Update progress - Parsing stage (0-30%)
        progress = self._progress_calculator.calculate_markdown_progress("parsing", 0, 1)
        msg = self._status_formatter.format_markdown_status("parsing", progress_percent=0)
        self._force_progress_update(progress, msg)

        # Check for cancellation
        await self._check_stopped_async()

        # Update progress - Starting section analysis
        progress = self._progress_calculator.calculate_markdown_progress("section_analysis", 0, 1)
        msg = self._status_formatter.format_markdown_status("section_analysis", current=0, total=1)
        self._update_progress(progress, msg)

        # Check for cancellation
        await self._check_stopped_async()

        # Process the markdown
        result = await md_to_tree(
            md_path=self.file_path,
            if_thinning=self.config.get('thinning_enabled', False),
            min_token_threshold=self.config.get('thinning_threshold', 5000),
            if_add_node_summary=opt.if_add_node_summary == 'yes',
            summary_token_threshold=self.config.get('summary_token_threshold', 200),
            model=opt.model,
            if_add_doc_description=opt.if_add_doc_description == 'yes',
            if_add_node_text=opt.if_add_node_text == 'yes',
            if_add_node_id=opt.if_add_node_id == 'yes'
        )

        # Check for cancellation
        await self._check_stopped_async()

        # Update progress - Complete
        progress = self._progress_calculator.calculate_markdown_progress("ai_inference", 1, 1)
        msg = self._status_formatter.format_complete()
        self._force_progress_update(progress, msg)

        return {
            'success': True,
            'file_type': 'markdown',
            'file_path': self.file_path,
            'result': result,
            'output_file': self._get_output_path(self.file_path)
        }

    def _get_output_path(self, file_path: str) -> str:
        """Get the output file path for results.

        Args:
            file_path: Input file path

        Returns:
            Output file path
        """
        file_name = Path(file_path).stem
        output_dir = Path("./results")
        output_dir.mkdir(parents=True, exist_ok=True)
        return str(output_dir / f"{file_name}_structure.json")


def save_result_to_file(result: dict[str, Any], output_path: str) -> None:
    """Save processing result to JSON file with atomic write.

    @MX:NOTE: Uses atomic_write_json for data integrity.

    Args:
        result: Result dictionary from processing
        output_path: Path to save the output file
    """
    # Create output directory if needed
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Use atomic write for data integrity
    atomic_write_json(output_path, result['result'])
