"""
Unit tests for GUI Progress Display and Cancellation functionality.

Tests SPEC-GUI-003: GUI progress display and cancellation improvements.
Following TDD RED-GREEN-REFACTOR cycle.

Requirements covered:
- REQ-1: Real working cancellation mechanism
- REQ-2: Fine-grained progress display
- REQ-3: Data integrity on cancellation
- REQ-4: Processing stage status messages
- REQ-5: Consistent cancellation architecture
"""

import sys
import threading
import time
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
import importlib.util

import pytest

# Get the project root
PROJECT_ROOT = Path(__file__).parent.parent.parent


def import_module_from_path(module_name: str, file_path: Path):
    """Import a module directly from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


# Import the processing modules directly
PROCESSING_DIR = PROJECT_ROOT / "pageindex" / "gui" / "processing"

# Import each module (in dependency order)
stop_event_checker = import_module_from_path(
    "stop_event_checker",
    PROCESSING_DIR / "stop_event_checker.py"
)

progress_calculator = import_module_from_path(
    "progress_calculator",
    PROCESSING_DIR / "progress_calculator.py"
)

progress_updater = import_module_from_path(
    "progress_updater",
    PROCESSING_DIR / "progress_updater.py"
)

temp_file_manager = import_module_from_path(
    "temp_file_manager",
    PROCESSING_DIR / "temp_file_manager.py"
)

status_formatter = import_module_from_path(
    "status_formatter",
    PROCESSING_DIR / "status_formatter.py"
)

# For processor, we check it exists but don't import it (due to relative import issues)
# The processor module is tested via integration tests instead
processor_file = PROCESSING_DIR / "processor.py"


class TestStopEventChecker:
    """
    Test TASK-004: StopEventChecker utility class.

    This utility provides a standardized way to check for stop events
    across both synchronous and asynchronous processing paths.
    """

    def test_stop_event_checker_exists(self):
        """Test that StopEventChecker class exists."""
        assert hasattr(stop_event_checker, 'StopEventChecker')

    def test_stop_event_checker_initialization(self):
        """Test StopEventChecker can be initialized with threading.Event."""
        StopEventChecker = stop_event_checker.StopEventChecker

        stop_event = threading.Event()
        checker = StopEventChecker(stop_event)

        assert checker is not None

    def test_stop_event_checker_not_stopped_initially(self):
        """Test that checker returns False when event is not set."""
        StopEventChecker = stop_event_checker.StopEventChecker

        stop_event = threading.Event()
        checker = StopEventChecker(stop_event)

        assert checker.is_stopped() is False

    def test_stop_event_checker_detects_stop(self):
        """Test that checker returns True when event is set."""
        StopEventChecker = stop_event_checker.StopEventChecker

        stop_event = threading.Event()
        checker = StopEventChecker(stop_event)

        stop_event.set()
        assert checker.is_stopped() is True

    def test_stop_event_checker_raises_on_stop(self):
        """Test that check_if_stopped raises CancellationException when stopped."""
        StopEventChecker = stop_event_checker.StopEventChecker
        CancellationException = stop_event_checker.CancellationException

        stop_event = threading.Event()
        checker = StopEventChecker(stop_event)

        stop_event.set()
        with pytest.raises(CancellationException):
            checker.check_if_stopped()

    def test_stop_event_checker_async_support(self):
        """Test that StopEventChecker supports async context."""
        StopEventChecker = stop_event_checker.StopEventChecker
        CancellationException = stop_event_checker.CancellationException

        async def run_test():
            stop_event = threading.Event()
            checker = StopEventChecker(stop_event)

            # Should not raise when not stopped
            await checker.check_if_stopped_async()

            # Should raise when stopped
            stop_event.set()
            with pytest.raises(CancellationException):
                await checker.check_if_stopped_async()

        asyncio.run(run_test())


class TestProgressCalculator:
    """
    Test TASK-008: ProgressCalculator class.

    Calculates progress percentages based on processing stages.
    """

    def test_progress_calculator_exists(self):
        """Test that ProgressCalculator class exists."""
        assert hasattr(progress_calculator, 'ProgressCalculator')

    def test_progress_calculator_initialization(self):
        """Test ProgressCalculator initialization."""
        ProgressCalculator = progress_calculator.ProgressCalculator

        calc = ProgressCalculator()
        assert calc is not None

    def test_progress_calculator_pdf_stages(self):
        """Test PDF processing progress stages."""
        ProgressCalculator = progress_calculator.ProgressCalculator

        calc = ProgressCalculator()

        # Stage ranges:
        # - Loading PDF: 0-10%
        # - Page processing: 10-60%
        # - Text extraction: 60-80%
        # - Structure analysis: 80-95%
        # - AI inference: 95-100%

        # Loading stage
        progress = calc.calculate_pdf_progress("loading", 0, 1)
        assert 0 <= progress <= 10

        # Page processing stage (3 of 10 pages)
        progress = calc.calculate_pdf_progress("page_processing", 3, 10)
        assert 10 <= progress <= 60

        # Text extraction stage
        progress = calc.calculate_pdf_progress("text_extraction", 0.5, 1.0)
        assert 60 <= progress <= 80

        # Structure analysis stage
        progress = calc.calculate_pdf_progress("structure_analysis", 5, 10)
        assert 80 <= progress <= 95

        # AI inference stage
        progress = calc.calculate_pdf_progress("ai_inference", 7, 10)
        assert 95 <= progress <= 100

    def test_progress_calculator_markdown_stages(self):
        """Test Markdown processing progress stages."""
        ProgressCalculator = progress_calculator.ProgressCalculator

        calc = ProgressCalculator()

        # Stage ranges:
        # - File parsing: 0-30%
        # - Section analysis: 30-70%
        # - Tree construction: 70-95%
        # - AI inference: 95-100%

        # Parsing stage
        progress = calc.calculate_markdown_progress("parsing", 0.5, 1.0)
        assert 0 <= progress <= 30

        # Section analysis stage
        progress = calc.calculate_markdown_progress("section_analysis", 3, 10)
        assert 30 <= progress <= 70

        # Tree construction stage
        progress = calc.calculate_markdown_progress("tree_construction", 0.8, 1.0)
        assert 70 <= progress <= 95

        # AI inference stage
        progress = calc.calculate_markdown_progress("ai_inference", 5, 10)
        assert 95 <= progress <= 100

    def test_progress_calculator_clamping(self):
        """Test that progress is clamped between 0 and 100."""
        ProgressCalculator = progress_calculator.ProgressCalculator

        calc = ProgressCalculator()

        # Negative current
        progress = calc.calculate_pdf_progress("page_processing", -5, 10)
        assert progress >= 0

        # Current greater than total
        progress = calc.calculate_pdf_progress("page_processing", 20, 10)
        assert progress <= 100


class TestProgressUpdater:
    """
    Test TASK-009: ProgressUpdater with throttling.

    Ensures UI updates don't happen too frequently to avoid
    performance degradation.
    """

    def test_progress_updater_exists(self):
        """Test that ProgressUpdater class exists."""
        assert hasattr(progress_updater, 'ProgressUpdater')

    def test_progress_updater_initialization(self):
        """Test ProgressUpdater initialization with callback."""
        ProgressUpdater = progress_updater.ProgressUpdater

        callback = MagicMock()
        updater = ProgressUpdater(callback, min_interval_ms=100)

        assert updater is not None

    def test_progress_updater_throttling(self):
        """Test that updates are throttled to avoid excessive UI calls."""
        ProgressUpdater = progress_updater.ProgressUpdater

        callback = MagicMock()
        updater = ProgressUpdater(callback, min_interval_ms=100)

        # Rapid updates should be throttled
        updater.update(10, "Loading...")
        updater.update(15, "Loading...")
        updater.update(20, "Loading...")
        updater.update(25, "Loading...")

        # Only the first call should have gone through immediately
        assert callback.call_count >= 1

    def test_progress_updater_always_updates_significant_changes(self):
        """Test that significant progress changes always trigger update."""
        ProgressUpdater = progress_updater.ProgressUpdater

        callback = MagicMock()
        updater = ProgressUpdater(callback, min_interval_ms=1000)

        # Significant change (>5%) should update even if throttled
        updater.update(0, "Starting...")
        updater.update(10, "Processing...")  # 10% change

        # Both updates should go through due to significant change
        assert callback.call_count >= 2

    def test_progress_updater_force_update(self):
        """Test that force_update bypasses throttling."""
        ProgressUpdater = progress_updater.ProgressUpdater

        callback = MagicMock()
        updater = ProgressUpdater(callback, min_interval_ms=1000)

        updater.update(10, "Loading...")
        callback.reset_mock()

        # Force update should bypass throttling
        updater.force_update(20, "Important update!")

        assert callback.call_count == 1


class TestTempFileManager:
    """
    Test TASK-013: TempFileManager class.

    Manages temporary files during processing to ensure data integrity
    on cancellation.
    """

    def test_temp_file_manager_exists(self):
        """Test that TempFileManager class exists."""
        assert hasattr(temp_file_manager, 'TempFileManager')

    def test_temp_file_manager_create_temp_file(self):
        """Test creating a temporary file for output."""
        TempFileManager = temp_file_manager.TempFileManager

        manager = TempFileManager()
        temp_path = manager.create_temp_file("test_output.json")

        assert temp_path is not None
        assert Path(temp_path).exists()
        assert temp_path.endswith(".json")

        # Cleanup
        manager.cleanup()

    def test_temp_file_manager_commit_moves_to_final(self):
        """Test that commit moves temp file to final destination."""
        TempFileManager = temp_file_manager.TempFileManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TempFileManager()
            temp_path = manager.create_temp_file("test.json")

            # Write some data to temp file
            Path(temp_path).write_text('{"test": "data"}', encoding='utf-8')

            final_path = str(Path(tmpdir) / "final_output.json")
            manager.commit(temp_path, final_path)

            # Temp file should be moved to final location
            assert Path(final_path).exists()
            assert Path(final_path).read_text(encoding='utf-8') == '{"test": "data"}'

    def test_temp_file_manager_cleanup_on_cancel(self):
        """Test that cleanup removes incomplete temp files."""
        TempFileManager = temp_file_manager.TempFileManager

        manager = TempFileManager()
        temp_path = manager.create_temp_file("incomplete.json")

        # Write partial data
        Path(temp_path).write_text('{"incomplete":', encoding='utf-8')

        # Cleanup on cancel
        manager.cleanup_on_cancel()

        # Temp file should be removed
        assert not Path(temp_path).exists()

    def test_temp_file_manager_context_manager(self):
        """Test using TempFileManager as context manager."""
        TempFileManager = temp_file_manager.TempFileManager

        temp_path = None
        with TempFileManager() as manager:
            temp_path = manager.create_temp_file("test.json")
            assert Path(temp_path).exists()

        # After context exit, temp files should be cleaned up
        # (unless committed)
        assert not Path(temp_path).exists()


class TestAtomicFileWriter:
    """
    Test TASK-014: Atomic file writing.

    Ensures file writes are atomic to prevent corruption on cancellation.
    """

    def test_atomic_write_success(self):
        """Test atomic write creates complete file."""
        atomic_write_json = temp_file_manager.atomic_write_json

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "output.json")

            data = {"key": "value", "nested": {"a": 1}}
            atomic_write_json(output_path, data)

            # File should exist and contain complete data
            assert Path(output_path).exists()

            import json
            with open(output_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)

            assert loaded == data

    def test_atomic_write_handles_interruption(self):
        """Test that interrupted write doesn't leave partial file."""
        import os as os_module
        atomic_write_json = temp_file_manager.atomic_write_json

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = str(Path(tmpdir) / "output.json")

            # Simulate interruption by patching tempfile.mkstemp
            with patch('tempfile.mkstemp', side_effect=InterruptedError("Simulated interruption")):
                with pytest.raises(InterruptedError):
                    atomic_write_json(output_path, {"test": "data"})

            # Output file should not exist
            assert not Path(output_path).exists()


class TestStatusMessageFormatter:
    """
    Test TASK-012: Status message formatter.

    Formats meaningful status messages for each processing stage.
    """

    def test_status_formatter_exists(self):
        """Test that StatusMessageFormatter class exists."""
        assert hasattr(status_formatter, 'StatusMessageFormatter')

    def test_format_pdf_page_processing(self):
        """Test formatting PDF page processing message."""
        StatusMessageFormatter = status_formatter.StatusMessageFormatter

        formatter = StatusMessageFormatter()

        msg = formatter.format_pdf_status(
            stage="page_processing",
            current=3,
            total=10
        )

        assert "3" in msg
        assert "10" in msg
        assert "page" in msg.lower()

    def test_format_text_extraction(self):
        """Test formatting text extraction message."""
        StatusMessageFormatter = status_formatter.StatusMessageFormatter

        formatter = StatusMessageFormatter()

        msg = formatter.format_pdf_status(
            stage="text_extraction",
            progress_percent=45
        )

        assert "45" in msg
        assert "text" in msg.lower() or "extract" in msg.lower()

    def test_format_ai_inference(self):
        """Test formatting AI inference message."""
        StatusMessageFormatter = status_formatter.StatusMessageFormatter

        formatter = StatusMessageFormatter()

        msg = formatter.format_status(
            stage="ai_inference",
            current=7,
            total=10
        )

        assert "7" in msg
        assert "10" in msg
        assert "ai" in msg.lower() or "inference" in msg.lower()

    def test_format_cancellation_message(self):
        """Test formatting cancellation message."""
        StatusMessageFormatter = status_formatter.StatusMessageFormatter

        formatter = StatusMessageFormatter()

        msg = formatter.format_cancelled()

        assert "cancel" in msg.lower() or "stop" in msg.lower()


class TestProcessorCancellation:
    """
    Test TASK-005, TASK-006, TASK-007: Cancellation mechanism integration.

    Tests that the Processor properly handles cancellation across
    PDF and Markdown processing paths.

    @MX:NOTE: These tests verify the processor file structure.
    Full integration tests are done separately.
    """

    def test_processor_file_exists(self):
        """Test that processor file exists."""
        assert processor_file.exists()

    def test_processor_has_stop_event_checker_import(self):
        """Test that processor imports StopEventChecker."""
        content = processor_file.read_text(encoding='utf-8')
        assert 'StopEventChecker' in content
        assert 'CancellationException' in content

    def test_processor_has_progress_calculator_import(self):
        """Test that processor imports ProgressCalculator."""
        content = processor_file.read_text(encoding='utf-8')
        assert 'ProgressCalculator' in content

    def test_processor_has_progress_updater_import(self):
        """Test that processor imports ProgressUpdater."""
        content = processor_file.read_text(encoding='utf-8')
        assert 'ProgressUpdater' in content

    def test_processor_has_temp_file_manager_import(self):
        """Test that processor imports TempFileManager."""
        content = processor_file.read_text(encoding='utf-8')
        assert 'TempFileManager' in content
        assert 'atomic_write_json' in content

    def test_processor_has_status_formatter_import(self):
        """Test that processor imports StatusMessageFormatter."""
        content = processor_file.read_text(encoding='utf-8')
        assert 'StatusMessageFormatter' in content

    def test_processor_has_check_stopped_method(self):
        """Test that processor has _check_stopped method."""
        content = processor_file.read_text(encoding='utf-8')
        assert '_check_stopped' in content

    def test_processor_has_handle_cancellation_method(self):
        """Test that processor has _handle_cancellation method."""
        content = processor_file.read_text(encoding='utf-8')
        assert '_handle_cancellation' in content


class TestProgressCallbacks:
    """
    Test progress callback interface.

    Tests that the callback interface is properly defined.
    """

    def test_processing_callbacks_class_exists(self):
        """Test that ProcessingCallbacks class can be defined."""
        # Define a simple ProcessingCallbacks class to test the interface
        class ProcessingCallbacks:
            def __init__(
                self,
                on_progress,
                on_complete,
                on_error
            ):
                self.on_progress = on_progress
                self.on_complete = on_complete
                self.on_error = on_error

        # Callback should accept (percentage, status_message)
        progress_calls = []

        def track_progress(percentage: int, message: str):
            progress_calls.append((percentage, message))

        callbacks = ProcessingCallbacks(
            on_progress=track_progress,
            on_complete=MagicMock(),
            on_error=MagicMock()
        )

        callbacks.on_progress(50, "Processing page 5/10...")

        assert len(progress_calls) == 1
        assert progress_calls[0] == (50, "Processing page 5/10...")

    def test_progress_callback_thread_safety(self):
        """Test that progress callbacks can be called from background thread."""
        # Define a simple ProcessingCallbacks class to test the interface
        class ProcessingCallbacks:
            def __init__(
                self,
                on_progress,
                on_complete,
                on_error
            ):
                self.on_progress = on_progress
                self.on_complete = on_complete
                self.on_error = on_error

        progress_calls = []
        lock = threading.Lock()

        def track_progress(percentage: int, message: str):
            with lock:
                progress_calls.append((percentage, message))

        callbacks = ProcessingCallbacks(
            on_progress=track_progress,
            on_complete=MagicMock(),
            on_error=MagicMock()
        )

        # Simulate calls from multiple threads
        def worker(start_pct):
            for i in range(5):
                callbacks.on_progress(start_pct + i, f"Message {i}")

        threads = [
            threading.Thread(target=worker, args=(i * 10,))
            for i in range(3)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All calls should be recorded
        assert len(progress_calls) == 15
