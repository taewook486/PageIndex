"""
Data models for PageIndex.

This module defines Pydantic models for type-safe data structures
used throughout the PageIndex project.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


# =============================================================================
# Configuration Models
# =============================================================================
class PageIndexConfig(BaseModel):
    """Configuration for PageIndex processing."""

    model: str = Field(default="glm-5", description="AI model to use")
    toc_check_page_num: int = Field(default=20, ge=1, description="Number of pages to check for TOC")
    max_page_num_each_node: int = Field(default=10, ge=1, description="Maximum pages per node")
    max_token_num_each_node: int = Field(default=20000, ge=100, description="Maximum tokens per node")

    # Node options
    if_add_node_id: str = Field(default="yes", pattern="^(yes|no)$", description="Add node ID")
    if_add_node_summary: str = Field(default="yes", pattern="^(yes|no)$", description="Add node summary")
    if_add_node_text: str = Field(default="no", pattern="^(yes|no)$", description="Add node text")
    if_add_doc_description: str = Field(default="no", pattern="^(yes|no)$", description="Add document description")

    @field_validator("if_add_node_id", "if_add_node_summary", "if_add_node_text", "if_add_doc_description")
    @classmethod
    def validate_yes_no(cls, v: str) -> str:
        """Validate yes/no string values."""
        if v not in ("yes", "no"):
            raise ValueError('must be "yes" or "no"')
        return v

    @property
    def add_node_id(self) -> bool:
        """Convert yes/no string to boolean."""
        return self.if_add_node_id == "yes"

    @property
    def add_node_summary(self) -> bool:
        """Convert yes/no string to boolean."""
        return self.if_add_node_summary == "yes"

    @property
    def add_node_text(self) -> bool:
        """Convert yes/no string to boolean."""
        return self.if_add_node_text == "yes"

    @property
    def add_doc_description(self) -> bool:
        """Convert yes/no string to boolean."""
        return self.if_add_doc_description == "yes"


# =============================================================================
# TOC Models
# =============================================================================
class TocItem(BaseModel):
    """Table of Contents item."""

    structure: Optional[str] = Field(None, description="Structure index (e.g., '1.1.2')")
    title: str = Field(..., description="Section title")
    page: Optional[int] = Field(None, description="Page number from TOC")
    physical_index: Optional[int] = Field(None, description="Actual physical page index")
    start: Optional[str] = Field(None, description="Start marker ('yes' or 'no')")
    appear_start: Optional[str] = Field(None, description="Does section start at page beginning")


# =============================================================================
# Node Models
# =============================================================================
class Node(BaseModel):
    """Tree node representing a document section."""

    title: str = Field(..., description="Node title")
    node_id: Optional[str] = Field(None, description="Node ID (4-digit zero-padded)")
    start_index: Optional[int] = Field(None, description="Start page index")
    end_index: Optional[int] = Field(None, description="End page index")
    text: Optional[str] = Field(None, description="Node text content")
    summary: Optional[str] = Field(None, description="Node summary")
    prefix_summary: Optional[str] = Field(None, description="Prefix summary for parent nodes")
    nodes: List["Node"] = Field(default_factory=list, description="Child nodes")

    class Config:
        """Pydantic config."""

        # Allow forward references for recursive Node model
        arbitrary_types_allowed = True


# =============================================================================
# Document Models
# =============================================================================
class DocumentStructure(BaseModel):
    """Complete document structure output."""

    doc_name: str = Field(..., description="Document name")
    doc_description: Optional[str] = Field(None, description="Document description")
    structure: List[Node] = Field(default_factory=list, description="Document tree structure")


# =============================================================================
# Page Models
# =============================================================================
class PageInfo(BaseModel):
    """Information about a single page."""

    text: str = Field(..., description="Page text content")
    token_count: int = Field(..., ge=0, description="Number of tokens in page")


# =============================================================================
# Verification Models
# =============================================================================
class TitleCheckResult(BaseModel):
    """Result of title appearance check."""

    list_index: int = Field(..., description="Index in the list")
    answer: str = Field(..., pattern="^(yes|no)$", description="Whether title appears")
    title: str = Field(..., description="Section title")
    page_number: Optional[int] = Field(None, description="Page number")


class TocExtractionResult(BaseModel):
    """Result of TOC extraction."""

    toc_content: Optional[str] = Field(None, description="Extracted TOC content")
    toc_page_list: List[int] = Field(default_factory=list, description="Page indices containing TOC")
    page_index_given_in_toc: str = Field(..., pattern="^(yes|no)$", description="Whether page numbers in TOC")


# =============================================================================
# API Response Models
# =============================================================================
class LlmResponse(BaseModel):
    """Standard LLM API response."""

    content: str = Field(..., description="Response content")
    finish_reason: str = Field(..., description="Reason for finishing")


# =============================================================================
# Update forward references for recursive models
# =============================================================================
Node.model_rebuild()
