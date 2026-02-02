"""
XL Research Framework v2.1 - XL Profile

Balanced profile focused on XL ecosystem analysis.
Uses 4GB RAM, includes XL-specific family module.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from .base import Profile


@dataclass
class XLProfile(Profile):
    """
    XL-focused profile for MyXL/Axis research.
    
    Characteristics:
    - 4GB memory limit (comfortable on 8GB systems)
    - API, endpoint, and XL family analysis
    - 2000 file limit
    - Java source decompilation
    - Balanced execution (~3-5 min)
    """
    
    name: str = "xl"
    description: str = "XL ecosystem analysis (4GB)"
    
    # Memory: 4GB
    memory_limit_mb: int = 4096
    cache_size_mb: int = 256
    
    # Modules: XL-focused
    modules: List[str] = field(default_factory=lambda: [
        "api_scanner",
        "endpoint_finder",
        "family_logic",
        "env_extractor"
    ])
    
    # Files: code and config
    file_types: List[str] = field(default_factory=lambda: [
        ".java",
        ".kt",
        ".json",
        ".xml",
        ".properties"
    ])
    max_files: Optional[int] = 2000
    max_file_size_mb: float = 10.0
    
    # Extraction: Java sources
    decompile_level: str = "sources"
    
    # Balanced timeout
    timeout_seconds: int = 300
