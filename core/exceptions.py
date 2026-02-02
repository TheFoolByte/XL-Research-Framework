"""
XL Research Framework - Custom Exceptions

Provides a comprehensive exception hierarchy for error handling
across the framework with detailed error context and logging support.
"""

from typing import Optional, Dict, Any
from pathlib import Path


class XLResearchError(Exception):
    """
    Base exception for all XL Research Framework errors.
    
    Provides:
    - Error context storage
    - Logging integration
    - Traceback enhancement
    """
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        self.message = message
        self.context = context or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.context:
            ctx_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} [{ctx_str}]"
        return self.message


# ==================== Configuration Errors ====================

class ConfigurationError(XLResearchError):
    """Configuration file or settings error"""
    pass


class ProfileNotFoundError(ConfigurationError):
    """Requested profile does not exist"""
    
    def __init__(self, profile_name: str):
        super().__init__(
            f"Profile not found: {profile_name}",
            {"profile": profile_name}
        )


class InvalidConfigError(ConfigurationError):
    """Invalid configuration format or values"""
    pass


# ==================== Module Errors ====================

class ModuleError(XLResearchError):
    """Base error for module operations"""
    pass


class ModuleNotFoundError(ModuleError):
    """Requested module does not exist"""
    
    def __init__(self, module_name: str):
        super().__init__(
            f"Module not found: {module_name}",
            {"module": module_name}
        )


class ModuleLoadError(ModuleError):
    """Failed to load a module"""
    
    def __init__(self, module_name: str, reason: str):
        super().__init__(
            f"Failed to load module '{module_name}': {reason}",
            {"module": module_name, "reason": reason}
        )


class ModuleExecutionError(ModuleError):
    """Module execution failed"""
    
    def __init__(self, module_name: str, reason: str):
        super().__init__(
            f"Module '{module_name}' execution failed: {reason}",
            {"module": module_name, "reason": reason}
        )


# ==================== Analysis Errors ====================

class AnalysisError(XLResearchError):
    """Base error for analysis operations"""
    pass


class APKNotFoundError(AnalysisError):
    """APK file not found"""
    
    def __init__(self, apk_path: str):
        super().__init__(
            f"APK not found: {apk_path}",
            {"path": apk_path}
        )


class ExtractionError(AnalysisError):
    """APK extraction failed"""
    
    def __init__(self, apk_path: str, reason: str):
        super().__init__(
            f"Failed to extract APK: {reason}",
            {"path": apk_path, "reason": reason}
        )


class ContextInitError(AnalysisError):
    """Failed to initialize analysis context"""
    pass


# ==================== Memory Errors ====================

class MemoryError(XLResearchError):
    """Memory management error"""
    pass


class MemoryLimitExceeded(MemoryError):
    """Memory usage exceeded configured limit"""
    
    def __init__(self, current_mb: float, limit_mb: float):
        super().__init__(
            f"Memory limit exceeded: {current_mb:.1f}MB > {limit_mb:.1f}MB",
            {"current_mb": current_mb, "limit_mb": limit_mb}
        )


# ==================== Research Errors ====================

class ResearchError(XLResearchError):
    """Base error for research operations"""
    pass


class ResearchConfigError(ResearchError):
    """Research configuration error"""
    pass


class APIConnectionError(ResearchError):
    """Failed to connect to research API"""
    
    def __init__(self, endpoint: str, reason: str):
        super().__init__(
            f"API connection failed to {endpoint}: {reason}",
            {"endpoint": endpoint, "reason": reason}
        )


class AuthenticationError(ResearchError):
    """Authentication failed"""
    pass


class RateLimitError(ResearchError):
    """Rate limit exceeded"""
    
    def __init__(self, wait_seconds: int = 60):
        super().__init__(
            f"Rate limit exceeded, wait {wait_seconds}s",
            {"wait_seconds": wait_seconds}
        )


# ==================== File Errors ====================

class FileError(XLResearchError):
    """File operation error"""
    pass


class FileReadError(FileError):
    """Failed to read file"""
    
    def __init__(self, file_path: str, reason: str):
        super().__init__(
            f"Failed to read file: {reason}",
            {"path": file_path, "reason": reason}
        )


class FileWriteError(FileError):
    """Failed to write file"""
    
    def __init__(self, file_path: str, reason: str):
        super().__init__(
            f"Failed to write file: {reason}",
            {"path": file_path, "reason": reason}
        )


# ==================== Timeout Errors ====================

class TimeoutError(XLResearchError):
    """Operation timed out"""
    
    def __init__(self, operation: str, timeout_seconds: int):
        super().__init__(
            f"Operation '{operation}' timed out after {timeout_seconds}s",
            {"operation": operation, "timeout": timeout_seconds}
        )


# ==================== Validation Errors ====================

class ValidationError(XLResearchError):
    """Input validation failed"""
    pass


class InvalidInputError(ValidationError):
    """Invalid input provided"""
    pass


class InvalidFamilyCodeError(ValidationError):
    """Invalid family code format"""
    
    def __init__(self, code: str):
        super().__init__(
            f"Invalid family code format: {code}",
            {"code": code}
        )


# ==================== Export for convenience ====================

__all__ = [
    "XLResearchError",
    "ConfigurationError",
    "ProfileNotFoundError",
    "InvalidConfigError",
    "ModuleError",
    "ModuleNotFoundError",
    "ModuleLoadError",
    "ModuleExecutionError",
    "AnalysisError",
    "APKNotFoundError",
    "ExtractionError",
    "ContextInitError",
    "MemoryError",
    "MemoryLimitExceeded",
    "ResearchError",
    "ResearchConfigError",
    "APIConnectionError",
    "AuthenticationError",
    "RateLimitError",
    "FileError",
    "FileReadError",
    "FileWriteError",
    "TimeoutError",
    "ValidationError",
    "InvalidInputError",
    "InvalidFamilyCodeError",
]
