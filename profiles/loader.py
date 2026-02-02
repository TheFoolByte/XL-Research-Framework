"""
XL Research Framework v2.1 - Profile Loader

Dynamic profile loading and management.
"""

from typing import Dict, Type, Optional
from .base import Profile
from .light import LightProfile
from .xl import XLProfile
from .full import FullProfile


class ProfileLoader:
    """
    Loads and manages execution profiles.
    
    Available profiles:
    - light: Quick scan, 2GB
    - xl: XL-focused, 4GB
    - full: Deep analysis, 6GB
    """
    
    # Registry of available profiles
    PROFILES: Dict[str, Type[Profile]] = {
        "light": LightProfile,
        "xl": XLProfile,
        "full": FullProfile,
    }
    
    @classmethod
    def load(cls, name: str) -> Profile:
        """
        Load a profile by name.
        
        Args:
            name: Profile name (light, xl, full)
            
        Returns:
            Profile instance
            
        Raises:
            ValueError if profile not found
        """
        if name not in cls.PROFILES:
            available = ", ".join(cls.PROFILES.keys())
            raise ValueError(f"Profile '{name}' not found. Available: {available}")
        
        return cls.PROFILES[name]()
    
    @classmethod
    def get(cls, name: str) -> Optional[Profile]:
        """
        Get profile by name (returns None if not found).
        
        Args:
            name: Profile name
            
        Returns:
            Profile instance or None
        """
        if name in cls.PROFILES:
            return cls.PROFILES[name]()
        return None
    
    @classmethod
    def list_all(cls) -> Dict[str, str]:
        """
        List all available profiles with descriptions.
        
        Returns:
            Dict of name -> description
        """
        return {
            name: cls.PROFILES[name]().description
            for name in cls.PROFILES
        }
    
    @classmethod
    def register(cls, name: str, profile_class: Type[Profile]):
        """
        Register a custom profile.
        
        Args:
            name: Profile name
            profile_class: Profile class
        """
        cls.PROFILES[name] = profile_class
