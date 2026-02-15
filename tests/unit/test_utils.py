"""
Unit tests for utility functions.

Tests for token counting, JSON extraction, and other utility functions.
"""

import pytest

from pageindex.utils import count_tokens, extract_json, get_api_rate_limiter, RateLimiter
from pageindex.constants import JsonFields, ApiPatterns, Defaults


class TestCountTokens:
    """Test token counting functionality."""

    def test_count_tokens_with_empty_text(self):
        """Test that empty text returns 0 tokens."""
        assert count_tokens("") == 0

    def test_count_tokens_with_whitespace_only(self):
        """Test that whitespace-only text returns 0 tokens."""
        assert count_tokens("   \n\t  ") == 0

    def test_count_tokens_with_simple_text(self):
        """Test token counting with simple English text."""
        result = count_tokens("Hello world")
        # Token count may vary slightly, but should be positive
        assert result > 0

    def test_count_tokens_with_longer_text(self):
        """Test token counting with longer text."""
        text = "This is a longer text with multiple sentences."
        result = count_tokens(text)
        assert result > 5  # Should have multiple tokens

    def test_count_tokens_with_specific_model(self):
        """Test token counting with a specific model."""
        result = count_tokens("Hello world", model="gpt-4")
        assert result > 0


class TestExtractJson:
    """Test JSON extraction functionality."""

    def test_extract_json_plain(self):
        """Test extraction of plain JSON."""
        result = extract_json('{"key": "value"}')
        assert result == {"key": "value"}

    def test_extract_json_with_code_block(self):
        """Test extraction from JSON code block."""
        result = extract_json('```json\n{"key": "value"}\n```')
        assert result == {"key": "value"}

    def test_extract_json_with_whitespace(self):
        """Test extraction with extra whitespace."""
        result = extract_json('  {  "key"  :  "value"  }  ')
        assert result == {"key": "value"}

    def test_extract_json_with_newlines(self):
        """Test extraction with newlines in JSON."""
        result = extract_json('{"key":\n"value"}')
        assert result == {"key": "value"}

    def test_extract_json_python_none_to_null(self):
        """Test conversion of Python None to JSON null."""
        result = extract_json('{"key": None}')
        assert result == {"key": None}

    def test_extract_json_with_trailing_comma(self):
        """Test handling of trailing commas."""
        result = extract_json('{"key": "value",}')
        assert result == {"key": "value"}

    def test_extract_json_array_with_trailing_comma(self):
        """Test handling of trailing commas in arrays."""
        result = extract_json('{"items": [1, 2, 3,]}')
        assert result == {"items": [1, 2, 3]}

    def test_extract_json_invalid(self):
        """Test that invalid JSON returns empty dict."""
        result = extract_json('not valid json')
        assert result == {}

    def test_extract_json_nested_structure(self):
        """Test extraction of nested JSON structures."""
        result = extract_json('{"outer": {"inner": "value"}}')
        assert result == {"outer": {"inner": "value"}}


class TestConstants:
    """Test that constants are properly defined."""

    def test_json_fields_defined(self):
        """Test that JSON field constants are defined."""
        assert hasattr(JsonFields, 'NODE_ID')
        assert hasattr(JsonFields, 'TITLE')
        assert hasattr(JsonFields, 'STRUCTURE')

    def test_api_patterns_defined(self):
        """Test that API pattern constants are defined."""
        assert hasattr(ApiPatterns, 'JSON_CODE_BLOCK_START')
        assert hasattr(ApiPatterns, 'JSON_CODE_BLOCK_END')

    def test_constant_values(self):
        """Test that constant values are correct."""
        assert JsonFields.NODE_ID == "node_id"
        assert JsonFields.TITLE == "title"
        assert ApiPatterns.JSON_CODE_BLOCK_START == "```json"
        assert ApiPatterns.JSON_CODE_BLOCK_END == "```"


class TestRateLimiter:
    """Test rate limiting functionality."""

    def test_get_api_rate_limiter_singleton(self):
        """Test that get_api_rate_limiter returns singleton instance."""
        limiter1 = get_api_rate_limiter()
        limiter2 = get_api_rate_limiter()
        assert limiter1 is limiter2

    def test_rate_limiter_initialization(self):
        """Test that rate limiter initializes with correct defaults."""
        limiter = RateLimiter(max_concurrent=3, delay=0.5)
        assert limiter is not None
        assert limiter._semaphore._value == 3
        assert limiter._delay == 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
