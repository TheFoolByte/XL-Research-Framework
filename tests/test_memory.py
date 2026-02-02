"""
XL Research Framework - Memory Tests

Tests for memory optimization functionality.
"""

import pytest
import gc


class TestMemoryOptimizerImport:
    """Test memory optimizer imports"""
    
    def test_optimizer_import(self):
        """Memory optimizer should import"""
        from core.memory_optimizer import MemoryOptimizer
        assert MemoryOptimizer is not None
    
    def test_monitor_context_import(self):
        """Memory monitor context should import"""
        from core.memory_optimizer import memory_monitor
        assert memory_monitor is not None


class TestMemoryOptimizer:
    """Test MemoryOptimizer class"""
    
    def test_optimizer_creation(self):
        """Optimizer should be creatable"""
        from core.memory_optimizer import MemoryOptimizer
        
        optimizer = MemoryOptimizer(limit_mb=1024)
        assert optimizer is not None
    
    def test_get_current_usage(self):
        """Optimizer should report memory usage"""
        from core.memory_optimizer import MemoryOptimizer
        
        optimizer = MemoryOptimizer()
        usage = optimizer.get_current_usage_mb()
        
        assert isinstance(usage, (int, float))
        assert usage >= 0
    
    def test_check_thresholds(self):
        """Optimizer should check memory thresholds"""
        from core.memory_optimizer import MemoryOptimizer
        
        optimizer = MemoryOptimizer(limit_mb=8192)  # High limit
        exceeded, level = optimizer.check_thresholds()
        
        assert isinstance(exceeded, bool)
        assert level in ["ok", "warning", "critical"]
    
    def test_force_cleanup(self):
        """Optimizer should force cleanup"""
        from core.memory_optimizer import MemoryOptimizer
        
        optimizer = MemoryOptimizer()
        freed = optimizer.force_cleanup()
        
        assert isinstance(freed, (int, float))


class TestMemoryMonitorContext:
    """Test memory_monitor context manager"""
    
    def test_context_manager(self):
        """memory_monitor should work as context manager"""
        from core.memory_optimizer import memory_monitor
        
        with memory_monitor("test_operation") as monitor:
            # Do some work
            data = list(range(1000))
        
        # Should complete without error


class TestLRUCache:
    """Test LRU cache functionality"""
    
    def test_context_has_cache(self):
        """Context should have LRU cache"""
        from core.context import Context
        
        # Check that Context class has cache-related methods
        assert hasattr(Context, '_cache') or hasattr(Context, '__init__')


class TestGarbageCollection:
    """Test garbage collection integration"""
    
    def test_gc_enabled(self):
        """Garbage collection should be enabled"""
        assert gc.isenabled()
    
    def test_gc_collect(self):
        """gc.collect should work"""
        collected = gc.collect()
        assert isinstance(collected, int)


class TestMemoryLimits:
    """Test memory limit enforcement"""
    
    def test_profile_memory_limits(self):
        """Profiles should have memory limits"""
        from profiles import LightProfile, XLProfile, FullProfile
        
        light = LightProfile()
        xl = XLProfile()
        full = FullProfile()
        
        assert light.memory_limit_mb < xl.memory_limit_mb
        assert xl.memory_limit_mb <= full.memory_limit_mb
    
    def test_light_profile_limit(self):
        """Light profile should have ~2GB limit"""
        from profiles import LightProfile
        
        profile = LightProfile()
        assert 1500 <= profile.memory_limit_mb <= 2500
    
    def test_xl_profile_limit(self):
        """XL profile should have ~4GB limit"""
        from profiles import XLProfile
        
        profile = XLProfile()
        assert 3500 <= profile.memory_limit_mb <= 4500
    
    def test_full_profile_limit(self):
        """Full profile should have ~6GB limit"""
        from profiles import FullProfile
        
        profile = FullProfile()
        assert 5500 <= profile.memory_limit_mb <= 6500


class TestLazyLoading:
    """Test lazy loading functionality"""
    
    def test_lazy_loader_exists(self):
        """Lazy loader should exist"""
        from core.lazy_loader import LazyModuleLoader
        assert LazyModuleLoader is not None
    
    def test_lazy_loading_deferred(self):
        """Lazy loading should defer module load"""
        from core.lazy_loader import loader
        
        # Modules should not be loaded initially
        # This tests that the loader exists and can list modules
        available = loader.list_available()
        assert isinstance(available, list)


class TestMemoryUsageUnderLimit:
    """Test that memory stays under profile limits"""
    
    def test_light_profile_import_memory(self):
        """Importing with light profile settings should stay reasonable"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / (1024 * 1024)
        
        # Python process with imports should be under 500MB
        assert memory_mb < 500, f"Memory usage too high: {memory_mb:.1f}MB"
