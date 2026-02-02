"""
XL Research Framework - API Analyzer

Detects API patterns using streaming reads.
Stateless, JSON-compatible output.
"""

import re
from typing import Dict, Any
from pathlib import Path

from core.context import Context, AnalysisResult
from modules.base import BaseModule, Finding


class Analyzer(BaseModule):
    """
    API Scanner - Detects REST, GraphQL, and API patterns.
    
    Scans for:
    - REST endpoints (GET, POST, PUT, DELETE)
    - GraphQL queries/mutations
    - Retrofit annotations
    - Base URL configurations
    - API versioning
    """
    
    name = "api_scanner"
    description = "API endpoint scanner"
    priority = 10
    
    PATTERNS = {
        "rest_endpoint": {
            "pattern": r'["\']/(api|v[0-9]+)/[a-zA-Z0-9/_-]+["\']',
            "severity": "high",
            "confidence": "high"
        },
        "retrofit_get": {
            "pattern": r'@GET\s*\(\s*["\']([^"\']+)["\']',
            "severity": "high",
            "confidence": "high"
        },
        "retrofit_post": {
            "pattern": r'@POST\s*\(\s*["\']([^"\']+)["\']',
            "severity": "high",
            "confidence": "high"
        },
        "retrofit_put": {
            "pattern": r'@PUT\s*\(\s*["\']([^"\']+)["\']',
            "severity": "medium",
            "confidence": "high"
        },
        "retrofit_delete": {
            "pattern": r'@DELETE\s*\(\s*["\']([^"\']+)["\']',
            "severity": "medium",
            "confidence": "high"
        },
        "base_url": {
            "pattern": r'(?:BASE_URL|baseUrl|API_URL)\s*[=:]\s*["\']([^"\']+)["\']',
            "severity": "high",
            "confidence": "high"
        },
        "graphql_operation": {
            "pattern": r'(?:query|mutation|subscription)\s+\w+\s*[({]',
            "severity": "medium",
            "confidence": "high"
        },
        "api_version": {
            "pattern": r'["\']v[0-9]+(?:\.[0-9]+)?["\']',
            "severity": "low",
            "confidence": "medium"
        },
    }
    
    def __init__(self):
        super().__init__()
        self._compiled_patterns = self.compile_patterns(self.PATTERNS)
    
    def analyze(self, context: Context) -> AnalysisResult:
        """Scan sources for API patterns using streaming"""
        self.reset()
        
        extensions = [".java", ".kt", ".json", ".xml"]
        
        for file_info in context.iter_files(extensions=extensions):
            self.scan_file_streaming(context, file_info)
        
        # Build stats
        self._stats = {
            "by_type": self.group_by_type(),
            "by_severity": self.group_by_severity()
        }
        
        return self.create_result()
    
    def on_match(self, pattern_name: str, match: re.Match,
                 line_num: int, file_path: str, line: str):
        """Create finding from match"""
        config = self.PATTERNS.get(pattern_name, {})
        
        finding = Finding(
            category="API",
            type=pattern_name,
            message=f"{pattern_name}: {match.group(0)[:60]}",
            file_path=file_path,
            line_number=line_num,
            severity=config.get("severity", "medium"),
            confidence=config.get("confidence", "medium"),
            value=match.group(0)[:200],
            context=line.strip()[:100]
        )
        self.add_finding(finding)
