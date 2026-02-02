"""
XL Research Framework v2.1 - Full Profile

Comprehensive analysis profile for deep research.
Uses 6GB RAM, all modules, no file limits.
Includes research integration.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .base import Profile


@dataclass
class FullProfile(Profile):
    """
    Full profile for comprehensive deep analysis.
    
    Characteristics:
    - 6GB memory limit (leaves 2GB for system on 8GB)
    - All analysis modules
    - No file limit
    - Full decompilation (sources + resources)
    - Extended execution (~5-15 min)
    - Research integration enabled
    """
    
    name: str = "full"
    description: str = "Comprehensive analysis (6GB)"
    
    # Memory: 6GB (max on 8GB system)
    memory_limit_mb: int = 6144
    cache_size_mb: int = 512
    
    # Modules: all
    modules: List[str] = field(default_factory=lambda: [
        "all"  # Loads all available modules
    ])
    
    # Files: no restrictions
    file_types: List[str] = field(default_factory=lambda: [
        "*"  # All file types
    ])
    max_files: Optional[int] = None  # Unlimited
    max_file_size_mb: float = 20.0
    
    # Extraction: full decompile
    decompile_level: str = "full"
    
    # Extended timeout
    timeout_seconds: int = 600
    
    # Research: enabled in full profile
    research_enabled: bool = True
    research_settings: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "config_path": "research_config.yaml",
        "analyzer_enabled": True,
        "enumerator_enabled": False,  # Off by default, can be slow
        "validator_enabled": True,
        "decoy_enabled": True,
    })

