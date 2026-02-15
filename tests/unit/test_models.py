"""
Unit tests for data models.

Tests for Pydantic models used throughout PageIndex.
"""

import pytest
from pydantic import ValidationError

from pageindex.models import (
    PageIndexConfig,
    TocItem,
    Node,
    DocumentStructure,
    PageInfo,
    TitleCheckResult,
)


class TestPageIndexConfig:
    """Test PageIndexConfig model."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        config = PageIndexConfig()
        assert config.model == "glm-5"
        assert config.toc_check_page_num == 20
        assert config.max_page_num_each_node == 10
        assert config.max_token_num_each_node == 20000

    def test_boolean_properties(self):
        """Test boolean property conversion from yes/no strings."""
        config = PageIndexConfig(
            if_add_node_id="yes",
            if_add_node_summary="no",
            if_add_node_text="yes",
            if_add_doc_description="no"
        )
        assert config.add_node_id is True
        assert config.add_node_summary is False
        assert config.add_node_text is True
        assert config.add_doc_description is False

    def test_invalid_yes_no_value(self):
        """Test that invalid yes/no values raise ValidationError."""
        with pytest.raises(ValidationError):
            PageIndexConfig(if_add_node_id="maybe")

    def test_negative_toc_check_page_num(self):
        """Test that negative toc_check_page_num raises ValidationError."""
        with pytest.raises(ValidationError):
            PageIndexConfig(toc_check_page_num=-1)

    def test_zero_toc_check_page_num(self):
        """Test that zero toc_check_page_num raises ValidationError."""
        with pytest.raises(ValidationError):
            PageIndexConfig(toc_check_page_num=0)

    def test_custom_values(self):
        """Test setting custom configuration values."""
        config = PageIndexConfig(
            model="gpt-4",
            toc_check_page_num=50,
            max_page_num_each_node=20
        )
        assert config.model == "gpt-4"
        assert config.toc_check_page_num == 50
        assert config.max_page_num_each_node == 20


class TestTocItem:
    """Test TocItem model."""

    def test_minimal_item(self):
        """Test creating a minimal TOC item."""
        item = TocItem(title="Chapter 1")
        assert item.title == "Chapter 1"
        assert item.structure is None
        assert item.page is None

    def test_full_item(self):
        """Test creating a fully specified TOC item."""
        item = TocItem(
            structure="1.1",
            title="Introduction",
            page=10,
            physical_index=12
        )
        assert item.structure == "1.1"
        assert item.title == "Introduction"
        assert item.page == 10
        assert item.physical_index == 12


class TestNode:
    """Test Node model."""

    def test_leaf_node(self):
        """Test creating a leaf node (no children)."""
        node = Node(
            title="Section 1",
            node_id="0001"
        )
        assert node.title == "Section 1"
        assert node.node_id == "0001"
        assert node.nodes == []

    def test_node_with_children(self):
        """Test creating a node with child nodes."""
        child = Node(title="Child 1")
        parent = Node(
            title="Parent",
            nodes=[child]
        )
        assert len(parent.nodes) == 1
        assert parent.nodes[0].title == "Child 1"

    def test_nested_structure(self):
        """Test creating nested node structure."""
        grandchild = Node(title="Grandchild")
        child = Node(title="Child", nodes=[grandchild])
        parent = Node(title="Parent", nodes=[child])
        assert parent.nodes[0].nodes[0].title == "Grandchild"


class TestDocumentStructure:
    """Test DocumentStructure model."""

    def test_minimal_structure(self):
        """Test creating minimal document structure."""
        doc = DocumentStructure(doc_name="example.pdf")
        assert doc.doc_name == "example.pdf"
        assert doc.doc_description is None
        assert doc.structure == []

    def test_full_structure(self):
        """Test creating full document structure."""
        node = Node(title="Chapter 1")
        doc = DocumentStructure(
            doc_name="example.pdf",
            doc_description="An example document",
            structure=[node]
        )
        assert doc.doc_name == "example.pdf"
        assert doc.doc_description == "An example document"
        assert len(doc.structure) == 1


class TestPageInfo:
    """Test PageInfo model."""

    def test_page_info(self):
        """Test creating page info."""
        page = PageInfo(
            text="This is page content",
            token_count=100
        )
        assert page.text == "This is page content"
        assert page.token_count == 100

    def test_negative_token_count(self):
        """Test that negative token count raises ValidationError."""
        with pytest.raises(ValidationError):
            PageInfo(text="content", token_count=-1)


class TestTitleCheckResult:
    """Test TitleCheckResult model."""

    def test_check_result(self):
        """Test creating title check result."""
        result = TitleCheckResult(
            list_index=0,
            answer="yes",
            title="Chapter 1",
            page_number=5
        )
        assert result.list_index == 0
        assert result.answer == "yes"
        assert result.title == "Chapter 1"
        assert result.page_number == 5

    def test_invalid_answer(self):
        """Test that invalid answer value raises ValidationError."""
        with pytest.raises(ValidationError):
            TitleCheckResult(
                list_index=0,
                answer="maybe",
                title="Chapter 1"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
