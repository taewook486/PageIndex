"""
Export Manager for PageIndex GUI.

This module provides functionality to export results in various formats.
Implements M9.4 of SPEC-GUI-002.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class ExportManager:
    """Manages export of processing results to various formats."""

    def __init__(self):
        """Initialize the export manager."""
        pass

    def export_to_pdf(
        self,
        result: Dict[str, Any],
        output_path: str,
        include_metadata: bool = True
    ) -> bool:
        """Export result to PDF format.

        Args:
            result: Processing result dictionary
            output_path: Path for output PDF file
            include_metadata: Whether to include metadata

        Returns:
            True if export successful
        """
        try:
            from fpdf import FPDF

            pdf = FPDF()
            pdf.add_page()

            # Set up font
            # Note: FPDF needs a font that supports Unicode for non-ASCII characters
            # For simplicity, we'll use the default font
            pdf.set_font("Arial", size=12)

            # Title
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "PageIndex Processing Result", ln=True, align="C")
            pdf.ln(5)

            # Metadata
            if include_metadata:
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "File Information:", ln=True)

                pdf.set_font("Arial", size=11)
                pdf.cell(0, 7, f"File: {result.get('file_path', 'N/A')}", ln=True)
                pdf.cell(0, 7, f"Type: {result.get('file_type', 'N/A').upper()}", ln=True)
                pdf.cell(0, 7, f"Output: {result.get('output_file', 'N/A')}", ln=True)
                pdf.ln(5)

            # Structure
            structure = result.get('result', {})

            # Document name
            doc_name = structure.get('doc_name', 'N/A')
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, f"Document: {doc_name}", ln=True)
            pdf.ln(5)

            # Tree structure
            pdf.set_font("Arial", size=11)
            self._add_tree_to_pdf(pdf, structure.get('structure', []))

            # Output
            pdf.output(output_path)
            return True

        except ImportError:
            # fpdf not available
            raise Exception("PDF export requires fpdf library. Install with: pip install fpdf")
        except Exception as e:
            raise Exception(f"PDF export failed: {e}")

    def _add_tree_to_pdf(self, pdf, nodes, indent=0):
        """Add tree structure to PDF recursively.

        Args:
            pdf: FPDF instance
            nodes: List of node dictionaries
            indent: Current indentation level
        """
        for node in nodes:
            prefix = "  " * indent
            title = node.get('title', 'Untitled')
            node_id = node.get('node_id', '')
            start_idx = node.get('start_index', '')
            end_idx = node.get('end_index', '')

            # Build line
            line = f"{prefix}{title}"
            if node_id:
                line += f" [{node_id}]"
            if start_idx and end_idx:
                line += f" (pp. {start_idx}-{end_idx})"

            # Add to PDF (split if too long)
            if len(line) > 100:
                # Split long lines
                for i in range(0, len(line), 100):
                    pdf.cell(0, 7, line[i:i+100], ln=True)
            else:
                pdf.cell(0, 7, line, ln=True)

            # Recursively add children
            child_nodes = node.get('nodes', [])
            if child_nodes:
                self._add_tree_to_pdf(pdf, child_nodes, indent + 1)

    def export_to_html(
        self,
        result: Dict[str, Any],
        output_path: str,
        include_metadata: bool = True
    ) -> bool:
        """Export result to HTML format.

        Args:
            result: Processing result dictionary
            output_path: Path for output HTML file
            include_metadata: Whether to include metadata

        Returns:
            True if export successful
        """
        try:
            from jinja2 import Template

            template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PageIndex Result - {{ file_name }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
        }
        .metadata {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .metadata p {
            margin: 5px 0;
        }
        .tree {
            font-family: 'Consolas', 'Monaco', monospace;
        }
        .node {
            padding: 3px 0;
        }
        .node-title {
            font-weight: bold;
            color: #2980b9;
        }
        .node-id {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        .node-pages {
            color: #27ae60;
            font-size: 0.9em;
        }
        .indent {
            display: inline-block;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>PageIndex Processing Result</h1>

        {% if include_metadata %}
        <div class="metadata">
            <h2>File Information</h2>
            <p><strong>File:</strong> {{ result.file_path }}</p>
            <p><strong>Type:</strong> {{ result.file_type|upper }}</p>
            <p><strong>Output:</strong> {{ result.output_file }}</p>
        </div>
        {% endif %}

        <h2>Document Structure</h2>
        <div class="tree">
            <p><strong>{{ structure.doc_name }}</strong></p>
            {% if structure.doc_description %}
            <p>{{ structure.doc_description }}</p>
            {% endif %}
            <br>
            {{ tree_html }}
        </div>

        <div class="footer">
            Generated by PageIndex on {{ timestamp }}
        </div>
    </div>
</body>
</html>
            """

            # Render tree HTML
            tree_html = self._render_tree_html(result.get('result', {}).get('structure', []))

            # Get file name
            file_name = os.path.basename(result.get('file_path', 'result'))

            # Create template
            template = Template(template_str)

            # Render
            html = template.render(
                result=result,
                structure=result.get('result', {}),
                file_name=file_name,
                tree_html=tree_html,
                include_metadata=include_metadata,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)

            return True

        except ImportError:
            raise Exception("HTML export requires jinja2 library. Install with: pip install jinja2")
        except Exception as e:
            raise Exception(f"HTML export failed: {e}")

    def _render_tree_html(self, nodes, indent=0) -> str:
        """Render tree structure as HTML.

        Args:
            nodes: List of node dictionaries
            indent: Current indentation level

        Returns:
            HTML string
        """
        lines = []
        indent_str = "&nbsp;" * (indent * 4)

        for node in nodes:
            title = node.get('title', 'Untitled')
            node_id = node.get('node_id', '')
            start_idx = node.get('start_index', '')
            end_idx = node.get('end_index', '')

            # Build node HTML
            line = f'<div class="node">{indent_str}<span class="node-title">{title}</span>'

            if node_id:
                line += f' <span class="node-id">[{node_id}]</span>'

            if start_idx and end_idx:
                line += f' <span class="node-pages">(pp. {start_idx}-{end_idx})</span>'

            line += '</div>'
            lines.append(line)

            # Recursively add children
            child_nodes = node.get('nodes', [])
            if child_nodes:
                lines.append(self._render_tree_html(child_nodes, indent + 1))

        return '\n'.join(lines)

    def export_to_markdown(
        self,
        result: Dict[str, Any],
        output_path: str,
        include_metadata: bool = True
    ) -> bool:
        """Export result to Markdown format.

        Args:
            result: Processing result dictionary
            output_path: Path for output Markdown file
            include_metadata: Whether to include metadata

        Returns:
            True if export successful
        """
        try:
            lines = []

            # Title
            lines.append("# PageIndex Processing Result")
            lines.append("")

            # Metadata
            if include_metadata:
                lines.append("## File Information")
                lines.append("")
                lines.append(f"- **File:** {result.get('file_path', 'N/A')}")
                lines.append(f"- **Type:** {result.get('file_type', 'N/A').upper()}")
                lines.append(f"- **Output:** {result.get('output_file', 'N/A')}")
                lines.append("")

            # Structure
            structure = result.get('result', {})
            lines.append("## Document Structure")
            lines.append("")

            # Document name
            doc_name = structure.get('doc_name', 'N/A')
            lines.append(f"### {doc_name}")
            lines.append("")

            doc_description = structure.get('doc_description')
            if doc_description:
                lines.append(f"{doc_description}")
                lines.append("")

            # Tree structure
            tree_md = self._render_tree_markdown(structure.get('structure', []))
            lines.append(tree_md)

            # Footer
            lines.append("")
            lines.append("---")
            lines.append(f"*Generated by PageIndex on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            return True

        except Exception as e:
            raise Exception(f"Markdown export failed: {e}")

    def _render_tree_markdown(self, nodes, indent=0) -> str:
        """Render tree structure as Markdown.

        Args:
            nodes: List of node dictionaries
            indent: Current indentation level

        Returns:
            Markdown string
        """
        lines = []
        indent_str = "  " * indent

        for node in nodes:
            title = node.get('title', 'Untitled')
            node_id = node.get('node_id', '')
            start_idx = node.get('start_index', '')
            end_idx = node.get('end_index', '')

            # Build line
            line = f"{indent_str}- **{title}**"

            if node_id:
                line += f" `[{node_id}]`"

            if start_idx and end_idx:
                line += f" (pp. {start_idx}-{end_idx})"

            lines.append(line)

            # Recursively add children
            child_nodes = node.get('nodes', [])
            if child_nodes:
                lines.append(self._render_tree_markdown(child_nodes, indent + 1))

        return '\n'.join(lines)
