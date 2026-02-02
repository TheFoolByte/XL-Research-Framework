"""
XL Research Framework - Module Tests

Tests for analysis module functionality.
"""

import pytest
from pathlib import Path


class TestModuleImports:
    """Test module imports"""
    
    def test_base_module_import(self):
        """BaseModule should import"""
        from modules.base import BaseModule, Finding
        assert BaseModule is not None
        assert Finding is not None
    
    def test_api_analyzer_import(self):
        """API analyzer should import"""
        from modules.api.analyzer import Analyzer
        assert Analyzer is not None
    
    def test_auth_analyzer_import(self):
        """Auth analyzer should import"""
        from modules.auth.analyzer import Analyzer
        assert Analyzer is not None
    
    def test_config_analyzer_import(self):
        """Config analyzer should import"""
        from modules.config.analyzer import Analyzer
        assert Analyzer is not None
    
    def test_endpoint_analyzer_import(self):
        """Endpoint analyzer should import"""
        from modules.endpoint.analyzer import Analyzer
        assert Analyzer is not None
    
    def test_family_analyzer_import(self):
        """Family analyzer should import"""
        from modules.family.analyzer import Analyzer
        assert Analyzer is not None


class TestFinding:
    """Test Finding dataclass"""
    
    def test_finding_creation(self):
        """Finding should be creatable with defaults"""
        from modules.base import Finding
        
        finding = Finding(
            category="Test",
            message="Test message"
        )
        
        assert finding.category == "Test"
        assert finding.message == "Test message"
        assert finding.severity == "info"  # default
    
    def test_finding_to_dict(self):
        """Finding should convert to dict"""
        from modules.base import Finding
        
        finding = Finding(
            category="API",
            message="Found API key",
            severity="critical"
        )
        
        d = finding.to_dict()
        
        assert isinstance(d, dict)
        assert d["category"] == "API"
        assert d["severity"] == "critical"


class TestBaseModule:
    """Test BaseModule functionality"""
    
    def test_module_reset(self):
        """Module should reset findings"""
        from modules.api.analyzer import Analyzer
        
        analyzer = Analyzer()
        analyzer._findings = ["dummy"]
        analyzer.reset()
        
        assert len(analyzer._findings) == 0
    
    def test_module_add_finding(self):
        """Module should add findings"""
        from modules.api.analyzer import Analyzer
        from modules.base import Finding
        
        analyzer = Analyzer()
        analyzer.reset()
        
        finding = Finding(category="Test", message="Test")
        analyzer.add_finding(finding)
        
        assert len(analyzer._findings) == 1


class TestAnalyzerPatterns:
    """Test analyzer pattern compilation"""
    
    def test_api_patterns_compiled(self):
        """API analyzer patterns should compile"""
        from modules.api.analyzer import Analyzer
        
        analyzer = Analyzer()
        
        assert len(analyzer._compiled_patterns) > 0
    
    def test_auth_patterns_compiled(self):
        """Auth analyzer patterns should compile"""
        from modules.auth.analyzer import Analyzer
        
        analyzer = Analyzer()
        
        assert len(analyzer._compiled_patterns) > 0
    
    def test_config_patterns_compiled(self):
        """Config analyzer patterns should compile"""
        from modules.config.analyzer import Analyzer
        
        analyzer = Analyzer()
        
        assert len(analyzer._compiled_patterns) > 0


class TestLazyLoader:
    """Test lazy module loader"""
    
    def test_loader_import(self):
        """Lazy loader should import"""
        from core.lazy_loader import LazyModuleLoader, loader
        assert LazyModuleLoader is not None
        assert loader is not None
    
    def test_loader_list_available(self):
        """Loader should list available modules"""
        from core.lazy_loader import loader
        
        available = loader.list_available()
        
        assert isinstance(available, list)
