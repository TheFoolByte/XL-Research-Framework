"""
XL Research Framework - Engine Tests

Tests for core Engine functionality.
"""

import pytest
from pathlib import Path


class TestEngineImport:
    """Test engine module imports"""
    
    def test_engine_import(self):
        """Engine should import without errors"""
        from core.engine import Engine
        assert Engine is not None
    
    def test_engine_context_import(self):
        """Engine context manager should import"""
        from core.engine import engine_context
        assert engine_context is not None
    
    def test_run_analysis_import(self):
        """run_analysis function should import"""
        from core.engine import run_analysis
        assert run_analysis is not None


class TestEngineInitialization:
    """Test engine initialization"""
    
    def test_engine_default_profile(self):
        """Engine should initialize with default xl profile"""
        from core.engine import Engine
        engine = Engine()
        assert engine._profile_name == "xl"
    
    def test_engine_custom_profile(self):
        """Engine should accept custom profile"""
        from core.engine import Engine
        engine = Engine("light")
        assert engine._profile_name == "light"
    
    def test_engine_full_profile(self):
        """Engine should accept full profile"""
        from core.engine import Engine
        engine = Engine("full")
        assert engine._profile_name == "full"
    
    def test_engine_initial_state(self):
        """Engine should start with empty results"""
        from core.engine import Engine
        engine = Engine()
        assert engine._results == {}
        assert engine._correlations == []


class TestEngineStats:
    """Test engine statistics"""
    
    def test_get_stats(self):
        """Engine should return stats dict"""
        from core.engine import Engine
        engine = Engine()
        stats = engine.get_stats()
        
        assert isinstance(stats, dict)
        assert "duration_seconds" in stats
        assert "modules_loaded" in stats
        assert "files_scanned" in stats


class TestEngineCallbacks:
    """Test engine callback system"""
    
    def test_set_callbacks(self):
        """Engine should accept callback functions"""
        from core.engine import Engine
        
        engine = Engine()
        
        def on_start(name, i, total):
            pass
        
        def on_complete(name, count):
            pass
        
        engine.set_callbacks(
            on_module_start=on_start,
            on_module_complete=on_complete
        )
        
        assert engine._on_module_start is not None
        assert engine._on_module_complete is not None


class TestEngineMemory:
    """Test engine memory management"""
    
    def test_memory_limit_default(self):
        """Engine should have default memory limit"""
        from core.engine import Engine
        engine = Engine()
        assert engine._memory_limit_mb == 4096  # 4GB default
    
    def test_memory_thresholds(self):
        """Engine should have memory thresholds"""
        from core.engine import Engine
        engine = Engine()
        assert 0 < engine._memory_warning_threshold < 1
        assert 0 < engine._memory_critical_threshold < 1
        assert engine._memory_warning_threshold < engine._memory_critical_threshold
