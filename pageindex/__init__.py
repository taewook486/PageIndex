"""
PageIndex - Vectorless, reasoning-based RAG system.

This package provides tools for converting PDF and Markdown documents
into hierarchical tree structures using LLM-based reasoning.
"""

from .page_index import *  # noqa: F401, F403
from .page_index_md import md_to_tree  # noqa: F401
from .constants import EnvKeys, Defaults, ErrorMessages  # noqa: F401
from .models import PageIndexConfig  # noqa: F401

__version__ = "1.0.0"
__all__ = [
    # Core functions
    "page_index",
    "page_index_main",
    "md_to_tree",
    # Configuration
    "config",
    "PageIndexConfig",
    # Constants
    "EnvKeys",
    "Defaults",
    "ErrorMessages",
]