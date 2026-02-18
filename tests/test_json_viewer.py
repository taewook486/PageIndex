"""
Test script for JSON Viewer components.

This script tests the JSON viewer widgets with sample data.
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import customtkinter as ctk
from pageindex.gui.json_viewer import (
    SyntaxHighlightedTextbox,
    TreeView,
    SummaryView,
    JsonViewerTabView
)


def load_sample_data() -> dict:
    """Load sample JSON data for testing.

    Returns:
        Sample result dictionary
    """
    # Use one of the test result files
    result_file = project_root / "tests" / "results" / "four-lectures_structure.json"

    if result_file.exists():
        with open(result_file, 'r', encoding='utf-8') as f:
            structure = json.load(f)

        return {
            'success': True,
            'file_path': 'tests/fixtures/four-lectures.pdf',
            'file_type': 'pdf',
            'output_file': str(result_file),
            'result': structure
        }

    # Fallback sample data
    return {
        'success': True,
        'file_path': 'sample.pdf',
        'file_type': 'pdf',
        'output_file': 'results/sample_structure.json',
        'result': {
            'doc_name': 'Sample Document',
            'doc_description': 'A sample document for testing',
            'structure': [
                {
                    'title': 'Chapter 1',
                    'start_index': 1,
                    'end_index': 5,
                    'node_id': '0001',
                    'nodes': [
                        {
                            'title': 'Section 1.1',
                            'start_index': 1,
                            'end_index': 2,
                            'node_id': '0002'
                        },
                        {
                            'title': 'Section 1.2',
                            'start_index': 3,
                            'end_index': 5,
                            'node_id': '0003'
                        }
                    ]
                },
                {
                    'title': 'Chapter 2',
                    'start_index': 6,
                    'end_index': 10,
                    'node_id': '0004'
                }
            ]
        }
    }


class JsonViewerTestApp(ctk.CTk):
    """Test application for JSON viewer components."""

    def __init__(self):
        """Initialize the test application."""
        super().__init__()

        self.title("JSON Viewer Test")
        self.geometry("1000x700")

        # Load sample data
        self.sample_data = load_sample_data()

        # Create UI
        self._create_ui()

    def _create_ui(self):
        """Create the user interface."""
        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=10, pady=10)

        title_label = ctk.CTkLabel(
            header_frame,
            text="JSON Viewer Component Test",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=10)

        info_label = ctk.CTkLabel(
            header_frame,
            text=f"Testing with: {self.sample_data.get('file_path', 'N/A')}",
            font=ctk.CTkFont(size=11)
        )
        info_label.pack(pady=(0, 10))

        # Test buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            button_frame,
            text="Test Tabbed Viewer",
            command=self._test_tabbed_viewer,
            width=200
        ).pack(side="left", padx=5, pady=10)

        ctk.CTkButton(
            button_frame,
            text="Test Individual Components",
            command=self._test_individual_components,
            width=200
        ).pack(side="left", padx=5, pady=10)

        # Content area
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Initial message
        self._show_welcome_message()

    def _show_welcome_message(self):
        """Show welcome message in content area."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        welcome_label = ctk.CTkLabel(
            self.content_frame,
            text="Click a button above to test JSON viewer components",
            font=ctk.CTkFont(size=14)
        )
        welcome_label.pack(expand=True)

    def _test_tabbed_viewer(self):
        """Test the tabbed JSON viewer."""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Create tabbed viewer
        tab_view = JsonViewerTabView(self.content_frame)
        tab_view.pack(fill="both", expand=True)

        # Load data
        tab_view.load_result(self.sample_data)

    def _test_individual_components(self):
        """Test individual components separately."""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Create test frames for each component
        main_container = ctk.CTkFrame(self.content_frame)
        main_container.pack(fill="both", expand=True)

        # Component selector
        selector_frame = ctk.CTkFrame(main_container)
        selector_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            selector_frame,
            text="Select Component:",
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left", padx=5)

        component_var = ctk.StringVar(value="tree")

        def show_component():
            choice = component_var.get()
            for widget in test_container.winfo_children():
                widget.destroy()

            if choice == "json":
                self._show_json_component(test_container)
            elif choice == "tree":
                self._show_tree_component(test_container)
            elif choice == "summary":
                self._show_summary_component(test_container)

        ctk.CTkRadioButton(
            selector_frame,
            text="JSON Syntax Highlight",
            variable=component_var,
            value="json",
            command=show_component
        ).pack(side="left", padx=10)

        ctk.CTkRadioButton(
            selector_frame,
            text="Tree View",
            variable=component_var,
            value="tree",
            command=show_component
        ).pack(side="left", padx=10)

        ctk.CTkRadioButton(
            selector_frame,
            text="Summary",
            variable=component_var,
            value="summary",
            command=show_component
        ).pack(side="left", padx=10)

        # Test container
        test_container = ctk.CTkFrame(main_container)
        test_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Show tree view by default
        self._show_tree_component(test_container)

    def _show_json_component(self, parent):
        """Show the JSON syntax highlight component.

        Args:
            parent: Parent widget
        """
        json_box = SyntaxHighlightedTextbox(parent)
        json_box.pack(fill="both", expand=True, padx=10, pady=10)
        json_box.display_json(self.sample_data.get('result', {}))

    def _show_tree_component(self, parent):
        """Show the tree view component.

        Args:
            parent: Parent widget
        """
        # Control frame
        control_frame = ctk.CTkFrame(parent)
        control_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            control_frame,
            text="Expand All",
            command=lambda: tree_view.expand_all(),
            width=100
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            control_frame,
            text="Collapse All",
            command=lambda: tree_view.collapse_all(),
            width=100
        ).pack(side="right", padx=5)

        # Tree view
        tree_view = TreeView(parent)
        tree_view.pack(fill="both", expand=True, padx=10, pady=10)

        structure = self.sample_data.get('result', {}).get('structure', [])
        tree_view.load_tree_structure(structure)

    def _show_summary_component(self, parent):
        """Show the summary view component.

        Args:
            parent: Parent widget
        """
        summary = SummaryView(parent)
        summary.pack(fill="both", expand=True, padx=10, pady=10)
        summary.load_data(self.sample_data)


def main():
    """Run the JSON viewer test application."""
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = JsonViewerTestApp()
    app.mainloop()


if __name__ == "__main__":
    main()
