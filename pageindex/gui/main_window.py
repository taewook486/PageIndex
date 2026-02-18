"""
PageIndex GUI Main Window.

This module provides the main application window for the PageIndex GUI.
"""

import os
import json
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from typing import Optional, Dict, Any
from pathlib import Path
from .processing import ProcessingCallbacks, BackgroundProcessor, save_result_to_file
from .json_viewer import JsonViewerTabView


class PageIndexMainWindow(ctk.CTk):
    """Main application window for PageIndex GUI."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        # Configure window
        self.title("PageIndex GUI")
        self.geometry("900x700")

        # Make window resizable
        self.minsize(800, 600)

        # State variables
        self.selected_file: Optional[str] = None
        self.file_type: Optional[str] = None  # 'pdf' or 'markdown'
        self.is_processing: bool = False
        self.current_processor: Optional[BackgroundProcessor] = None
        self.processing_result: Optional[Dict[str, Any]] = None

        # Build UI
        self._create_menu()
        self._create_main_layout()

        # Center window on screen
        self._center_window()

    def _create_menu(self):
        """Create the application menu bar."""
        # Create menubar (using standard tkinter menu)
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open PDF...", command=self._open_pdf_file)
        file_menu.add_command(label="Open Markdown...", command=self._open_markdown_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Preferences...", command=self._open_settings)
        settings_menu.add_command(label="API Key...", command=self._open_api_key_settings)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _create_main_layout(self):
        """Create the main application layout."""
        # Create main scrollable frame
        self.main_frame = ctk.CTkScrollableFrame(
            self,
            label_text="PageIndex - Document Structure Generator",
            label_font=ctk.CTkFont(size=18, weight="bold")
        )
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # File Selection Section
        self._create_file_selection_section()

        # Configuration Section
        self._create_configuration_section()

        # Action Buttons Section
        self._create_action_buttons_section()

        # Progress Section
        self._create_progress_section()

        # Results Section
        self._create_results_section()

    def _create_file_selection_section(self):
        """Create the file selection section."""
        file_frame = ctk.CTkFrame(self.main_frame)
        file_frame.pack(fill="x", padx=5, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            file_frame,
            text="File Selection",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(10, 5))

        # File drop zone / display
        self.file_display_frame = ctk.CTkFrame(file_frame, height=100)
        self.file_display_frame.pack(fill="x", padx=10, pady=5)

        self.file_label = ctk.CTkLabel(
            self.file_display_frame,
            text="📄 Drag & Drop PDF/Markdown file here\nor",
            font=ctk.CTkFont(size=12)
        )
        self.file_label.pack(expand=True)

        # Browse button
        browse_btn = ctk.CTkButton(
            file_frame,
            text="Browse Files...",
            command=self._browse_files,
            width=200
        )
        browse_btn.pack(pady=(5, 10))

        # Selected file info
        self.selected_file_label = ctk.CTkLabel(
            file_frame,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.selected_file_label.pack(pady=(0, 10))

    def _create_configuration_section(self):
        """Create the configuration section."""
        config_frame = ctk.CTkFrame(self.main_frame)
        config_frame.pack(fill="x", padx=5, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            config_frame,
            text="Configuration",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(10, 5))

        # Create grid layout for configuration options
        config_grid = ctk.CTkFrame(config_frame, fg_color="transparent")
        config_grid.pack(fill="x", padx=10, pady=5)

        # Model selection
        ctk.CTkLabel(config_grid, text="AI Model:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.model_var = ctk.StringVar(value="glm-5")
        self.model_entry = ctk.CTkEntry(config_grid, textvariable=self.model_var, width=200)
        self.model_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Base URL
        ctk.CTkLabel(config_grid, text="Base URL:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.base_url_var = ctk.StringVar(value="https://api.z.ai/api/coding/paas/v4")
        self.base_url_entry = ctk.CTkEntry(config_grid, textvariable=self.base_url_var, width=300)
        self.base_url_entry.grid(row=0, column=3, columnspan=3, sticky="w", padx=5, pady=5)

        # PDF Options section
        pdf_options_frame = ctk.CTkFrame(config_frame)
        pdf_options_frame.pack(fill="x", padx=10, pady=5)

        # Section title
        ctk.CTkLabel(pdf_options_frame, text="PDF Options", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=6, sticky="w", padx=5, pady=(5, 0))

        # TOC Check Pages
        ctk.CTkLabel(pdf_options_frame, text="TOC Check Pages:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.toc_check_pages_var = ctk.StringVar(value="20")
        self.toc_check_pages_entry = ctk.CTkEntry(pdf_options_frame, textvariable=self.toc_check_pages_var, width=100)
        self.toc_check_pages_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Max Pages/Node
        ctk.CTkLabel(pdf_options_frame, text="Max Pages/Node:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.max_pages_var = ctk.StringVar(value="10")
        self.max_pages_entry = ctk.CTkEntry(pdf_options_frame, textvariable=self.max_pages_var, width=100)
        self.max_pages_entry.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        # Max Tokens/Node
        ctk.CTkLabel(pdf_options_frame, text="Max Tokens/Node:").grid(row=1, column=4, sticky="w", padx=5, pady=5)
        self.max_tokens_var = ctk.StringVar(value="20000")
        self.max_tokens_entry = ctk.CTkEntry(pdf_options_frame, textvariable=self.max_tokens_var, width=100)
        self.max_tokens_entry.grid(row=1, column=5, sticky="w", padx=5, pady=5)

        # Output Options section
        output_options_frame = ctk.CTkFrame(config_frame)
        output_options_frame.pack(fill="x", padx=10, pady=5)

        # Section title
        ctk.CTkLabel(output_options_frame, text="Output Options", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=4, sticky="w", padx=5, pady=(5, 0))

        # Checkboxes for output options
        self.add_node_id_var = ctk.BooleanVar(value=True)
        self.add_node_summary_var = ctk.BooleanVar(value=True)
        self.add_doc_description_var = ctk.BooleanVar(value=False)
        self.add_node_text_var = ctk.BooleanVar(value=False)

        ctk.CTkCheckBox(
            output_options_frame,
            text="Add Node ID",
            variable=self.add_node_id_var
        ).grid(row=1, column=0, sticky="w", padx=5, pady=5)

        ctk.CTkCheckBox(
            output_options_frame,
            text="Add Summary",
            variable=self.add_node_summary_var
        ).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ctk.CTkCheckBox(
            output_options_frame,
            text="Add Doc Description",
            variable=self.add_doc_description_var
        ).grid(row=2, column=0, sticky="w", padx=5, pady=5)

        ctk.CTkCheckBox(
            output_options_frame,
            text="Add Node Text",
            variable=self.add_node_text_var
        ).grid(row=2, column=1, sticky="w", padx=5, pady=5)

    def _create_action_buttons_section(self):
        """Create the action buttons section."""
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(fill="x", padx=5, pady=10)

        self.start_button = ctk.CTkButton(
            button_frame,
            text="▶ Start Conversion",
            command=self._start_conversion,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.start_button.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        self.cancel_button = ctk.CTkButton(
            button_frame,
            text="⏹ Cancel",
            command=self._cancel_processing,
            height=40,
            state="disabled",
            fg_color="darkred",
            hover_color="red"
        )
        self.cancel_button.pack(side="left", padx=5, pady=10)

        self.clear_button = ctk.CTkButton(
            button_frame,
            text="Clear",
            command=self._clear_form,
            height=40
        )
        self.clear_button.pack(side="left", padx=5, pady=10)

        self.open_results_button = ctk.CTkButton(
            button_frame,
            text="Open Results Folder",
            command=self._open_results_folder,
            height=40,
            state="disabled"
        )
        self.open_results_button.pack(side="right", padx=10, pady=10)

    def _create_progress_section(self):
        """Create the progress display section."""
        progress_frame = ctk.CTkFrame(self.main_frame)
        progress_frame.pack(fill="x", padx=5, pady=10)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(progress_frame, width=400)
        self.progress_bar.pack(padx=10, pady=(10, 5))
        self.progress_bar.set(0)

        # Status label
        self.status_label = ctk.CTkLabel(
            progress_frame,
            text="Ready",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(pady=(0, 10))

    def _create_results_section(self):
        """Create the results display section with improved JSON viewer."""
        results_frame = ctk.CTkFrame(self.main_frame)
        results_frame.pack(fill="both", expand=True, padx=5, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            results_frame,
            text="Results",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(10, 5))

        # Create tabbed JSON viewer
        self.json_viewer = JsonViewerTabView(
            results_frame,
            width=700,
            height=200
        )
        self.json_viewer.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Keep old results_text for progress messages (hidden but used for log)
        self.results_text = ctk.CTkTextbox(
            results_frame,
            height=0,  # Hidden
            font=ctk.CTkFont(family="Courier", size=10)
        )
        self.results_text.pack(fill="both", expand=False, padx=10, pady=(0, 10))
        self.results_text.insert("1.0", "Processing...")
        self.results_text.configure(state="disabled")

    def _center_window(self):
        """Center the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    # Event handlers
    def _open_pdf_file(self):
        """Handle Open PDF menu item."""
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if file_path:
            self._load_file(file_path, "pdf")

    def _open_markdown_file(self):
        """Handle Open Markdown menu item."""
        file_path = filedialog.askopenfilename(
            title="Select Markdown File",
            filetypes=[("Markdown Files", "*.md *.markdown"), ("All Files", "*.*")]
        )
        if file_path:
            self._load_file(file_path, "markdown")

    def _browse_files(self):
        """Handle browse button click."""
        file_path = filedialog.askopenfilename(
            title="Select File",
            filetypes=[
                ("Supported Files", "*.pdf *.md *.markdown"),
                ("PDF Files", "*.pdf"),
                ("Markdown Files", "*.md *.markdown"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            # Detect file type from extension
            if file_path.lower().endswith('.pdf'):
                self._load_file(file_path, "pdf")
            elif file_path.lower().endswith(('.md', '.markdown')):
                self._load_file(file_path, "markdown")
            else:
                self._show_error("Unsupported file type. Please select PDF or Markdown file.")

    def _load_file(self, file_path: str, file_type: str):
        """Load a file into the application."""
        if not os.path.exists(file_path):
            self._show_error(f"File not found: {file_path}")
            return

        self.selected_file = file_path
        self.file_type = file_type

        # Update UI
        file_name = os.path.basename(file_path)
        self.file_label.configure(text=f"📄 {file_name}")
        self.selected_file_label.configure(text=f"Selected: {file_path}")

        # Enable start button
        self.start_button.configure(state="normal")

    def _clear_form(self):
        """Clear all form fields."""
        self.selected_file = None
        self.file_type = None
        self.file_label.configure(text="📄 Drag & Drop PDF/Markdown file here\nor")
        self.selected_file_label.configure(text="")
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", "Results will be displayed here after processing...")
        self.results_text.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="Ready")
        self.open_results_button.configure(state="disabled")

    def _start_conversion(self):
        """Start the file conversion process."""
        if not self.selected_file:
            self._show_error("Please select a file first.")
            return

        if self.is_processing:
            self._show_error("Processing already in progress.")
            return

        # Validate configuration
        try:
            config = self._get_configuration()
        except ValueError as e:
            self._show_error(str(e))
            return

        # Update UI state
        self.is_processing = True
        self.start_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="Starting processing...")

        # Clear previous results
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", "Processing started...\n\n")
        self.results_text.configure(state="disabled")

        # Create callbacks
        callbacks = ProcessingCallbacks(
            on_progress=self._on_progress_update,
            on_complete=self._on_processing_complete,
            on_error=self._on_processing_error
        )

        # Start background processing
        self.current_processor = BackgroundProcessor(
            file_path=self.selected_file,
            file_type=self.file_type,
            config=config,
            callbacks=callbacks
        )
        self.current_processor.start()

        # Enable cancel button, disable start button
        self.cancel_button.configure(state="normal")
        self.start_button.configure(state="disabled")

    def _cancel_processing(self):
        """Cancel the ongoing processing."""
        if self.current_processor and self.is_processing:
            # Stop the processor
            if hasattr(self.current_processor, 'stop'):
                self.current_processor.stop()

            # Update UI state
            self.is_processing = False
            self.current_processor = None
            self.start_button.configure(state="normal")
            self.cancel_button.configure(state="disabled")

            # Update status
            self.status_label.configure(text="Processing cancelled by user")

            # Update results text
            self.results_text.configure(state="normal")
            self.results_text.insert("end", "\n⏹ Processing cancelled by user\n")
            self.results_text.see("end")
            self.results_text.configure(state="disabled")
        else:
            self._show_error("No processing to cancel.")

    def _get_configuration(self) -> Dict[str, Any]:
        """Get and validate configuration from UI.

        Returns:
            Configuration dictionary

        Raises:
            ValueError: If configuration is invalid
        """
        config = {}

        # Model
        config['model'] = self.model_var.get().strip()
        if not config['model']:
            raise ValueError("AI Model is required")

        # Base URL (optional)
        base_url = self.base_url_var.get().strip()
        if base_url:
            config['base_url'] = base_url

        # PDF options
        try:
            config['toc_check_pages'] = int(self.toc_check_pages_var.get())
            if config['toc_check_pages'] < 1:
                raise ValueError("TOC Check Pages must be at least 1")
        except ValueError as e:
            raise ValueError(f"Invalid TOC Check Pages: {e}")

        try:
            config['max_pages'] = int(self.max_pages_var.get())
            if config['max_pages'] < 1:
                raise ValueError("Max Pages/Node must be at least 1")
        except ValueError as e:
            raise ValueError(f"Invalid Max Pages/Node: {e}")

        try:
            config['max_tokens'] = int(self.max_tokens_var.get())
            if config['max_tokens'] < 100:
                raise ValueError("Max Tokens/Node must be at least 100")
        except ValueError as e:
            raise ValueError(f"Invalid Max Tokens/Node: {e}")

        # Output options
        config['add_node_id'] = self.add_node_id_var.get()
        config['add_node_summary'] = self.add_node_summary_var.get()
        config['add_doc_description'] = self.add_doc_description_var.get()
        config['add_node_text'] = self.add_node_text_var.get()

        return config

    def _on_progress_update(self, percentage: int, status: str):
        """Handle progress updates from background processor.

        Args:
            percentage: Progress percentage (0-100)
            status: Status message
        """
        # Update UI in thread-safe manner
        self.after(0, lambda: self._update_progress_ui(percentage, status))

    def _update_progress_ui(self, percentage: int, status: str):
        """Update progress UI (must be called from main thread).

        Args:
            percentage: Progress percentage (0-100)
            status: Status message
        """
        self.progress_bar.set(percentage / 100.0)
        self.status_label.configure(text=status)

        # Also update results text
        self.results_text.configure(state="normal")
        self.results_text.insert("end", f"[{percentage}%] {status}\n")
        self.results_text.see("end")
        self.results_text.configure(state="disabled")

    def _on_processing_complete(self, result: Dict[str, Any]):
        """Handle processing completion.

        Args:
            result: Processing result dictionary
        """
        # Update UI in thread-safe manner
        self.after(0, lambda: self._handle_completion(result))

    def _handle_completion(self, result: Dict[str, Any]):
        """Handle completion (must be called from main thread).

        Args:
            result: Processing result dictionary
        """
        self.processing_result = result
        self.is_processing = False
        self.current_processor = None

        # Disable cancel button, enable start button
        self.cancel_button.configure(state="disabled")
        self.start_button.configure(state="normal")

        # Save result to file
        if result.get('success'):
            try:
                output_path = result.get('output_file')
                if output_path:
                    save_result_to_file(result, output_path)

                    # Display result
                    self._display_result(result)

                    # Enable open results button
                    self.open_results_button.configure(state="normal")

                    # Update status
                    self.status_label.configure(
                        text=f"✅ Complete! Results saved to {output_path}"
                    )

                    # Update progress
                    self.progress_bar.set(1.0)

            except Exception as e:
                self._show_error(f"Failed to save results: {e}")
                self.is_processing = False
                self.start_button.configure(state="normal")

        else:
            self._show_error(f"Processing failed: {result.get('error', 'Unknown error')}")
            self.is_processing = False
            self.start_button.configure(state="normal")

    def _on_processing_error(self, error: str):
        """Handle processing error.

        Args:
            error: Error message
        """
        # Update UI in thread-safe manner
        self.after(0, lambda: self._handle_error(error))

    def _handle_error(self, error: str):
        """Handle error (must be called from main thread).

        Args:
            error: Error message
        """
        self.is_processing = False
        self.current_processor = None

        # Disable cancel button, enable start button
        self.cancel_button.configure(state="disabled")
        self.start_button.configure(state="normal")

        self._show_error(f"Processing failed: {error}")

    def _display_result(self, result: Dict[str, Any]):
        """Display processing result in the improved JSON viewer.

        Args:
            result: Processing result dictionary
        """
        # Load result into the JSON viewer tab view
        self.json_viewer.load_result(result)

        # Also display summary in the hidden results_text for reference
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")

        # Display summary
        self.results_text.insert("end", "=" * 60 + "\n")
        self.results_text.insert("end", "PROCESSING COMPLETE\n")
        self.results_text.insert("end", "=" * 60 + "\n\n")

        self.results_text.insert("end", f"File: {result['file_path']}\n")
        self.results_text.insert("end", f"Type: {result['file_type'].upper()}\n")
        self.results_text.insert("end", f"Output: {result.get('output_file', 'N/A')}\n\n")

        # Display structure preview
        structure = result.get('result', {})
        if isinstance(structure, dict):
            doc_name = structure.get('doc_name', 'N/A')
            doc_description = structure.get('doc_description', None)
            tree_structure = structure.get('structure', [])

            self.results_text.insert("end", f"Document Name: {doc_name}\n")
            if doc_description:
                self.results_text.insert("end", f"Description: {doc_description}\n")

            self.results_text.insert("end", f"\nStructure: {len(tree_structure)} top-level nodes\n")
            self.results_text.insert("end", "\nView results in the tabs above for:\n")
            self.results_text.insert("end", "  - Formatted JSON with syntax highlighting\n")
            self.results_text.insert("end", "  - Interactive tree view\n")
            self.results_text.insert("end", "  - Summary statistics\n")
            self.results_text.insert("end", "\n" + "=" * 60 + "\n")

        self.results_text.configure(state="disabled")

    def _display_tree_structure(self, nodes, indent=0):
        """Display tree structure recursively.

        Args:
            nodes: List of nodes to display
            indent: Indentation level
        """
        for node in nodes:
            prefix = "  " * indent
            title = node.get('title', 'Untitled')
            node_id = node.get('node_id', '')
            start_idx = node.get('start_index', '')
            end_idx = node.get('end_index', '')

            self.results_text.insert("end", f"{prefix}├─ {title}")
            if node_id:
                self.results_text.insert("end", f" [{node_id}]")
            if start_idx and end_idx:
                self.results_text.insert("end", f" (pp. {start_idx}-{end_idx})")
            self.results_text.insert("end", "\n")

            # Recursively display child nodes
            child_nodes = node.get('nodes', [])
            if child_nodes:
                self._display_tree_structure(child_nodes, indent + 1)

    def _open_results_folder(self):
        """Open the results folder in file explorer."""
        results_dir = Path("./results")
        if results_dir.exists():
            os.startfile(results_dir)  # Windows
        else:
            self._show_error("Results folder not found.")

    def _open_settings(self):
        """Open settings dialog."""
        self._show_info("Settings dialog will be implemented in the next phase.")

    def _open_api_key_settings(self):
        """Open API key settings dialog."""
        self._show_info("API key settings will be implemented in the next phase.")

    def _show_about(self):
        """Show about dialog."""
        about_text = """
PageIndex GUI v1.0.0

A graphical user interface for the PageIndex
document processing system.

Convert PDF and Markdown documents into
hierarchical tree structures using AI.
        """
        self._show_info(about_text)

    def _show_error(self, message: str):
        """Show an error message."""
        import tkinter.messagebox as messagebox

        # Update status label
        self.status_label.configure(text=f"❌ Error: {message}")

        # Also show in results text area for better visibility
        self.results_text.configure(state="normal")
        self.results_text.insert("end", f"\n❌ ERROR: {message}\n")
        self.results_text.see("end")
        self.results_text.configure(state="disabled")

        # Show messagebox for critical errors
        if len(message) > 100 or "Traceback" in message or "Error" in message:
            # For long errors or tracebacks, show in a scrollable messagebox
            messagebox.showerror("PageIndex Error", message)

    def _show_info(self, message: str):
        """Show an info message."""
        # For now, use status label
        self.status_label.configure(text=f"ℹ️ {message}")
