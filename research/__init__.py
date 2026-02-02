"""
XL Research - Research Module Package

Provides API research capabilities integrated with the main framework.
Uses lazy loading to minimize memory footprint when disabled.
"""

__version__ = "1.0.0"

# Lazy imports - only load when accessed
def __getattr__(name):
    if name == "ResearchAdapter":
        from .adapter import ResearchAdapter
        return ResearchAdapter
    elif name == "create_adapter":
        from .adapter import create_adapter
        return create_adapter
    elif name == "ResearchConfig":
        from .adapter import ResearchConfig
        return ResearchConfig
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["ResearchAdapter", "create_adapter", "ResearchConfig"]
