"""
XL Research - Research Modules Package

Provides family code analysis, smart enumeration, validation testing,
decoy management, and endpoint discovery capabilities.
"""

from .analyzer import FamilyCodeAnalyzer
from .enumerator import SmartFamilyCodeEnumerator
from .validator import PackageValidator
from .decoy import DecoyManager

__all__ = [
    "analyzer", 
    "enumerator", 
    "validator", 
    "decoy",
    "discovery",
    "FamilyCodeAnalyzer",
    "SmartFamilyCodeEnumerator",
    "PackageValidator",
    "DecoyManager"
]
