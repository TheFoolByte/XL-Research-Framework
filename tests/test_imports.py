"""
XL Research Framework - Import and Circular Dependency Tests

Tests to ensure no circular imports and all modules load correctly.
"""

import pytest
import sys
import importlib


class TestCoreImports:
    """Test core module imports without circular dependencies"""
    
    def test_config_import(self):
        """core.config should import"""
        from core.config import config
        assert config is not None
    
    def test_logger_import(self):
        """core.logger should import"""
        from core.logger import log
        assert log is not None
    
    def test_context_import(self):
        """core.context should import"""
        from core.context import Context
        assert Context is not None
    
    def test_engine_import(self):
        """core.engine should import"""
        from core.engine import Engine
        assert Engine is not None
    
    def test_exceptions_import(self):
        """core.exceptions should import"""
        from core.exceptions import XLResearchError
        assert XLResearchError is not None
    
    def test_lazy_loader_import(self):
        """core.lazy_loader should import"""
        from core.lazy_loader import loader
        assert loader is not None
    
    def test_memory_optimizer_import(self):
        """core.memory_optimizer should import"""
        from core.memory_optimizer import MemoryOptimizer
        assert MemoryOptimizer is not None


class TestProfileImports:
    """Test profile imports"""
    
    def test_profiles_package_import(self):
        """profiles package should import"""
        import profiles
        assert profiles is not None
    
    def test_base_profile_import(self):
        """profiles.base should import"""
        from profiles.base import Profile
        assert Profile is not None
    
    def test_light_profile_import(self):
        """LightProfile should import"""
        from profiles import LightProfile
        assert LightProfile is not None
    
    def test_xl_profile_import(self):
        """XLProfile should import"""
        from profiles import XLProfile
        assert XLProfile is not None
    
    def test_full_profile_import(self):
        """FullProfile should import"""
        from profiles import FullProfile
        assert FullProfile is not None


class TestExtractorImports:
    """Test extractor imports"""
    
    def test_partial_jadx_import(self):
        """extractors.partial_jadx should import"""
        from extractors.partial_jadx import PartialJADX
        assert PartialJADX is not None
    
    def test_manifest_parser_import(self):
        """extractors.manifest_parser should import"""
        from extractors.manifest_parser import ManifestParser
        assert ManifestParser is not None


class TestReporterImports:
    """Test reporter imports"""
    
    def test_report_generator_import(self):
        """reporters.report_generator should import"""
        from reporters.report_generator import ReportGenerator
        assert ReportGenerator is not None


class TestResearchImports:
    """Test research package imports"""
    
    def test_research_package_import(self):
        """research package should import"""
        import research
        assert research is not None
    
    def test_research_adapter_import(self):
        """research.adapter should import"""
        from research.adapter import ResearchAdapter
        assert ResearchAdapter is not None
    
    def test_research_modules_import(self):
        """research.modules should import"""
        from research import modules
        assert modules is not None


class TestNoCircularImports:
    """Test that circular imports don't exist"""
    
    def test_full_import_chain(self):
        """Full import chain should work without errors"""
        # Reload all modules to test
        modules_to_test = [
            "core.config",
            "core.logger",
            "core.context",
            "core.exceptions",
            "core.lazy_loader",
            "core.memory_optimizer",
            "core.engine",
            "modules.base",
            "profiles.base",
            "research.adapter",
        ]
        
        for module_name in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                assert module is not None, f"Failed to import {module_name}"
            except ImportError as e:
                pytest.fail(f"Circular import or missing dependency in {module_name}: {e}")
    
    def test_cross_module_imports(self):
        """Cross-module imports should work"""
        # Import engine which uses many other modules
        from core.engine import Engine
        
        # Import research which uses core
        from research import ResearchAdapter
        
        # Import modules which use core
        from modules.base import BaseModule
        
        # All should work without circular import errors
        assert Engine is not None
        assert ResearchAdapter is not None
        assert BaseModule is not None


class TestExceptionHierarchy:
    """Test exception hierarchy"""
    
    def test_base_exception(self):
        """Base exception should work"""
        from core.exceptions import XLResearchError
        
        error = XLResearchError("Test error")
        assert str(error) == "Test error"
    
    def test_exception_with_context(self):
        """Exception should accept context"""
        from core.exceptions import XLResearchError
        
        error = XLResearchError("Test", {"key": "value"})
        assert "key=value" in str(error)
    
    def test_specific_exceptions(self):
        """Specific exceptions should inherit from base"""
        from core.exceptions import (
            XLResearchError,
            ConfigurationError,
            ModuleError,
            AnalysisError,
            ResearchError,
        )
        
        assert issubclass(ConfigurationError, XLResearchError)
        assert issubclass(ModuleError, XLResearchError)
        assert issubclass(AnalysisError, XLResearchError)
        assert issubclass(ResearchError, XLResearchError)
