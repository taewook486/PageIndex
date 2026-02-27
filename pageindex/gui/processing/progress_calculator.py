"""
Progress Calculator for processing stages.

This module calculates progress percentages based on processing stages
for PDF and Markdown document processing.

@MX:SPEC: SPEC-GUI-003 - REQ-2, REQ-4
"""

from typing import Literal


class ProgressCalculator:
    """Calculate progress percentages for processing stages.

    Provides progress calculation for both PDF and Markdown processing
    with defined stage ranges for granular progress updates.

    Stage Ranges for PDF:
        - Loading PDF: 0-10%
        - Page processing: 10-60%
        - Text extraction: 60-80%
        - Structure analysis: 80-95%
        - AI inference: 95-100%

    Stage Ranges for Markdown:
        - File parsing: 0-30%
        - Section analysis: 30-70%
        - Tree construction: 70-95%
        - AI inference: 95-100%

    @MX:NOTE: Progress percentages are mapped to specific processing
    stages to provide meaningful feedback to users.
    """

    # PDF stage ranges
    PDF_LOADING_START = 0
    PDF_LOADING_END = 10
    PDF_PAGE_START = 10
    PDF_PAGE_END = 60
    PDF_TEXT_START = 60
    PDF_TEXT_END = 80
    PDF_STRUCTURE_START = 80
    PDF_STRUCTURE_END = 95
    PDF_AI_START = 95
    PDF_AI_END = 100

    # Markdown stage ranges
    MD_PARSING_START = 0
    MD_PARSING_END = 30
    MD_SECTION_START = 30
    MD_SECTION_END = 70
    MD_TREE_START = 70
    MD_TREE_END = 95
    MD_AI_START = 95
    MD_AI_END = 100

    # Stage name types
    PDFStage = Literal[
        "loading",
        "page_processing",
        "text_extraction",
        "structure_analysis",
        "ai_inference"
    ]

    MarkdownStage = Literal[
        "parsing",
        "section_analysis",
        "tree_construction",
        "ai_inference"
    ]

    def calculate_pdf_progress(
        self,
        stage: PDFStage,
        current: float,
        total: float
    ) -> int:
        """Calculate progress for PDF processing stage.

        Args:
            stage: Current processing stage name.
            current: Current progress within stage (e.g., page number).
            total: Total items in stage (e.g., total pages).

        Returns:
            Progress percentage (0-100).
        """
        if total <= 0:
            total = 1

        ratio = max(0, min(current / total, 1.0))

        if stage == "loading":
            start, end = self.PDF_LOADING_START, self.PDF_LOADING_END
        elif stage == "page_processing":
            start, end = self.PDF_PAGE_START, self.PDF_PAGE_END
        elif stage == "text_extraction":
            start, end = self.PDF_TEXT_START, self.PDF_TEXT_END
        elif stage == "structure_analysis":
            start, end = self.PDF_STRUCTURE_START, self.PDF_STRUCTURE_END
        elif stage == "ai_inference":
            start, end = self.PDF_AI_START, self.PDF_AI_END
        else:
            # Unknown stage, return 0
            return 0

        progress = start + (end - start) * ratio
        return int(max(0, min(progress, 100)))

    def calculate_markdown_progress(
        self,
        stage: MarkdownStage,
        current: float,
        total: float
    ) -> int:
        """Calculate progress for Markdown processing stage.

        Args:
            stage: Current processing stage name.
            current: Current progress within stage.
            total: Total items in stage.

        Returns:
            Progress percentage (0-100).
        """
        if total <= 0:
            total = 1

        ratio = max(0, min(current / total, 1.0))

        if stage == "parsing":
            start, end = self.MD_PARSING_START, self.MD_PARSING_END
        elif stage == "section_analysis":
            start, end = self.MD_SECTION_START, self.MD_SECTION_END
        elif stage == "tree_construction":
            start, end = self.MD_TREE_START, self.MD_TREE_END
        elif stage == "ai_inference":
            start, end = self.MD_AI_START, self.MD_AI_END
        else:
            # Unknown stage, return 0
            return 0

        progress = start + (end - start) * ratio
        return int(max(0, min(progress, 100)))
