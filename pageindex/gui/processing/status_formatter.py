"""
Status Message Formatter for processing stages.

This module provides formatted status messages for each processing stage
to give users meaningful feedback about processing progress.

@MX:SPEC: SPEC-GUI-003 - REQ-4
"""

from typing import Literal, Optional


class StatusMessageFormatter:
    """Format status messages for processing stages.

    Provides localized, meaningful status messages for PDF and Markdown
    processing stages.

    @MX:NOTE: Messages are designed to be informative and indicate
    current progress context (e.g., page numbers, section counts).
    """

    # Status templates for PDF processing
    PDF_MESSAGES = {
        "loading": "Loading PDF file...",
        "page_processing": "Processing page {current}/{total}...",
        "text_extraction": "Extracting text ({percent}%)...",
        "structure_analysis": "Analyzing structure (section {current}/{total})...",
        "ai_inference": "AI inference ({current}/{total} completed)...",
        "complete": "Processing complete!",
        "cancelled": "Processing cancelled by user",
        "error": "Error: {error}",
    }

    # Status templates for Markdown processing
    MARKDOWN_MESSAGES = {
        "parsing": "Parsing Markdown ({percent}%)...",
        "section_analysis": "Analyzing section {current}/{total}...",
        "tree_construction": "Building tree structure ({percent}%)...",
        "ai_inference": "AI inference ({current}/{total} completed)...",
        "complete": "Processing complete!",
        "cancelled": "Processing cancelled by user",
        "error": "Error: {error}",
    }

    # Generic stage type
    Stage = Literal[
        "loading",
        "page_processing",
        "text_extraction",
        "structure_analysis",
        "parsing",
        "section_analysis",
        "tree_construction",
        "ai_inference",
        "complete",
        "cancelled",
        "error"
    ]

    def format_pdf_status(
        self,
        stage: str,
        current: Optional[float] = None,
        total: Optional[float] = None,
        progress_percent: Optional[float] = None,
        error: Optional[str] = None
    ) -> str:
        """Format status message for PDF processing.

        Args:
            stage: Current processing stage.
            current: Current item number (e.g., page number).
            total: Total items (e.g., total pages).
            progress_percent: Progress percentage for percentage-based stages.
            error: Error message for error stage.

        Returns:
            Formatted status message.
        """
        template = self.PDF_MESSAGES.get(stage, "Processing...")

        return self._format_template(
            template,
            current=current,
            total=total,
            progress_percent=progress_percent,
            error=error
        )

    def format_markdown_status(
        self,
        stage: str,
        current: Optional[float] = None,
        total: Optional[float] = None,
        progress_percent: Optional[float] = None,
        error: Optional[str] = None
    ) -> str:
        """Format status message for Markdown processing.

        Args:
            stage: Current processing stage.
            current: Current item number.
            total: Total items.
            progress_percent: Progress percentage.
            error: Error message for error stage.

        Returns:
            Formatted status message.
        """
        template = self.MARKDOWN_MESSAGES.get(stage, "Processing...")

        return self._format_template(
            template,
            current=current,
            total=total,
            progress_percent=progress_percent,
            error=error
        )

    def format_status(
        self,
        stage: str,
        current: Optional[float] = None,
        total: Optional[float] = None,
        progress_percent: Optional[float] = None,
        error: Optional[str] = None
    ) -> str:
        """Format generic status message.

        Works for both PDF and Markdown stages.

        Args:
            stage: Current processing stage.
            current: Current item number.
            total: Total items.
            progress_percent: Progress percentage.
            error: Error message for error stage.

        Returns:
            Formatted status message.
        """
        # Try PDF first, then Markdown
        template = self.PDF_MESSAGES.get(stage) or self.MARKDOWN_MESSAGES.get(stage, "Processing...")

        return self._format_template(
            template,
            current=current,
            total=total,
            progress_percent=progress_percent,
            error=error
        )

    def format_cancelled(self) -> str:
        """Format cancellation message.

        Returns:
            Cancellation status message.
        """
        return self.PDF_MESSAGES["cancelled"]

    def format_complete(self) -> str:
        """Format completion message.

        Returns:
            Completion status message.
        """
        return self.PDF_MESSAGES["complete"]

    def format_error(self, error: str) -> str:
        """Format error message.

        Args:
            error: Error description.

        Returns:
            Error status message.
        """
        return self._format_template(self.PDF_MESSAGES["error"], error=error)

    def _format_template(
        self,
        template: str,
        current: Optional[float] = None,
        total: Optional[float] = None,
        progress_percent: Optional[float] = None,
        error: Optional[str] = None
    ) -> str:
        """Format a template with provided values.

        Args:
            template: Message template with placeholders.
            current: Current item number.
            total: Total items.
            progress_percent: Progress percentage.
            error: Error message.

        Returns:
            Formatted message.
        """
        result = template

        if current is not None:
            result = result.replace("{current}", str(int(current)))

        if total is not None:
            result = result.replace("{total}", str(int(total)))

        if progress_percent is not None:
            result = result.replace("{percent}", str(int(progress_percent)))

        if error is not None:
            result = result.replace("{error}", error)

        return result
