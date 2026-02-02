"""
XL Research Framework v2 - Execution Context (Optimized)

Memory-efficient execution context with:
- Streaming file reads
- Binary asset filtering
- LRU caching
- Automatic memory management
"""

import os
import gc
import psutil
from pathlib import Path
from typing import Iterator, List, Optional, Set, Dict, Any, Tuple, Generator
from dataclasses import dataclass, field
from contextlib import contextmanager


@dataclass
class AnalysisResult:
    """Result from an analyzer"""
    analyzer_name: str
    findings: List[Dict[str, Any]] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    def add_finding(self, finding: Dict[str, Any]):
        self.findings.append(finding)
    
    def add_error(self, error: str):
        self.errors.append(error)
    
    @property
    def count(self) -> int:
        return len(self.findings)
    
    @property
    def has_findings(self) -> bool:
        return len(self.findings) > 0


@dataclass
class FileInfo:
    """Information about a file"""
    path: str
    relative_path: str
    name: str
    extension: str
    size_bytes: int
    
    @property
    def size_mb(self) -> float:
        return self.size_bytes / (1024 * 1024)


# Binary extensions to skip
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".bmp", ".svg",
    ".mp3", ".mp4", ".wav", ".avi", ".mov", ".webm", ".ogg",
    ".zip", ".rar", ".tar", ".gz", ".7z", ".bz2",
    ".dex", ".so", ".dll", ".exe", ".apk", ".jar", ".class", ".o",
    ".ttf", ".otf", ".woff", ".woff2", ".eot",
    ".pdf", ".doc", ".docx",
}


class Context:
    """
    Memory-efficient execution context.
    
    Uses generators for file iteration (no preloading).
    Implements streaming reads for large files.
    Includes LRU cache with size limits.
    """
    
    def __init__(self, apk_path: str, source_dir: Optional[str] = None):
        self._apk_path = apk_path
        self._source_dir = source_dir or ""
        self._apk_name = os.path.basename(apk_path)
        
        # Cache with LRU eviction
        self._file_cache: Dict[str, str] = {}
        self._cache_order: List[str] = []
        self._max_cache_items = 50
        self._max_cache_size_mb = 128
        self._current_cache_size = 0
        
        # Stats
        self._files_scanned = 0
        self._files_skipped = 0
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Config reference
        self._config = None
    
    @property
    def apk_path(self) -> str:
        return self._apk_path
    
    @property
    def apk_name(self) -> str:
        return self._apk_name
    
    @property
    def source_dir(self) -> str:
        return self._source_dir
    
    @property
    def files_scanned(self) -> int:
        return self._files_scanned
    
    # ==================== GENERATOR-BASED ITERATION ====================
    
    def iter_files(self, extensions: Optional[List[str]] = None,
                   max_size_mb: float = 10) -> Iterator[FileInfo]:
        """
        Generator that yields files one at a time.
        
        Memory efficient - never loads full file list.
        
        Args:
            extensions: File extensions to include (e.g., ['.java', '.kt'])
            max_size_mb: Skip files larger than this
        """
        if not self._source_dir or not os.path.isdir(self._source_dir):
            return
        
        max_size_bytes = int(max_size_mb * 1024 * 1024)
        
        for root, _, files in os.walk(self._source_dir):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                ext = Path(file_name).suffix.lower()
                
                # Skip binary
                if ext in BINARY_EXTENSIONS:
                    self._files_skipped += 1
                    continue
                
                # Extension filter
                if extensions and ext not in extensions:
                    continue
                
                # Size check
                try:
                    size = os.path.getsize(file_path)
                    if size > max_size_bytes:
                        self._files_skipped += 1
                        continue
                except OSError:
                    continue
                
                self._files_scanned += 1
                
                yield FileInfo(
                    path=file_path,
                    relative_path=os.path.relpath(file_path, self._source_dir),
                    name=file_name,
                    extension=ext,
                    size_bytes=size
                )
    
    # ==================== STREAMING READS ====================
    
    def read_file_lines(self, file_info: FileInfo) -> Generator[Tuple[int, str], None, None]:
        """
        Generator that yields (line_number, line) tuples.
        
        Memory efficient - only one line in memory at a time.
        """
        try:
            with open(file_info.path, "r", encoding="utf-8", errors="ignore") as f:
                for line_num, line in enumerate(f, 1):
                    yield line_num, line.rstrip("\n\r")
        except (IOError, OSError):
            return
    
    def read_file(self, file_info: FileInfo, use_cache: bool = True) -> Optional[str]:
        """
        Read file with LRU caching.
        
        Args:
            file_info: File to read
            use_cache: Whether to use cache
        """
        path = file_info.path
        
        # Check cache
        if use_cache and path in self._file_cache:
            self._cache_hits += 1
            # Move to end (most recently used)
            self._cache_order.remove(path)
            self._cache_order.append(path)
            return self._file_cache[path]
        
        self._cache_misses += 1
        
        # Read file
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except (IOError, OSError):
            return None
        
        # Cache if small enough
        if use_cache and file_info.size_mb < 5:
            self._cache_put(path, content)
        
        return content
    
    def _cache_put(self, path: str, content: str):
        """Add to cache with LRU eviction"""
        size_mb = len(content.encode("utf-8")) / (1024 * 1024)
        
        # Evict if needed
        while (len(self._file_cache) >= self._max_cache_items or
               self._current_cache_size + size_mb > self._max_cache_size_mb):
            if not self._cache_order:
                break
            old_path = self._cache_order.pop(0)
            if old_path in self._file_cache:
                old_content = self._file_cache.pop(old_path)
                self._current_cache_size -= len(old_content.encode("utf-8")) / (1024 * 1024)
        
        # Add to cache
        self._file_cache[path] = content
        self._cache_order.append(path)
        self._current_cache_size += size_mb
    
    # ==================== CLEANUP ====================
    
    def cleanup_cache(self):
        """Clear file cache"""
        self._file_cache.clear()
        self._cache_order.clear()
        self._current_cache_size = 0
        gc.collect()
    
    def cleanup(self):
        """Full cleanup"""
        self.cleanup_cache()
        gc.collect()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get context statistics"""
        hit_rate = (self._cache_hits / (self._cache_hits + self._cache_misses) 
                   if (self._cache_hits + self._cache_misses) > 0 else 0)
        return {
            "files_scanned": self._files_scanned,
            "files_skipped": self._files_skipped,
            "cache_items": len(self._file_cache),
            "cache_size_mb": round(self._current_cache_size, 2),
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate": round(hit_rate, 2)
        }


# Context manager for analysis
@contextmanager
def analysis_context(apk_path: str, source_dir: Optional[str] = None):
    """
    Context manager for analysis.
    
    Ensures cleanup on exit.
    """
    ctx = Context(apk_path, source_dir)
    try:
        yield ctx
    finally:
        ctx.cleanup()
