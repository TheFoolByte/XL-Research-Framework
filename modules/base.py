"""
XL Research Framework v2.1 - Base Module

Abstract base class for all analysis modules with:
- Streaming file support
- JSON-compatible output
- Stateless design
- Profile limit awareness
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Iterator, Optional
from pathlib import Path
import re

from core.context import Context, AnalysisResult, FileInfo


@dataclass
class Finding:
    """
    Represents a single finding.
    
    All fields are JSON-serializable.
    """
    category: str
    message: str
    type: str = ""
    file_path: str = ""
    line_number: int = 0
    severity: str = "info"  # critical, high, medium, low, info
    confidence: str = "medium"  # high, medium, low
    value: str = ""
    context: str = ""
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-compatible dict"""
        return {
            "category": self.category,
            "type": self.type,
            "message": self.message[:200],
            "file": self.file_path,
            "line": self.line_number,
            "severity": self.severity,
            "confidence": self.confidence,
            "value": self.value[:500] if self.value else "",
            "context": self.context[:200] if self.context else "",
            "metadata": self.metadata
        }


class BaseModule(ABC):
    """
    Abstract base class for analysis modules.
    
    Design Principles:
    - Stateless: reset() before each analysis
    - Streaming: use iter_lines for large files
    - JSON output: all findings are serializable
    - Profile-aware: respect memory/file limits
    
    Usage:
        class MyAnalyzer(BaseModule):
            name = "my_analyzer"
            description = "My analyzer"
            
            def analyze(self, context: Context) -> AnalysisResult:
                self.reset()
                for file_info in context.iter_files(['.java']):
                    self.scan_file_streaming(context, file_info)
                return self.create_result()
    """
    
    # Module metadata
    name: str = "base"
    description: str = "Base module"
    priority: int = 50  # Lower = runs first
    
    # Pattern configuration
    PATTERNS: Dict[str, Dict[str, Any]] = {}
    
    def __init__(self):
        self._findings: List[Finding] = []
        self._errors: List[str] = []
        self._stats: Dict[str, Any] = {}
        self._compiled_patterns: Dict[str, re.Pattern] = {}
    
    @abstractmethod
    def analyze(self, context: Context) -> AnalysisResult:
        """
        Run analysis on context.
        
        Args:
            context: Analysis context with file access
            
        Returns:
            AnalysisResult with findings
        """
        pass
    
    def reset(self):
        """Reset state before analysis (stateless design)"""
        self._findings.clear()
        self._errors.clear()
        self._stats.clear()
    
    def add_finding(self, finding: Finding):
        """Add a finding"""
        self._findings.append(finding)
    
    def add_error(self, error: str):
        """Add an error"""
        self._errors.append(error)
    
    def create_result(self) -> AnalysisResult:
        """Create JSON-compatible result"""
        result = AnalysisResult(analyzer_name=self.name)
        result.findings = [f.to_dict() for f in self._findings]
        result.errors = self._errors.copy()
        result.stats = {
            "total": len(self._findings),
            **self._stats
        }
        return result
    
    # ==================== STREAMING HELPERS ====================
    
    def scan_file_streaming(self, context: Context, file_info: FileInfo,
                           patterns: Optional[Dict[str, re.Pattern]] = None):
        """
        Scan file using streaming line-by-line reads.
        
        Memory efficient for large files.
        
        Args:
            context: Analysis context
            file_info: File to scan
            patterns: Compiled regex patterns to match
        """
        if patterns is None:
            patterns = self._compiled_patterns
        
        for line_num, line in context.read_file_lines(file_info):
            self.process_line(line, line_num, file_info.relative_path, patterns)
    
    def process_line(self, line: str, line_num: int, file_path: str,
                    patterns: Dict[str, re.Pattern]):
        """
        Process a single line against patterns.
        
        Override in subclass for custom logic.
        """
        for pattern_name, regex in patterns.items():
            for match in regex.finditer(line):
                self.on_match(pattern_name, match, line_num, file_path, line)
    
    def on_match(self, pattern_name: str, match: re.Match, 
                 line_num: int, file_path: str, line: str):
        """
        Handle a pattern match.
        
        Override in subclass for custom finding creation.
        """
        finding = Finding(
            category=self.name,
            type=pattern_name,
            message=f"{pattern_name}: {match.group(0)[:50]}",
            file_path=file_path,
            line_number=line_num,
            value=match.group(0),
            context=line.strip()[:100]
        )
        self.add_finding(finding)
    
    def compile_patterns(self, patterns: Dict[str, Dict[str, Any]]) -> Dict[str, re.Pattern]:
        """Compile pattern dict to regex objects"""
        compiled = {}
        for name, config in patterns.items():
            if isinstance(config, dict):
                pattern = config.get("pattern", "")
                flags = config.get("flags", re.IGNORECASE)
            else:
                pattern = config
                flags = re.IGNORECASE
            
            if pattern:
                compiled[name] = re.compile(pattern, flags)
        
        return compiled
    
    # ==================== JSON HELPERS ====================
    
    def to_json(self) -> Dict[str, Any]:
        """Export module results as JSON dict"""
        return {
            "module": self.name,
            "description": self.description,
            "total": len(self._findings),
            "stats": self._stats,
            "findings": [f.to_dict() for f in self._findings],
            "errors": self._errors
        }
    
    def group_by_type(self) -> Dict[str, int]:
        """Group findings by type"""
        counts: Dict[str, int] = {}
        for f in self._findings:
            counts[f.type] = counts.get(f.type, 0) + 1
        return counts
    
    def group_by_severity(self) -> Dict[str, int]:
        """Group findings by severity"""
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for f in self._findings:
            if f.severity in counts:
                counts[f.severity] += 1
        return counts
