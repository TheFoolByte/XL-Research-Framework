"""
XL Research Framework v2.1 - Central Engine

Production-quality orchestrator that manages:
- Profile loading and configuration
- Context initialization
- Lazy module loading with LRU cache
- Memory monitoring and GC triggers
- Analysis pipeline execution
- Correlation analysis stage
- Research integration (Stage 8)
- Cleanup and resource management
"""

import os
import gc
import time
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from contextlib import contextmanager
import threading

from .config import config
from .context import Context, analysis_context
from .logger import log
from .lazy_loader import LazyModuleLoader, loader
from .correlation_engine import CorrelationEngine
from .memory_optimizer import memory_optimizer


@dataclass
class EngineStats:
    """Engine execution statistics"""
    start_time: float = 0.0
    end_time: float = 0.0
    modules_loaded: int = 0
    modules_unloaded: int = 0
    files_scanned: int = 0
    total_findings: int = 0
    correlations_found: int = 0
    memory_peak_mb: float = 0.0
    gc_runs: int = 0
    research_findings: int = 0


class Engine:
    """
    Central analysis orchestrator.
    
    Manages the complete analysis workflow:
    1. Load profile (light/xl/full)
    2. Extract APK (partial or full decompilation)
    3. Initialize memory-efficient context
    4. Load required modules lazily
    5. Run analysis with memory monitoring
    6. Run correlation analysis
    7. Generate reports
    8. Cleanup resources
    
    Memory Management:
    - Monitors memory usage continuously
    - Triggers GC at configurable thresholds
    - Unloads modules when memory is constrained
    - Uses streaming file reads
    
    Thread Safety:
    - Uses locks for shared state
    - Safe for single-threaded analysis
    """
    
    def __init__(self, profile_name: str = "xl"):
        """
        Initialize engine with profile.
        
        Args:
            profile_name: Profile to use (light, xl, full)
        """
        self._profile_name = profile_name
        self._profile = None
        self._loader = loader
        self._context: Optional[Context] = None
        self._results: Dict[str, Any] = {}
        self._correlations: List[Any] = []
        self._research_results: Dict[str, Any] = {}
        self._research_adapter = None
        self._research_override: Optional[bool] = None  # CLI override
        self._stats = EngineStats()
        self._lock = threading.Lock()
        
        # Memory configuration
        self._memory_limit_mb = 4096  # Default 4GB
        self._memory_warning_threshold = 0.85
        self._memory_critical_threshold = 0.95
        
        # Callbacks
        self._on_module_start: Optional[Callable] = None
        self._on_module_complete: Optional[Callable] = None
        self._on_finding: Optional[Callable] = None
    
    # ==================== PUBLIC API ====================
    
    def analyze(self, apk_path: str) -> Dict[str, Any]:
        """
        Run complete analysis on APK.
        
        Args:
            apk_path: Path to APK file
            
        Returns:
            Analysis results dictionary with:
            - apk: APK name
            - profile: Profile used
            - timestamp: Analysis timestamp
            - duration_seconds: Total time
            - total_findings: Finding count
            - results: Per-module results
            - correlations: Security correlations
        """
        self._stats = EngineStats()
        self._stats.start_time = time.time()
        
        try:
            # Validate input
            if not self._validate_apk(apk_path):
                return {"error": "APK not found or invalid"}
            
            log.header("XL RESEARCH FRAMEWORK v2.1")
            log.info(f"Target: {os.path.basename(apk_path)}")
            
            # Pipeline stages
            self._stage_load_profile()
            
            source_dir = self._stage_extract(apk_path)
            if not source_dir:
                return {"error": "Extraction failed"}
            
            self._stage_init_context(apk_path, source_dir)
            
            modules = self._stage_load_modules()
            if not modules:
                return {"error": "No modules loaded"}
            
            self._stage_run_analysis(modules)
            
            self._stage_correlation()
            
            self._stage_research()
            
            self._stage_cleanup()
            
            # Finalize
            self._stats.end_time = time.time()
            elapsed = self._stats.end_time - self._stats.start_time
            
            log.header("COMPLETE")
            log.success(f"Analysis completed in {elapsed:.1f}s")
            log.info(f"Total findings: {self._stats.total_findings}")
            log.info(f"Correlations: {self._stats.correlations_found}")
            
            return self._build_results()
            
        except Exception as e:
            log.error(f"Analysis failed: {e}")
            self._emergency_cleanup()
            return {"error": str(e)}
    
    def set_callbacks(self, 
                      on_module_start: Optional[Callable] = None,
                      on_module_complete: Optional[Callable] = None,
                      on_finding: Optional[Callable] = None):
        """Set progress callbacks for UI integration"""
        self._on_module_start = on_module_start
        self._on_module_complete = on_module_complete
        self._on_finding = on_finding
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            "duration_seconds": self._stats.end_time - self._stats.start_time,
            "modules_loaded": self._stats.modules_loaded,
            "files_scanned": self._stats.files_scanned,
            "total_findings": self._stats.total_findings,
            "correlations": self._stats.correlations_found,
            "memory_peak_mb": self._stats.memory_peak_mb,
            "gc_runs": self._stats.gc_runs,
        }
    
    def set_research_override(self, enabled: bool):
        """
        Override profile's research setting.
        
        Args:
            enabled: True to force enable, False to force disable
        """
        self._research_override = enabled
    
    # ==================== PIPELINE STAGES ====================
    
    def _stage_load_profile(self):
        """Stage 1: Load execution profile"""
        log.section("Loading Profile")
        
        from profiles import ProfileLoader
        
        self._profile = ProfileLoader.load(self._profile_name)
        self._memory_limit_mb = self._profile.memory_limit_mb
        
        # Configure memory optimizer
        memory_optimizer.configure(
            memory_limit_mb=self._memory_limit_mb,
            gc_threshold=self._memory_warning_threshold
        )
        
        log.info(f"Profile: {self._profile.name}")
        log.info(f"Description: {self._profile.description}")
        log.info(f"Memory limit: {self._memory_limit_mb} MB")
        log.info(f"Modules: {', '.join(self._profile.modules)}")
    
    def _stage_extract(self, apk_path: str) -> Optional[str]:
        """Stage 2: Extract APK with partial decompilation"""
        log.section("Extraction")
        
        from extractors.partial_jadx import PartialJADX
        
        extractor = PartialJADX()
        level = self._profile.decompile_level
        
        log.info(f"Extraction level: {level}")
        
        try:
            source_dir = extractor.extract(apk_path, level=level)
            log.success(f"Extracted to: {source_dir}")
            return source_dir
        except Exception as e:
            log.error(f"Extraction failed: {e}")
            return None
    
    def _stage_init_context(self, apk_path: str, source_dir: str):
        """Stage 3: Initialize analysis context"""
        log.section("Initializing Context")
        
        self._context = Context(apk_path, source_dir)
        
        # Inject profile settings
        self._context._config = config
        
        log.info(f"APK: {self._context.apk_name}")
        log.info(f"Source: {source_dir}")
    
    def _stage_load_modules(self) -> List[Any]:
        """Stage 4: Load modules lazily"""
        log.section("Loading Modules")
        
        modules = self._loader.load_for_profile(self._profile)
        self._stats.modules_loaded = len(modules)
        
        log.info(f"Loaded {len(modules)} modules:")
        for mod in modules:
            log.info(f"  • {mod.name} (priority: {mod.priority})")
        
        return modules
    
    def _stage_run_analysis(self, modules: List[Any]):
        """Stage 5: Run analysis with memory monitoring"""
        log.section("Analysis")
        
        total = len(modules)
        
        for i, module in enumerate(modules, 1):
            # Memory check before each module
            self._check_memory_pressure()
            
            # Update peak memory
            current_mb = self._get_memory_mb()
            if current_mb > self._stats.memory_peak_mb:
                self._stats.memory_peak_mb = current_mb
            
            # Callback
            if self._on_module_start:
                self._on_module_start(module.name, i, total)
            
            log.progress(i, total, f"Running {module.name}")
            
            try:
                result = module.analyze(self._context)
                self._results[module.name] = result
                
                finding_count = result.count if hasattr(result, 'count') else 0
                self._stats.total_findings += finding_count
                
                if finding_count > 0:
                    log.info(f"  → {finding_count} findings")
                    self._show_top_findings(result, limit=2)
                else:
                    log.info(f"  → No findings")
                
                # Callback
                if self._on_module_complete:
                    self._on_module_complete(module.name, finding_count)
                    
            except Exception as e:
                log.error(f"  → Error: {e}")
                self._results[module.name] = {"error": str(e)}
            
            # Unload if memory constrained
            if self._get_memory_mb() > self._memory_limit_mb * 0.7:
                self._loader.unload(module.name)
                self._stats.modules_unloaded += 1
        
        # Update file stats
        if self._context:
            self._stats.files_scanned = self._context.files_scanned
    
    def _stage_correlation(self):
        """Stage 6: Run correlation analysis"""
        log.section("Correlation Analysis")
        
        try:
            correlation_engine = CorrelationEngine()
            
            # Build temp results
            temp_results = self._build_results()
            
            # Run correlation
            self._correlations = correlation_engine.analyze(temp_results)
            self._stats.correlations_found = len(self._correlations)
            
            summary = correlation_engine.get_summary()
            
            log.info(f"Found {summary['total']} correlations")
            log.info(f"Risk increase: +{summary['risk_increase']}")
            
            # Show top correlations
            if summary.get('top_correlations'):
                log.info("Top correlations:")
                for corr in summary['top_correlations'][:3]:
                    log.finding(
                        corr['type'].upper(),
                        corr['description'][:50],
                        corr['severity']
                    )
                    
        except Exception as e:
            log.warning(f"Correlation error: {e}")
            self._correlations = []
    
    def _stage_research(self):
        """Stage 8: Run research analysis (if enabled in profile)"""
        # Check if research is enabled in profile
        if not self._profile:
            return
        
        # Determine if research should run (CLI override takes precedence)
        if self._research_override is not None:
            research_enabled = self._research_override
        else:
            research_enabled = getattr(self._profile, 'research_enabled', False)
        
        if not research_enabled:
            log.info("Research: disabled")
            return
        
        log.section("Research Analysis")
        
        try:
            # Lazy import research adapter
            from research import create_adapter, ResearchConfig
            
            # Load research config from profile settings
            research_settings = getattr(self._profile, 'research_settings', {})
            
            if not research_settings:
                log.info("Research: no settings configured")
                return
            
            # Create adapter with profile settings
            self._research_adapter = create_adapter(research_settings)
            
            if not self._research_adapter:
                log.warning("Research: adapter creation failed")
                return
            
            # Initialize the adapter
            if not self._research_adapter.initialize():
                log.warning("Research: initialization failed")
                return
            
            log.info("Research adapter initialized")
            
            # Run research if family codes were found in analysis
            family_codes = self._extract_family_codes_from_results()
            
            if family_codes:
                log.info(f"Analyzing {len(family_codes)} family codes from analysis")
                
                # Analyze discovered family codes
                research_result = self._research_adapter.analyze_family_codes(family_codes)
                
                if research_result:
                    self._research_results['family_analysis'] = research_result
                    finding_count = research_result.get('valid', 0)
                    self._stats.research_findings += finding_count
                    log.success(f"Research: analyzed {finding_count} valid codes")
            else:
                log.info("No family codes found in analysis results")
            
            # Cleanup research adapter
            self._research_adapter.cleanup()
            self._research_adapter = None
            
        except ImportError:
            log.info("Research: module not available")
        except Exception as e:
            log.warning(f"Research error: {e}")
            self._research_results = {}
    
    def _extract_family_codes_from_results(self) -> List[str]:
        """Extract family codes from analysis results"""
        codes = []
        
        for module_name, result in self._results.items():
            findings = getattr(result, 'findings', [])
            
            for finding in findings:
                # Check for family_code in finding data
                if isinstance(finding, dict):
                    code = finding.get('family_code') or finding.get('familyCode')
                    if code:
                        codes.append(code)
                    
                    # Also check in data field
                    data = finding.get('data', {})
                    if isinstance(data, dict):
                        code = data.get('family_code') or data.get('familyCode')
                        if code:
                            codes.append(code)
        
        # Remove duplicates
        return list(set(codes))
    
    def _stage_cleanup(self):
        """Stage 9: Cleanup resources"""
        log.section("Cleanup")
        
        self._loader.unload_all()
        
        if self._context:
            self._context.cleanup()
        
        # Cleanup research adapter if still present
        if self._research_adapter:
            try:
                self._research_adapter.cleanup()
            except:
                pass
            self._research_adapter = None
        
        gc.collect()
        self._stats.gc_runs += 1
        
        log.info("Resources released")
    
    # ==================== MEMORY MANAGEMENT ====================
    
    def _check_memory_pressure(self):
        """Check and handle memory pressure"""
        usage_percent = self._get_memory_mb() / self._memory_limit_mb
        
        if usage_percent >= self._memory_critical_threshold:
            # Critical: aggressive cleanup
            log.warning("Critical memory pressure - aggressive cleanup")
            self._aggressive_cleanup()
        elif usage_percent >= self._memory_warning_threshold:
            # Warning: light cleanup
            log.warning("Memory pressure detected - running GC")
            self._light_cleanup()
    
    def _light_cleanup(self):
        """Light memory cleanup"""
        if self._context:
            self._context.cleanup_cache()
        gc.collect()
        self._stats.gc_runs += 1
    
    def _aggressive_cleanup(self):
        """Aggressive memory cleanup"""
        if self._context:
            self._context.cleanup_cache()
        
        # Unload least recently used modules
        self._loader.unload_lru(keep=2)
        
        gc.collect()
        gc.collect()  # Double collect for thorough cleanup
        self._stats.gc_runs += 2
    
    def _emergency_cleanup(self):
        """Emergency cleanup on error"""
        try:
            self._loader.unload_all()
            if self._context:
                self._context.cleanup()
            gc.collect()
        except:
            pass
    
    def _get_memory_mb(self) -> float:
        """Get current memory usage in MB"""
        return memory_optimizer.get_usage_mb()
    
    # ==================== HELPERS ====================
    
    def _validate_apk(self, apk_path: str) -> bool:
        """Validate APK file exists"""
        if not os.path.exists(apk_path):
            log.error(f"APK not found: {apk_path}")
            return False
        
        if not apk_path.lower().endswith('.apk'):
            log.warning("File may not be an APK")
        
        return True
    
    def _show_top_findings(self, result, limit: int = 3):
        """Show top findings from a result"""
        findings = getattr(result, 'findings', [])
        
        for finding in findings[:limit]:
            severity = finding.get("severity", "info")
            category = finding.get("category", "")
            message = finding.get("message", "")[:50]
            
            log.finding(category, message, severity)
            
            # Callback
            if self._on_finding:
                self._on_finding(finding)
    
    def _build_results(self) -> Dict[str, Any]:
        """Build final results dictionary"""
        result = {
            "apk": self._context.apk_name if self._context else "",
            "profile": self._profile_name,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": (
                self._stats.end_time - self._stats.start_time
                if self._stats.end_time else 0
            ),
            "total_findings": self._stats.total_findings,
            "memory_peak_mb": round(self._stats.memory_peak_mb, 1),
            "files_scanned": self._stats.files_scanned,
            "results": {
                name: {
                    "count": getattr(r, 'count', 0),
                    "findings": getattr(r, 'findings', [])
                }
                for name, r in self._results.items()
                if hasattr(r, 'findings')
            }
        }
        
        # Add correlations
        if self._correlations:
            result["correlations"] = {
                "count": len(self._correlations),
                "items": [
                    {
                        "type": c.type,
                        "severity": c.severity,
                        "description": c.description,
                        "source_module": c.source_module,
                        "target_module": c.target_module,
                        "confidence": c.confidence,
                        "risk_increase": c.risk_increase
                    }
                    for c in self._correlations[:30]
                ]
            }
        
        # Add research results
        if self._research_results:
            result["research"] = {
                "findings_count": self._stats.research_findings,
                "results": self._research_results
            }
        
        return result


# ==================== CONVENIENCE FUNCTIONS ====================

def run_analysis(apk_path: str, profile: str = "xl") -> Dict[str, Any]:
    """
    Convenience function to run analysis.
    
    Args:
        apk_path: Path to APK file
        profile: Profile name (light, xl, full)
        
    Returns:
        Analysis results dictionary
    """
    engine = Engine(profile)
    return engine.analyze(apk_path)


@contextmanager
def engine_context(profile: str = "xl"):
    """
    Context manager for Engine usage.
    
    Usage:
        with engine_context("xl") as engine:
            results = engine.analyze("app.apk")
    """
    engine = Engine(profile)
    try:
        yield engine
    finally:
        engine._emergency_cleanup()
