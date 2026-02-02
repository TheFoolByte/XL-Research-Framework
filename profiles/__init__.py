"""
XL Research Framework v2.1 - Profiles Package

Execution profiles that control memory, modules, and extraction behavior.
"""

from .base import Profile
from .loader import ProfileLoader
from .light import LightProfile
from .xl import XLProfile
from .full import FullProfile

__all__ = [
    "Profile",
    "ProfileLoader",
    "LightProfile",
    "XLProfile", 
    "FullProfile",
]
