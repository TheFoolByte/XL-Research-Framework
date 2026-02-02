"""
XL Research Framework v2.1 - Lazy Module Loader

Dynamic module loading system that loads modules only when needed.
Helps optimize memory usage on 8GB RAM systems.
"""

import importlib
import gc
from typing import Dict, List, Optional, Type, Any
from functools import lru_cache


class LazyModuleLoader:
    """
    Lazy loading system for analysis modules.
    
    Features:
    - Loads modules on-demand
    - Caches loaded modules
    - Unloads modules to free memory
    - Thread-safe singleton
    """
    
    _instance = None
    
    # Module registry: name -> module path
    MODULES = {
        "api_scanner": "modules.api.analyzer",
        "endpoint_finder": "modules.endpoint.analyzer", 
        "auth_flow": "modules.auth.analyzer",
        "family_logic": "modules.family.analyzer",
        "env_extractor": "modules.config.analyzer",
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._cache: Dict[str, Any] = {}
        self._load_order: List[str] = []
        self._max_cached = 5  # Max modules in cache
    
    def load(self, name: str) -> Optional[Any]:
        """
        Load a module by name. Returns cached instance if available.
        
        Args:
            name: Module name (e.g., 'api', 'endpoint')
            
        Returns:
            Analyzer instance or None if not found
        """
        if name not in self.MODULES:
            return None
        
        # Return cached if available
        if name in self._cache:
            return self._cache[name]
        
        # Enforce cache limit
        if len(self._cache) >= self._max_cached:
            self._evict_oldest()
        
        # Dynamic import
        try:
            module_path = self.MODULES[name]
            module = importlib.import_module(module_path)
            
            # Get the Analyzer class
            if hasattr(module, 'Analyzer'):
                instance = module.Analyzer()
            elif hasattr(module, f'{name.title()}Analyzer'):
                cls = getattr(module, f'{name.title()}Analyzer')
                instance = cls()
            else:
                return None
            
            # Cache it
            self._cache[name] = instance
            self._load_order.append(name)
            
            return instance
            
        except ImportError as e:
            print(f"[!] Failed to load module {name}: {e}")
            return None
    
    def load_for_profile(self, profile) -> List[Any]:
        """
        Load all modules required by a profile.
        
        Args:
            profile: Profile instance with 'modules' attribute
            
        Returns:
            List of loaded analyzer instances
        """
        modules = []
        
        for name in profile.modules:
            if name == "all":
                # Load all available modules
                for mod_name in self.MODULES.keys():
                    mod = self.load(mod_name)
                    if mod:
                        modules.append(mod)
                break
            else:
                mod = self.load(name)
                if mod:
                    modules.append(mod)
        
        # Sort by priority
        modules.sort(key=lambda x: getattr(x, 'priority', 50))
        
        return modules
    
    def unload(self, name: str):
        """
        Unload a module to free memory.
        
        Args:
            name: Module name to unload
        """
        if name in self._cache:
            del self._cache[name]
            if name in self._load_order:
                self._load_order.remove(name)
            gc.collect()
    
    def unload_all(self):
        """Unload all cached modules"""
        self._cache.clear()
        self._load_order.clear()
        gc.collect()
    
    def _evict_oldest(self):
        """Evict oldest module from cache (LRU)"""
        if self._load_order:
            oldest = self._load_order.pop(0)
            if oldest in self._cache:
                del self._cache[oldest]
            gc.collect()
    
    @property
    def loaded_modules(self) -> List[str]:
        """Get list of currently loaded module names"""
        return list(self._cache.keys())
    
    @classmethod
    def list_available(cls) -> List[str]:
        """List all available module names"""
        return list(cls.MODULES.keys())


# Singleton instance
loader = LazyModuleLoader()
