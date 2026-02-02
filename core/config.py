"""
XL Research Framework v2 - Configuration Management

Handles YAML-based configuration with sensible defaults.
Memory-efficient and profile-aware.
"""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


# Default paths
ROOT_DIR = Path(__file__).parent.parent
CONFIG_FILE = ROOT_DIR / "config.yaml"
PROFILES_FILE = ROOT_DIR / "profiles.yaml"


@dataclass
class AnalyzerConfig:
    """Configuration for individual analyzers"""
    enabled: bool = True
    priority: int = 50
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProfileConfig:
    """Execution profile configuration"""
    name: str = "standard"
    description: str = ""
    max_memory_mb: int = 1024
    max_files: Optional[int] = 5000
    file_types: List[str] = field(default_factory=lambda: [".java", ".kt", ".xml", ".json"])
    analyzers: List[str] = field(default_factory=lambda: ["api", "endpoint", "auth", "config"])
    timeout_seconds: int = 300


@dataclass
class OutputConfig:
    """Output configuration"""
    directory: str = "output"
    reports_dir: str = "output/reports"
    format: str = "text"  # text, json, html
    verbose: bool = False


class Config:
    """
    Central configuration manager for XL Research Framework.
    
    Loads from YAML files with sensible defaults.
    Supports profile-based configuration.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._config: Dict[str, Any] = {}
        self._profiles: Dict[str, ProfileConfig] = {}
        self._current_profile: Optional[ProfileConfig] = None
        self.output = OutputConfig()
        
        self._load_defaults()
        self._load_config()
        self._load_profiles()
    
    def _load_defaults(self):
        """Load default configuration"""
        self._config = {
            "framework": {
                "name": "XL Research Framework",
                "version": "2.0.0",
            },
            "jadx": {
                "path": r"C:\Users\Hype AMD\OneDrive\Desktop\jadx-1.5.3\bin\jadx.bat",
                "timeout": 600,
            },
            "output": {
                "directory": "output",
                "reports_dir": "output/reports",
                "format": "text",
            },
            "memory": {
                "max_mb": 1024,
                "gc_threshold": 0.8,
            }
        }
    
    def _load_config(self):
        """Load configuration from YAML file"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f) or {}
                self._deep_merge(self._config, user_config)
            except Exception as e:
                print(f"[!] Warning: Could not load config: {e}")
    
    def _load_profiles(self):
        """Load execution profiles from YAML"""
        # Default profiles
        self._profiles = {
            "quick": ProfileConfig(
                name="quick",
                description="Fast scan, minimal memory usage",
                max_memory_mb=512,
                max_files=1000,
                file_types=[".json", ".xml"],
                analyzers=["api", "endpoint"],
                timeout_seconds=120
            ),
            "standard": ProfileConfig(
                name="standard",
                description="Balanced analysis for most use cases",
                max_memory_mb=1024,
                max_files=5000,
                file_types=[".java", ".kt", ".xml", ".json", ".properties"],
                analyzers=["api", "endpoint", "auth", "config"],
                timeout_seconds=300
            ),
            "deep": ProfileConfig(
                name="deep",
                description="Full research mode - comprehensive analysis",
                max_memory_mb=2048,
                max_files=None,
                file_types=["*"],
                analyzers=["api", "endpoint", "auth", "family", "config"],
                timeout_seconds=600
            ),
        }
        
        # Load custom profiles
        if PROFILES_FILE.exists():
            try:
                with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
                    custom = yaml.safe_load(f) or {}
                
                for name, data in custom.get("profiles", {}).items():
                    self._profiles[name] = ProfileConfig(
                        name=name,
                        description=data.get("description", ""),
                        max_memory_mb=data.get("max_memory_mb", 1024),
                        max_files=data.get("max_files"),
                        file_types=data.get("file_types", []),
                        analyzers=data.get("analyzers", []),
                        timeout_seconds=data.get("timeout_seconds", 300)
                    )
            except Exception as e:
                print(f"[!] Warning: Could not load profiles: {e}")
    
    def _deep_merge(self, base: dict, override: dict):
        """Deep merge override into base dict"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'jadx.path')"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set_profile(self, name: str) -> bool:
        """Set the active execution profile"""
        if name in self._profiles:
            self._current_profile = self._profiles[name]
            return True
        return False
    
    @property
    def profile(self) -> ProfileConfig:
        """Get current profile (defaults to standard)"""
        if self._current_profile is None:
            self._current_profile = self._profiles["standard"]
        return self._current_profile
    
    def get_profile(self, name: str) -> Optional[ProfileConfig]:
        """Get a specific profile by name"""
        return self._profiles.get(name)
    
    def list_profiles(self) -> List[str]:
        """List available profile names"""
        return list(self._profiles.keys())
    
    @property
    def jadx_path(self) -> str:
        """Get JADX executable path"""
        return self.get("jadx.path", "jadx")
    
    @property
    def output_dir(self) -> Path:
        """Get output directory path"""
        return ROOT_DIR / self.get("output.directory", "output")
    
    @property
    def reports_dir(self) -> Path:
        """Get reports directory path"""
        return ROOT_DIR / self.get("output.reports_dir", "output/reports")
    
    def ensure_dirs(self):
        """Create necessary output directories"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)


# Singleton instance
config = Config()
