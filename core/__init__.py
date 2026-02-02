"""
XL Research Framework v2.1 - Core Package
"""

__version__ = "2.1.0"
__author__ = "XL Research Team"

from .config import Config, config
from .context import Context, analysis_context, AnalysisResult, FileInfo
from .logger import Logger, log
from .lazy_loader import LazyModuleLoader, loader
from .engine import Engine, run_analysis
from .memory_optimizer import (
    memory_optimizer, file_cache, streaming,
    MemoryOptimizer, LRUFileCache, StreamingReader,
    BinaryFilter, WorkerPool, SmartUnloader, AsyncIO
)
from .correlation_engine import CorrelationEngine, correlation_engine
from .correlator import Correlator, Insight, correlator

__all__ = [
    "Config", "config",
    "Context", "analysis_context", "AnalysisResult", "FileInfo",
    "Logger", "log",
    "LazyModuleLoader", "loader",
    "Engine", "run_analysis",
    "memory_optimizer", "file_cache", "streaming",
    "MemoryOptimizer", "LRUFileCache", "StreamingReader", "BinaryFilter",
    "WorkerPool", "SmartUnloader", "AsyncIO",
    "CorrelationEngine", "correlation_engine",
    "Correlator", "Insight", "correlator",
    "__version__"
]
