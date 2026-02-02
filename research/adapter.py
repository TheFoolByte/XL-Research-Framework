"""
Research Adapter - Bridge between xl-research modules and core/engine.py

Provides:
- Lazy loading of research modules
- Shared context integration
- Memory-aware execution
- Profile-based feature toggles
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import gc

# Lazy imports to minimize memory footprint
_client = None
_analyzer = None
_enumerator = None
_validator = None
_decoy = None


@dataclass
class ResearchConfig:
    """Research module configuration"""
    enabled: bool = False
    api_base_url: str = ""
    request_delay: float = 1.5
    timeout: int = 30
    max_retries: int = 3
    enable_smart_patterns: bool = True
    enable_adaptive_learning: bool = True
    max_enumeration_attempts: int = 100
    memory_limit_mb: int = 256
    # API credentials (loaded from env)
    basic_auth: str = ""
    api_key: str = ""


class ResearchAdapter:
    """
    Adapter layer connecting xl-research modules to the main framework.
    
    Uses lazy loading to minimize memory when research features are disabled.
    Respects profile settings for enabling/disabling features.
    """
    
    def __init__(self, config: ResearchConfig, context: Optional[Any] = None):
        """
        Initialize adapter with configuration.
        
        Args:
            config: Research configuration
            context: Optional shared context from core/engine.py
        """
        self._config = config
        self._context = context
        self._client = None
        self._results: Dict[str, Any] = {}
        self._initialized = False
    
    @property
    def is_enabled(self) -> bool:
        """Check if research features are enabled"""
        return self._config.enabled
    
    @property
    def config(self) -> ResearchConfig:
        """Get configuration"""
        return self._config
    
    def initialize(self) -> bool:
        """
        Lazy initialize research modules.
        
        Returns:
            True if initialization successful
        """
        if not self._config.enabled:
            return False
        
        if self._initialized:
            return True
        
        try:
            # Import only when needed
            from .client import XLResearchClient
            
            self._client = XLResearchClient(
                base_url=self._config.api_base_url,
                config={
                    'timeout': self._config.timeout,
                    'max_retries': self._config.max_retries,
                    'request_delay': self._config.request_delay,
                    'basic_auth': self._config.basic_auth,
                    'api_key': self._config.api_key,
                }
            )
            self._initialized = True
            return True
        except Exception as e:
            # Log error but don't crash
            print(f"[WARN] Research adapter init failed: {e}")
            return False
    
    def analyze_family_codes(self, codes: List[str]) -> Dict[str, Any]:
        """
        Analyze family codes for patterns.
        
        Args:
            codes: List of family codes to analyze
            
        Returns:
            Analysis results dictionary
        """
        if not self.is_enabled:
            return {"error": "Research features disabled"}
        
        # Lazy import
        from .modules.analyzer import FamilyCodeAnalyzer
        
        analyzer = FamilyCodeAnalyzer()
        results = analyzer.analyze_batch(codes)
        
        self._results['analysis'] = results
        
        # Cleanup
        del analyzer
        gc.collect()
        
        return results
    
    def enumerate_codes(self, 
                       max_attempts: int = None,
                       target_categories: List[str] = None) -> Dict[str, Any]:
        """
        Run smart enumeration with adaptive learning.
        
        Args:
            max_attempts: Maximum enumeration attempts
            target_categories: Categories to target
            
        Returns:
            Enumeration results
        """
        if not self.is_enabled:
            return {"error": "Research features disabled"}
        
        if not self._initialized:
            if not self.initialize():
                return {"error": "Failed to initialize research client"}
        
        # Lazy import
        from .modules.enumerator import SmartFamilyCodeEnumerator
        
        max_attempts = max_attempts or self._config.max_enumeration_attempts
        
        enumerator = SmartFamilyCodeEnumerator(self._client)
        results = enumerator.enumerate(
            max_attempts=max_attempts,
            use_adaptive=self._config.enable_adaptive_learning,
            target_categories=target_categories
        )
        
        self._results['enumeration'] = enumerator.get_statistics()
        self._results['found_codes'] = enumerator.found_codes
        
        # Cleanup
        del enumerator
        gc.collect()
        
        return results
    
    def validate_package(self, family_code: str) -> Dict[str, Any]:
        """
        Run comprehensive validation on a package.
        
        Args:
            family_code: Package family code
            
        Returns:
            Validation results with risk assessment
        """
        if not self.is_enabled:
            return {"error": "Research features disabled"}
        
        if not self._initialized:
            if not self.initialize():
                return {"error": "Failed to initialize research client"}
        
        # Lazy import
        from .modules.validator import PackageValidator
        
        validator = PackageValidator(self._client)
        results = validator.comprehensive_validation(family_code)
        
        # Cleanup
        del validator
        gc.collect()
        
        return results
    
    def get_decoy(self, decoy_type: str = "default-balance") -> Optional[Dict]:
        """
        Fetch decoy data from endpoints.
        
        Args:
            decoy_type: Type of decoy to fetch
            
        Returns:
            Decoy data or None
        """
        if not self.is_enabled:
            return None
        
        # Lazy import
        from .modules.decoy import DecoyManager
        
        manager = DecoyManager()
        result = manager.fetch_decoy(decoy_type)
        
        # Cleanup
        del manager
        gc.collect()
        
        return result
    
    def discover_endpoints(self) -> Dict[str, Any]:
        """
        Discover available API endpoints.
        
        Returns:
            Dictionary of endpoints and their status
        """
        if not self.is_enabled:
            return {"error": "Research features disabled"}
        
        if not self._initialized:
            if not self.initialize():
                return {"error": "Failed to initialize research client"}
        
        return self._client.discover_endpoints()
    
    def cleanup(self):
        """Release all resources"""
        self._client = None
        self._results.clear()
        self._initialized = False
        gc.collect()
    
    def get_results(self) -> Dict[str, Any]:
        """Get accumulated results"""
        return self._results.copy()


def create_adapter(profile: Dict[str, Any], context: Optional[Any] = None) -> ResearchAdapter:
    """
    Factory function to create adapter from profile settings.
    
    Args:
        profile: Profile configuration dictionary
        context: Optional shared context
        
    Returns:
        Configured ResearchAdapter instance
    """
    research_settings = profile.get('research', {})
    
    config = ResearchConfig(
        enabled=research_settings.get('enabled', False),
        api_base_url=research_settings.get('api_base_url', ''),
        request_delay=research_settings.get('request_delay', 1.5),
        timeout=research_settings.get('timeout', 30),
        max_retries=research_settings.get('max_retries', 3),
        enable_smart_patterns=research_settings.get('enable_smart_patterns', True),
        enable_adaptive_learning=research_settings.get('enable_adaptive_learning', True),
        max_enumeration_attempts=research_settings.get('max_enumeration_attempts', 100),
        memory_limit_mb=research_settings.get('memory_limit_mb', 256),
        basic_auth=research_settings.get('basic_auth', ''),
        api_key=research_settings.get('api_key', ''),
    )
    
    return ResearchAdapter(config, context)


def load_research_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load research configuration from YAML file.
    
    Args:
        config_path: Path to research_config.yaml
        
    Returns:
        Configuration dictionary
    """
    import os
    import yaml
    
    if config_path is None:
        # Default path relative to this file
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'research_config.yaml'
        )
    
    if not os.path.exists(config_path):
        return {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f) or {}
    
    # Expand environment variables
    def expand_env(value):
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_var = value[2:-1]
            return os.environ.get(env_var, '')
        return value
    
    def process_dict(d):
        for key, value in d.items():
            if isinstance(value, dict):
                process_dict(value)
            elif isinstance(value, str):
                d[key] = expand_env(value)
    
    process_dict(config)
    
    return config
