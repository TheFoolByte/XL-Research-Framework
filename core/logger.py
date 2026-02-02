"""
XL Research Framework v2 - Logging Utilities

Structured logging with verbosity levels and colored output.
"""

import sys
import logging
from datetime import datetime
from typing import Optional
from enum import IntEnum


class LogLevel(IntEnum):
    """Log verbosity levels"""
    QUIET = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4
    TRACE = 5


# ANSI color codes
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    BOLD = "\033[1m"


class Logger:
    """
    Custom logger for XL Research Framework.
    
    Features:
    - Colored console output
    - Verbosity levels
    - Progress indicators
    - Structured output
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._level = LogLevel.INFO
        self._use_colors = sys.stdout.isatty()
        self._prefix = "XLRF"
    
    def set_level(self, level: LogLevel):
        """Set logging verbosity level"""
        self._level = level
    
    def set_quiet(self):
        """Set to quiet mode (errors only)"""
        self._level = LogLevel.QUIET
    
    def set_verbose(self):
        """Set to verbose mode"""
        self._level = LogLevel.DEBUG
    
    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled"""
        if self._use_colors:
            return f"{color}{text}{Colors.RESET}"
        return text
    
    def _format_time(self) -> str:
        """Format current time"""
        return datetime.now().strftime("%H:%M:%S")
    
    def _log(self, level: LogLevel, symbol: str, color: str, message: str):
        """Internal log method"""
        if level > self._level:
            return
        
        time_str = self._colorize(self._format_time(), Colors.GRAY)
        symbol_str = self._colorize(f"[{symbol}]", color)
        
        print(f"{time_str} {symbol_str} {message}")
    
    def info(self, message: str):
        """Log info message"""
        self._log(LogLevel.INFO, "+", Colors.GREEN, message)
    
    def success(self, message: str):
        """Log success message"""
        self._log(LogLevel.INFO, "✓", Colors.GREEN + Colors.BOLD, message)
    
    def warning(self, message: str):
        """Log warning message"""
        self._log(LogLevel.WARNING, "!", Colors.YELLOW, message)
    
    def error(self, message: str):
        """Log error message"""
        self._log(LogLevel.ERROR, "✗", Colors.RED, message)
    
    def debug(self, message: str):
        """Log debug message"""
        self._log(LogLevel.DEBUG, "~", Colors.CYAN, message)
    
    def trace(self, message: str):
        """Log trace message (very verbose)"""
        self._log(LogLevel.TRACE, ".", Colors.GRAY, message)
    
    def header(self, title: str):
        """Print a header section"""
        if self._level < LogLevel.INFO:
            return
        
        width = 60
        border = self._colorize("=" * width, Colors.BLUE)
        title_line = title.center(width)
        
        print()
        print(border)
        print(self._colorize(title_line, Colors.BOLD + Colors.BLUE))
        print(border)
    
    def section(self, title: str):
        """Print a section header"""
        if self._level < LogLevel.INFO:
            return
        
        line = self._colorize("-" * 50, Colors.GRAY)
        title_str = self._colorize(f"  {title}  ", Colors.BOLD)
        
        print()
        print(f"{line}")
        print(title_str)
        print(f"{line}")
    
    def progress(self, current: int, total: int, prefix: str = "Progress"):
        """Show progress indicator"""
        if self._level < LogLevel.INFO:
            return
        
        percent = int(current / total * 100) if total > 0 else 0
        bar_len = 30
        filled = int(bar_len * current / total) if total > 0 else 0
        
        bar = "█" * filled + "░" * (bar_len - filled)
        bar_colored = self._colorize(bar, Colors.CYAN)
        
        # Use carriage return for in-place update
        print(f"\r{prefix}: {bar_colored} {percent:3d}% ({current}/{total})", end="", flush=True)
        
        if current >= total:
            print()  # Newline when complete
    
    def table(self, headers: list, rows: list):
        """Print a formatted table"""
        if self._level < LogLevel.INFO:
            return
        
        # Calculate column widths
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(str(cell)))
        
        # Print header
        header_str = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
        print(self._colorize(header_str, Colors.BOLD))
        print("-" * len(header_str))
        
        # Print rows
        for row in rows:
            row_str = " | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))
            print(row_str)
    
    def finding(self, category: str, message: str, severity: str = "info"):
        """Log a finding with category"""
        color = {
            "critical": Colors.RED + Colors.BOLD,
            "high": Colors.RED,
            "medium": Colors.YELLOW,
            "low": Colors.CYAN,
            "info": Colors.WHITE
        }.get(severity.lower(), Colors.WHITE)
        
        cat_str = self._colorize(f"[{category}]", Colors.MAGENTA)
        sev_str = self._colorize(f"({severity})", color)
        
        print(f"  {cat_str} {sev_str} {message}")


# Singleton instance
log = Logger()
