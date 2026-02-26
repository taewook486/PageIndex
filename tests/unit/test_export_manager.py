"""
Unit tests for ExportManager.

Tests M9.4: Export functionality.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from pageindex.gui.managers.export_manager import ExportManager


@pytest.fixture
def sample_result():
    """Create a sample processing result."""
    return {
        "file_path": "/path/to/document.pdf",
        "file_type": "pdf",
        "output_file": "/path/to/output.json",
        "success": True,
        "result": {
            "doc_name": "Test Document",
            "doc_description": "A test document for export",
            "structure": [
                {
                    "title": "Chapter 1",
                    "node_id": "ch1",
                    "start_index": "1",
                    "end_index": "10",
                    "nodes": [
                        {
                            "title": "Section 1.1",
                            "node_id": "ch1.1",
                            "start_index": "2",
                            "end_index": "5",
                            "nodes": []
                        }
                    ]
                },
                {
                    "title": "Chapter 2",
                    "node_id": "ch2",
                    "start_index": "11",
                    "end_index": "20",
                    "nodes": []
                }
            ]
        }
    }


@pytest.fixture
def export_manager():
    """Create an ExportManager."""
    return ExportManager()


class TestExportManager:
    """Test ExportManager class."""

    def test_export_to_markdown(self, export_manager, sample_result):
        """Test Markdown export."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            output_path = f.name

        try:
            result = export_manager.export_to_markdown(sample_result, output_path)

            assert result is True
            assert Path(output_path).exists()

            # Check content
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()

            assert "# PageIndex Processing Result" in content
            assert "Test Document" in content
            assert "Chapter 1" in content
            assert "[ch1]" in content
            assert "(pp. 1-10)" in content

        finally:
            Path(output_path).unlink()

    def test_export_to_html(self, export_manager, sample_result):
        """Test HTML export."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as f:
            output_path = f.name

        try:
            result = export_manager.export_to_html(sample_result, output_path)

            assert result is True
            assert Path(output_path).exists()

            # Check content
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()

            assert "<!DOCTYPE html>" in content
            assert "<title>PageIndex Result" in content
            assert "Test Document" in content
            assert "Chapter 1" in content

        finally:
            Path(output_path).unlink()

    def test_export_to_pdf(self, export_manager, sample_result):
        """Test PDF export."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pdf') as f:
            output_path = f.name

        try:
            # Mock fpdf.FPDF class
            with patch('fpdf.FPDF') as mock_fpdf_class:
                mock_pdf = MagicMock()
                mock_fpdf_class.return_value = mock_pdf

                result = export_manager.export_to_pdf(sample_result, output_path)

                assert result is True
                # Verify fpdf was called
                assert mock_pdf.add_page.called
                assert mock_pdf.output.called

        finally:
            Path(output_path).unlink()

    def test_export_without_metadata(self, export_manager, sample_result):
        """Test export without metadata."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            output_path = f.name

        try:
            result = export_manager.export_to_markdown(
                sample_result, output_path, include_metadata=False
            )

            assert result is True

            # Check content
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()

            assert "File Information" not in content
            assert "Test Document" in content

        finally:
            Path(output_path).unlink()
