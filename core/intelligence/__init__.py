"""
XL Research Framework - Core Intelligence Module

Wrapper that re-exports from research/ package for unified imports.
Use: from core.intelligence import ResearchAdapter

This module provides backward compatibility with the new architecture.
"""

# Re-export from research package (canonical location)
from research.adapter import (
    ResearchAdapter,
    ResearchConfig,
    create_adapter,
    load_research_config,
)

__all__ = [
    'ResearchAdapter',
    'ResearchConfig',
    'create_adapter',
    'load_research_config',
]
