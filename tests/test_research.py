"""
XL Research Framework - Research Module Tests

Tests for research subsystem functionality.
"""

import pytest
from pathlib import Path


class TestResearchImports:
    """Test research module imports"""
    
    def test_research_package_import(self):
        """Research package should import"""
        from research import ResearchAdapter, create_adapter, ResearchConfig
        assert ResearchAdapter is not None
        assert create_adapter is not None
        assert ResearchConfig is not None
    
    def test_adapter_import(self):
        """Adapter module should import"""
        from research.adapter import ResearchAdapter, ResearchConfig
        assert ResearchAdapter is not None
        assert ResearchConfig is not None
    
    def test_client_import(self):
        """Client module should import"""
        from research.client import XLResearchClient
        assert XLResearchClient is not None
    
    def test_auth_import(self):
        """Auth module should import"""
        from research.auth import AuthManager
        assert AuthManager is not None
    
    def test_signature_import(self):
        """Signature module should import"""
        from research.signature import SignatureGenerator
        assert SignatureGenerator is not None


class TestResearchModulesImport:
    """Test research submodules imports"""
    
    def test_analyzer_import(self):
        """Analyzer module should import"""
        from research.modules.analyzer import FamilyCodeAnalyzer
        assert FamilyCodeAnalyzer is not None
    
    def test_enumerator_import(self):
        """Enumerator module should import"""
        from research.modules.enumerator import SmartFamilyCodeEnumerator
        assert SmartFamilyCodeEnumerator is not None
    
    def test_validator_import(self):
        """Validator module should import"""
        from research.modules.validator import PackageValidator
        assert PackageValidator is not None
    
    def test_decoy_import(self):
        """Decoy module should import"""
        from research.modules.decoy import DecoyManager
        assert DecoyManager is not None


class TestResearchUtilsImport:
    """Test research utilities imports"""
    
    def test_helpers_import(self):
        """Helpers should import"""
        from research.utils.helpers import (
            generate_random_phone,
            validate_uuid,
            format_price
        )
        assert generate_random_phone is not None
        assert validate_uuid is not None
        assert format_price is not None
    
    def test_exporter_import(self):
        """Exporter should import"""
        from research.utils.exporter import ResultExporter
        assert ResultExporter is not None


class TestHelperFunctions:
    """Test research helper functions"""
    
    def test_validate_uuid_valid(self):
        """validate_uuid should accept valid UUID"""
        from research.utils.helpers import validate_uuid
        
        result = validate_uuid("d004d498-e8a8-4e22-b8b1-b71b7652b409")
        assert result is True
    
    def test_validate_uuid_invalid(self):
        """validate_uuid should reject invalid UUID"""
        from research.utils.helpers import validate_uuid
        
        result = validate_uuid("not-a-uuid")
        assert result is False
    
    def test_format_price(self):
        """format_price should format correctly"""
        from research.utils.helpers import format_price
        
        result = format_price(50000)
        assert "50" in result
        assert "Rp" in result
    
    def test_generate_random_phone(self):
        """generate_random_phone should return valid format"""
        from research.utils.helpers import generate_random_phone
        
        phone = generate_random_phone()
        assert phone.startswith("08")
        assert len(phone) == 12


class TestFamilyCodeAnalyzer:
    """Test FamilyCodeAnalyzer"""
    
    def test_analyzer_init(self):
        """Analyzer should initialize"""
        from research.modules.analyzer import FamilyCodeAnalyzer
        
        analyzer = FamilyCodeAnalyzer()
        assert analyzer is not None
    
    def test_analyzer_has_patterns(self):
        """Analyzer should have patterns"""
        from research.modules.analyzer import FamilyCodeAnalyzer
        
        analyzer = FamilyCodeAnalyzer()
        patterns = analyzer.get_known_patterns()
        
        assert isinstance(patterns, list)
        assert len(patterns) > 0


class TestResearchConfig:
    """Test ResearchConfig dataclass"""
    
    def test_config_creation(self):
        """ResearchConfig should be creatable"""
        from research.adapter import ResearchConfig
        
        config = ResearchConfig(
            api_base_url="https://test.com",
            basic_auth="test_auth"
        )
        
        assert config.api_base_url == "https://test.com"
        assert config.basic_auth == "test_auth"
    
    def test_config_defaults(self):
        """ResearchConfig should have defaults"""
        from research.adapter import ResearchConfig
        
        config = ResearchConfig()
        
        assert config.timeout == 30
        assert config.max_retries == 3


class TestCreateAdapter:
    """Test create_adapter factory"""
    
    def test_create_adapter_disabled(self):
        """create_adapter should return None if disabled"""
        from research.adapter import create_adapter
        
        adapter = create_adapter({"enabled": False})
        
        assert adapter is None
    
    def test_create_adapter_enabled(self):
        """create_adapter should return adapter if enabled"""
        from research.adapter import create_adapter
        
        adapter = create_adapter({"enabled": True})
        
        assert adapter is not None
