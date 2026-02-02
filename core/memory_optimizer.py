"""
XL Research Framework - Advanced Memory & CPU Optimizer

Techniques Applied:
1. Generators - Lazy iteration, no full list loading
2. LRU Cache - Bounded caching with automatic eviction
3. Multiprocessing Limits - Worker pool based on profile
4. Smart Unloading - Priority-based module unloading
5. Async IO - Non-blocking file operations where safe

Target: 8GB RAM systems
"""

import os
import gc
import psutil
import mmap
import asyncio
import threading
from pathlib import Path
from typing import Dict, List, Any, Iterator, Optional, Callable, Tuple, Generator
from dataclasses import dataclass, field
from collections import OrderedDict
from functools import lru_cache, wraps
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time


# ==================== CONFIGURATION ====================

@dataclass
class OptimizerConfig:
    """Optimizer configuration"""
    memory_limit_mb: int = 4096
    gc_threshold: float = 0.80
    critical_threshold: float = 0.95
    max_workers: int = 2
    max_cache_mb: int = 256
    max_cached_items: int = 100
    chunk_size: int = 64 * 1024  # 64KB
    async_enabled: bool = True


# ==================== LRU FILE CACHE ====================

class LRUFileCache:
    """
    LRU cache for file contents with size limits.
    
    Features:
    - Automatic eviction when size exceeded
    - Memory-aware (evicts when memory low)
    - Thread-safe operations
    """
    
    def __init__(self, max_size_mb: int = 256, max_items: int = 100):
        self._cache: OrderedDict[str, bytes] = OrderedDict()
        self._max_size = max_size_mb * 1024 * 1024
        self._max_items = max_items
        self._current_size = 0
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[bytes]:
        """Get item, moves to end (most recently used)"""
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                self._hits += 1
                return self._cache[key]
            self._misses += 1
            return None
    
    def put(self, key: str, value: bytes) -> bool:
        """Put item, evicts LRU if needed"""
        size = len(value)
        
        # Skip if too large
        if size > self._max_size // 2:
            return False
        
        with self._lock:
            # Remove old entry if exists
            if key in self._cache:
                self._current_size -= len(self._cache[key])
                del self._cache[key]
            
            # Evict until space available
            while (self._current_size + size > self._max_size or 
                   len(self._cache) >= self._max_items):
                if not self._cache:
                    break
                _, evicted = self._cache.popitem(last=False)
                self._current_size -= len(evicted)
            
            # Add new entry
            self._cache[key] = value
            self._current_size += size
            return True
    
    def clear(self):
        """Clear all cache"""
        with self._lock:
            self._cache.clear()
            self._current_size = 0
    
    def evict_percent(self, percent: float = 0.5):
        """Evict a percentage of cached items (oldest first)"""
        with self._lock:
            count = int(len(self._cache) * percent)
            for _ in range(count):
                if self._cache:
                    _, evicted = self._cache.popitem(last=False)
                    self._current_size -= len(evicted)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = self._hits / (self._hits + self._misses) if (self._hits + self._misses) > 0 else 0
        return {
            "items": len(self._cache),
            "max_items": self._max_items,
            "size_mb": round(self._current_size / (1024 * 1024), 2),
            "max_size_mb": round(self._max_size / (1024 * 1024), 2),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 2)
        }


# ==================== STREAMING FILE READER ====================

class StreamingReader:
    """
    Memory-efficient file reader using generators.
    
    Never loads full file into memory.
    """
    
    @staticmethod
    def read_lines(file_path: str, encoding: str = "utf-8") -> Generator[Tuple[int, str], None, None]:
        """
        Generator that yields (line_number, line) tuples.
        
        Memory efficient - only one line in memory at a time.
        """
        try:
            with open(file_path, "r", encoding=encoding, errors="ignore") as f:
                for line_num, line in enumerate(f, 1):
                    yield line_num, line.rstrip("\n\r")
        except (IOError, OSError):
            return
    
    @staticmethod
    def read_chunks(file_path: str, chunk_size: int = 64 * 1024) -> Generator[bytes, None, None]:
        """
        Generator that yields file in chunks.
        
        Memory efficient - only chunk_size bytes in memory at a time.
        """
        try:
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        except (IOError, OSError):
            return
    
    @staticmethod
    def read_mmap(file_path: str) -> Generator[str, None, None]:
        """
        Memory-mapped file reading for very large files.
        
        Lets OS manage memory efficiently.
        """
        try:
            with open(file_path, "rb") as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    for line in iter(mm.readline, b""):
                        try:
                            yield line.decode("utf-8", errors="ignore").rstrip("\n\r")
                        except:
                            continue
        except (IOError, OSError, ValueError):
            return


# ==================== WORKER POOL MANAGER ====================

class WorkerPool:
    """
    Managed worker pool with limits.
    
    Features:
    - Thread pool for IO operations
    - Process pool for CPU-bound work
    - Automatic cleanup
    """
    
    def __init__(self, max_workers: int = 2):
        self._max_workers = max_workers
        self._thread_pool: Optional[ThreadPoolExecutor] = None
        self._process_pool: Optional[ProcessPoolExecutor] = None
        self._lock = threading.Lock()
    
    @property
    def threads(self) -> ThreadPoolExecutor:
        """Get or create thread pool"""
        with self._lock:
            if self._thread_pool is None:
                self._thread_pool = ThreadPoolExecutor(
                    max_workers=self._max_workers,
                    thread_name_prefix="xl_worker"
                )
            return self._thread_pool
    
    @property
    def processes(self) -> ProcessPoolExecutor:
        """Get or create process pool (limited)"""
        with self._lock:
            if self._process_pool is None:
                # Limit to 1-2 processes to save memory
                self._process_pool = ProcessPoolExecutor(
                    max_workers=min(self._max_workers, 2)
                )
            return self._process_pool
    
    def map_threads(self, func: Callable, items: List[Any]) -> List[Any]:
        """Map function over items using thread pool"""
        return list(self.threads.map(func, items))
    
    def submit_thread(self, func: Callable, *args, **kwargs):
        """Submit task to thread pool"""
        return self.threads.submit(func, *args, **kwargs)
    
    def shutdown(self):
        """Shutdown all pools"""
        with self._lock:
            if self._thread_pool:
                self._thread_pool.shutdown(wait=False)
                self._thread_pool = None
            if self._process_pool:
                self._process_pool.shutdown(wait=False)
                self._process_pool = None


# ==================== SMART MODULE UNLOADER ====================

class SmartUnloader:
    """
    Smart module unloading based on priority and memory.
    
    Features:
    - Priority-based unloading (low priority first)
    - Usage tracking (LRU unloading)
    - Memory-aware triggers
    """
    
    def __init__(self):
        self._loaded: OrderedDict[str, Any] = OrderedDict()
        self._priorities: Dict[str, int] = {}
        self._usage_count: Dict[str, int] = {}
        self._lock = threading.Lock()
    
    def register(self, name: str, module: Any, priority: int = 50):
        """Register a loaded module"""
        with self._lock:
            self._loaded[name] = module
            self._priorities[name] = priority
            self._usage_count[name] = 0
    
    def mark_used(self, name: str):
        """Mark module as used (updates LRU order)"""
        with self._lock:
            if name in self._loaded:
                self._loaded.move_to_end(name)
                self._usage_count[name] = self._usage_count.get(name, 0) + 1
    
    def unload_lru(self, keep: int = 2) -> List[str]:
        """Unload least recently used modules"""
        unloaded = []
        with self._lock:
            while len(self._loaded) > keep:
                name, module = self._loaded.popitem(last=False)
                del module
                unloaded.append(name)
        
        if unloaded:
            gc.collect()
        
        return unloaded
    
    def unload_by_priority(self, threshold: int = 30) -> List[str]:
        """Unload low priority modules"""
        unloaded = []
        with self._lock:
            to_remove = [
                name for name, pri in self._priorities.items()
                if pri < threshold and name in self._loaded
            ]
            for name in to_remove:
                del self._loaded[name]
                unloaded.append(name)
        
        if unloaded:
            gc.collect()
        
        return unloaded
    
    def unload_all(self):
        """Unload all modules"""
        with self._lock:
            self._loaded.clear()
            gc.collect()
    
    def get_loaded(self) -> List[str]:
        """Get list of loaded module names"""
        return list(self._loaded.keys())


# ==================== ASYNC IO MANAGER ====================

class AsyncIO:
    """
    Async IO operations where safe.
    
    Note: Uses thread pool for file IO since true async
    file IO is not available on all platforms.
    """
    
    def __init__(self, max_workers: int = 2):
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._loop: Optional[asyncio.AbstractEventLoop] = None
    
    async def read_file(self, path: str) -> str:
        """Async file read"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._sync_read,
            path
        )
    
    async def read_files(self, paths: List[str]) -> List[str]:
        """Read multiple files concurrently"""
        tasks = [self.read_file(p) for p in paths]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def _sync_read(self, path: str) -> str:
        """Sync file read"""
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except:
            return ""
    
    def shutdown(self):
        """Shutdown executor"""
        self._executor.shutdown(wait=False)


# ==================== MEMORY OPTIMIZER ====================

class MemoryOptimizer:
    """
    Central memory optimizer.
    
    Coordinates all optimization techniques.
    """
    
    def __init__(self):
        self._config = OptimizerConfig()
        self._file_cache = LRUFileCache(
            max_size_mb=self._config.max_cache_mb,
            max_items=self._config.max_cached_items
        )
        self._worker_pool = WorkerPool(self._config.max_workers)
        self._unloader = SmartUnloader()
        self._async_io = AsyncIO(self._config.max_workers)
        self._gc_runs = 0
        self._process = psutil.Process(os.getpid())
    
    def configure(self, **kwargs):
        """Update configuration"""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        
        # Update components
        self._file_cache = LRUFileCache(
            max_size_mb=self._config.max_cache_mb,
            max_items=self._config.max_cached_items
        )
        self._worker_pool = WorkerPool(self._config.max_workers)
    
    def get_usage_mb(self) -> float:
        """Get current memory usage in MB"""
        return self._process.memory_info().rss / (1024 * 1024)
    
    def check_memory(self) -> bool:
        """Check if memory is within limits"""
        usage = self.get_usage_mb()
        return usage < self._config.memory_limit_mb * self._config.gc_threshold
    
    def trigger_cleanup(self, aggressive: bool = False):
        """Trigger memory cleanup"""
        if aggressive:
            # Aggressive cleanup
            self._file_cache.clear()
            self._unloader.unload_lru(keep=1)
            gc.collect()
            gc.collect()
            self._gc_runs += 2
        else:
            # Light cleanup
            self._file_cache.evict_percent(0.5)
            gc.collect()
            self._gc_runs += 1
    
    def auto_cleanup(self):
        """Auto cleanup based on memory pressure"""
        usage = self.get_usage_mb()
        limit = self._config.memory_limit_mb
        
        if usage > limit * self._config.critical_threshold:
            self.trigger_cleanup(aggressive=True)
        elif usage > limit * self._config.gc_threshold:
            self.trigger_cleanup(aggressive=False)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get optimizer statistics"""
        return {
            "usage_mb": round(self.get_usage_mb(), 1),
            "limit_mb": self._config.memory_limit_mb,
            "usage_percent": round(self.get_usage_mb() / self._config.memory_limit_mb * 100, 1),
            "max_workers": self._config.max_workers,
            "gc_runs": self._gc_runs,
            "cache": self._file_cache.stats(),
            "loaded_modules": self._unloader.get_loaded()
        }
    
    def shutdown(self):
        """Cleanup all resources"""
        self._file_cache.clear()
        self._worker_pool.shutdown()
        self._unloader.unload_all()
        self._async_io.shutdown()
        gc.collect()
    
    # Expose components
    @property
    def cache(self) -> LRUFileCache:
        return self._file_cache
    
    @property
    def workers(self) -> WorkerPool:
        return self._worker_pool
    
    @property
    def unloader(self) -> SmartUnloader:
        return self._unloader
    
    @property
    def async_io(self) -> AsyncIO:
        return self._async_io


# ==================== BINARY FILTER ====================

class BinaryFilter:
    """Filter binary files to skip during analysis"""
    
    BINARY_EXTENSIONS = {
        # Images
        ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".bmp", ".svg",
        # Media
        ".mp3", ".mp4", ".wav", ".avi", ".mov", ".webm", ".ogg",
        # Archives
        ".zip", ".rar", ".tar", ".gz", ".7z", ".bz2",
        # Binaries
        ".dex", ".so", ".dll", ".exe", ".apk", ".jar", ".class", ".o",
        # Fonts
        ".ttf", ".otf", ".woff", ".woff2", ".eot",
        # Documents
        ".pdf", ".doc", ".docx",
    }
    
    @classmethod
    def should_skip(cls, path: str) -> bool:
        """Check if file should be skipped"""
        ext = Path(path).suffix.lower()
        return ext in cls.BINARY_EXTENSIONS
    
    @classmethod
    def filter_files(cls, paths: List[str]) -> Iterator[str]:
        """Generator that filters out binary files"""
        for path in paths:
            if not cls.should_skip(path):
                yield path


# ==================== DECORATORS ====================

def cached_result(maxsize: int = 128):
    """Decorator for caching function results"""
    def decorator(func):
        return lru_cache(maxsize=maxsize)(func)
    return decorator


def memory_check(optimizer: MemoryOptimizer):
    """Decorator to check memory before function execution"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            optimizer.auto_cleanup()
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ==================== SINGLETONS ====================

# Global optimizer instance
memory_optimizer = MemoryOptimizer()

# Convenience exports
file_cache = memory_optimizer.cache
streaming = StreamingReader()
