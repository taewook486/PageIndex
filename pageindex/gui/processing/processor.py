"""
Background Processing Module for PageIndex GUI.

This module handles file processing in background threads to keep
the GUI responsive during long-running operations.
"""

import asyncio
import threading
import queue
from typing import Callable, Optional, Dict, Any, Union
from pathlib import Path
import os


class ProcessingCallbacks:
    """Callback functions for processing updates."""

    def __init__(
        self,
        on_progress: Callable[[int, str], None],
        on_complete: Callable[[Dict[str, Any]], None],
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
    """Process files in background thread with event loop."""

    def __init__(
        self,
        file_path: str,
        file_type: str,
        config: Dict[str, Any],
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

    def run(self):
        """Run the processing in background thread."""
        try:
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

        except Exception as e:
            # Notify error with full traceback for debugging
            import traceback
            error_details = f"{str(e)}\n\n{traceback.format_exc()}"
            self.callbacks.on_error(error_details)

    def stop(self):
        """Stop the processing."""
        self._stop_event.set()

    def _process_pdf_sync(self) -> Dict[str, Any]:
        """Process PDF file synchronously.

        PDF processing uses asyncio.run() internally, so we can't
        call it from within an event loop. This method handles it
        synchronously.

        Returns:
            Dictionary with processing results
        """
        from pageindex.page_index import page_index_main, config
        from pageindex.utils import ConfigLoader

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
            import os
            os.environ['OPENAI_BASE_URL'] = self.config['base_url']

        opt = loader.load(user_config)

        # Update progress
        self.callbacks.on_progress(10, "Loading PDF...")

        # Process the PDF (synchronous - uses asyncio.run() internally)
        self.callbacks.on_progress(20, "Extracting text from PDF...")
        result = page_index_main(self.file_path, opt)

        self.callbacks.on_progress(100, "Processing complete!")

        return {
            'success': True,
            'file_type': 'pdf',
            'file_path': self.file_path,
            'result': result,
            'output_file': self._get_output_path(self.file_path)
        }

    async def _process_file(self) -> Dict[str, Any]:
        """Process the file asynchronously.

        Returns:
            Dictionary with processing results
        """
        # Notify start
        self.callbacks.on_progress(0, "Starting processing...")

        if self.file_type == 'pdf':
            return await self._process_pdf()
        elif self.file_type == 'markdown':
            return await self._process_markdown()
        else:
            raise ValueError(f"Unsupported file type: {self.file_type}")

    async def _process_pdf(self) -> Dict[str, Any]:
        """Process PDF file.

        Returns:
            Dictionary with processing results
        """
        from pageindex.page_index import page_index_main, config
        from pageindex.utils import ConfigLoader

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
            import os
            os.environ['OPENAI_BASE_URL'] = self.config['base_url']

        opt = loader.load(user_config)

        # Update progress
        self.callbacks.on_progress(10, "Loading PDF...")

        # Process the PDF
        self.callbacks.on_progress(20, "Extracting text from PDF...")
        result = page_index_main(self.file_path, opt)

        self.callbacks.on_progress(100, "Processing complete!")

        return {
            'success': True,
            'file_type': 'pdf',
            'file_path': self.file_path,
            'result': result,
            'output_file': self._get_output_path(self.file_path)
        }

    async def _process_markdown(self) -> Dict[str, Any]:
        """Process Markdown file.

        Returns:
            Dictionary with processing results
        """
        from pageindex.page_index_md import md_to_tree
        from pageindex.utils import ConfigLoader

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
            import os
            os.environ['OPENAI_BASE_URL'] = self.config['base_url']

        opt = loader.load(user_config)

        # Update progress
        self.callbacks.on_progress(10, "Loading Markdown file...")

        # Process the markdown
        self.callbacks.on_progress(20, "Parsing Markdown structure...")
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

        self.callbacks.on_progress(100, "Processing complete!")

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


def save_result_to_file(result: Dict[str, Any], output_path: str) -> None:
    """Save processing result to JSON file.

    Args:
        result: Result dictionary from processing
        output_path: Path to save the output file
    """
    import json

    # Create output directory if needed
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save result
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result['result'], f, indent=2, ensure_ascii=False)
