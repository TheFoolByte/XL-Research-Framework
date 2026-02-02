"""
XL Research Framework v2.1 - Light Profile

Minimal memory footprint for quick scanning on 8GB systems.
Uses only 2GB RAM, focuses on API and endpoint detection.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from .base import Profile


@dataclass
class LightProfile(Profile):
    """
    Light profile for quick, low-memory scanning.
    
    Characteristics:
    - 2GB memory limit (safe for 8GB systems)
    - Only API and endpoint analysis
    - 500 file limit
    - Manifest-only extraction
    - Fast execution (~1-2 min)
    """
    
    name: str = "light"
    description: str = "Quick scan, minimal memory (2GB)"
    
    # Memory: 2GB
    memory_limit_mb: int = 2048
    cache_size_mb: int = 128
    
    # Modules: only essential
    modules: List[str] = field(default_factory=lambda: [
        "api_scanner",
        "endpoint_finder"
    ])
    
    # Files: limited set
    file_types: List[str] = field(default_factory=lambda: [
        ".json",
        ".xml", 
        ".properties"
    ])
    max_files: Optional[int] = 500
    max_file_size_mb: float = 5.0
    
    # Extraction: manifest only (fastest)
    decompile_level: str = "manifest"
    
    # Fast timeout
    timeout_seconds: int = 120
