"""
Constants for PageIndex.

This module defines all constant values used across the PageIndex project,
including environment keys, default values, and configuration constants.
"""

import os
from typing import Final

# =============================================================================
# Environment Keys
# =============================================================================
class EnvKeys:
    """Environment variable names used in the application."""

    CHATGPT_API_KEY: Final[str] = "CHATGPT_API_KEY"
    OPENAI_BASE_URL: Final[str] = "OPENAI_BASE_URL"


# =============================================================================
# Default Values
# =============================================================================
class Defaults:
    """Default configuration values."""

    MODEL: Final[str] = "glm-5"
    MAX_RETRIES: Final[int] = 10
    RETRY_DELAY: Final[float] = 1.0  # seconds
    TEMPERATURE: Final[float] = 0.0

    # TOC Configuration
    TOC_CHECK_PAGE_NUM: Final[int] = 20
    MAX_PAGE_NUM_EACH_NODE: Final[int] = 10
    MAX_TOKEN_NUM_EACH_NODE: Final[int] = 20000

    # Node Configuration
    SUMMARY_TOKEN_THRESHOLD: Final[int] = 200
    THINNING_THRESHOLD: Final[int] = 5000

    # API Configuration
    MAX_TOKENS_DEFAULT: Final[int] = 110000
    ACCURACY_THRESHOLD: Final[float] = 0.6

    # Verification
    MAX_FIX_ATTEMPTS: Final[int] = 3
    MAX_CONTINUE_RETRIES: Final[int] = 5

    # Rate Limiting
    MAX_CONCURRENT_REQUESTS: Final[int] = 3  # Maximum concurrent API requests
    RATE_LIMIT_DELAY: Final[float] = 0.5  # Delay between requests in seconds


# =============================================================================
# Path Constants
# =============================================================================
class Paths:
    """File and directory path constants."""

    LOGS_DIR: Final[str] = "./logs"
    RESULTS_DIR: Final[str] = "./results"


# =============================================================================
# JSON Field Names
# =============================================================================
class JsonFields:
    """Common JSON field names used in the output."""

    NODE_ID: Final[str] = "node_id"
    TITLE: Final[str] = "title"
    STRUCTURE: Final[str] = "structure"
    START_INDEX: Final[str] = "start_index"
    END_INDEX: Final[str] = "end_index"
    PHYSICAL_INDEX: Final[str] = "physical_index"
    TEXT: Final[str] = "text"
    SUMMARY: Final[str] = "summary"
    PREFIX_SUMMARY: Final[str] = "prefix_summary"
    NODES: Final[str] = "nodes"
    DOC_NAME: Final[str] = "doc_name"
    DOC_DESCRIPTION: Final[str] = "doc_description"
    APPEAR_START: Final[str] = "appear_start"
    PAGE_NUMBER: Final[str] = "page_number"
    PAGE: Final[str] = "page"


# =============================================================================
# Error Messages
# =============================================================================
class ErrorMessages:
    """Standardized error messages."""

    API_KEY_MISSING: Final[str] = (
        f"{EnvKeys.CHATGPT_API_KEY} not set or using placeholder. "
        "Please set a valid API key in .env file."
    )
    INVALID_PDF_INPUT: Final[str] = (
        "Unsupported input type. Expected a PDF file path or BytesIO object."
    )
    CONFIG_UNKNOWN_KEYS: Final[str] = "Unknown config keys: {}"
    MAX_RETRIES_REACHED: Final[str] = "Max retries reached"
    FILE_NOT_FOUND: Final[str] = "File not found: {}"
    INVALID_EXTENSION: Final[str] = "File must have .{} extension"
    PROCESSING_FAILED: Final[str] = "Processing failed"


# =============================================================================
# API Response Patterns
# =============================================================================
class ApiPatterns:
    """Patterns for parsing API responses."""

    JSON_CODE_BLOCK_START: Final[str] = "```json"
    JSON_CODE_BLOCK_END: Final[str] = "```"
    PHYSICAL_INDEX_TAG: Final[str] = "<physical_index_{}>"
    PHYSICAL_INDEX_TAG_REGEX: Final[str] = r"<physical_index_(\d+)>"
