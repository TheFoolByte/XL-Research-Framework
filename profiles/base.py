"""
XL Research Framework v2.1 - Profile Base Class

Defines the interface for execution profiles.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Profile(ABC):
    """
    Base class for execution profiles.
    
    Profiles control:
    - Memory limits
    - Which modules to load
    - File type filters
    - Extraction depth
    - Research integration
    """
    
    # Profile metadata
    name: str = "base"
    description: str = "Base profile"
    
    # Memory settings (MB)
    memory_limit_mb: int = 4096
    cache_size_mb: int = 256
    
    # Module settings
    modules: List[str] = field(default_factory=list)
    
    # File settings
    file_types: List[str] = field(default_factory=list)
    max_files: Optional[int] = None
    max_file_size_mb: float = 10.0
    
    # Extraction settings
    decompile_level: str = "sources"  # manifest, sources, full
    
    # Timeout
    timeout_seconds: int = 300
    
    # Research settings
    research_enabled: bool = False
    research_settings: Dict[str, Any] = field(default_factory=dict)
    
    def should_include_file(self, extension: str) -> bool:
        """Check if file type should be included"""
        if not self.file_types or "*" in self.file_types:
            return True
        return extension.lower() in self.file_types
    
    def __str__(self) -> str:
        return f"{self.name} ({self.memory_limit_mb}MB, {len(self.modules)} modules)"

