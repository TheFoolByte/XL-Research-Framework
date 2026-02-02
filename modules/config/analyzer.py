"""
XL Research Framework - Config Analyzer (Env Extractor)

Extracts secrets and configuration using streaming reads.
Stateless, JSON-compatible output.
"""

import re
from typing import Dict, Any
from pathlib import Path

from core.context import Context, AnalysisResult
from modules.base import BaseModule, Finding


class Analyzer(BaseModule):
    """
    Env Extractor - Extracts configuration and secrets.
    
    Detects:
    - API keys (generic, Firebase, AWS)
    - Secret keys and tokens
    - Debug flags
    - Encryption keys
    - Database credentials
    - Environment variables
    """
    
    name = "env_extractor"
    description = "Environment and secrets extractor"
    priority = 25
    
    PATTERNS = {
        # API Keys
        "generic_api_key": {
            "pattern": r'api[_-]?key\s*[=:]\s*["\']([A-Za-z0-9_-]{16,})["\']',
            "severity": "critical",
        },
        "firebase_key": {
            "pattern": r'AIza[A-Za-z0-9_-]{35}',
            "severity": "high",
        },
        "fcm_key": {
            "pattern": r'AAAA[A-Za-z0-9_-]{30,}:APA91[A-Za-z0-9_-]{100,}',
            "severity": "high",
        },
        "aws_access_key": {
            "pattern": r'AKIA[A-Z0-9]{16}',
            "severity": "critical",
        },
        # Secrets
        "secret_key": {
            "pattern": r'secret[_-]?key\s*[=:]\s*["\']([^"\']{10,})["\']',
            "severity": "critical",
        },
        "private_key": {
            "pattern": r'private[_-]?key\s*[=:]\s*["\']([^"\']{10,})["\']',
            "severity": "critical",
        },
        "signing_key": {
            "pattern": r'signing[_-]?key\s*[=:]\s*["\']([^"\']{10,})["\']',
            "severity": "critical",
        },
        "pem_header": {
            "pattern": r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----',
            "severity": "critical",
        },
        # Debug
        "debug_true": {
            "pattern": r'DEBUG\s*=\s*(?:true|True|TRUE|1)',
            "severity": "high",
        },
        "debug_mode": {
            "pattern": r'(?:isDebug|debugMode|testMode)\s*=\s*true',
            "severity": "high",
        },
        "build_debug": {
            "pattern": r'BuildConfig\.DEBUG',
            "severity": "medium",
        },
        # Encryption
        "aes_key": {
            "pattern": r'aes[_-]?key\s*[=:]\s*["\']([A-Fa-f0-9]{32,})["\']',
            "severity": "critical",
        },
        "iv_vector": {
            "pattern": r'(?:iv|IV)\s*=\s*["\']([A-Fa-f0-9]{16,})["\']',
            "severity": "high",
        },
        # Database
        "jdbc_url": {
            "pattern": r'jdbc:[a-z]+://[^\s"\']+',
            "severity": "high",
        },
        "mongodb_url": {
            "pattern": r'mongodb(?:\+srv)?://[^\s"\']+',
            "severity": "high",
        },
        # Environment
        "getenv": {
            "pattern": r'getenv\s*\(\s*["\']([^"\']+)["\']',
            "severity": "low",
        },
        "build_config": {
            "pattern": r'BuildConfig\.([A-Z_]+)',
            "severity": "low",
        },
    }
    
    def __init__(self):
        super().__init__()
        self._compiled_patterns = self.compile_patterns(self.PATTERNS)
    
    def analyze(self, context: Context) -> AnalysisResult:
        """Extract secrets using streaming"""
        self.reset()
        
        extensions = [".java", ".kt", ".xml", ".json", ".properties", ".yaml", ".yml", ".gradle"]
        
        for file_info in context.iter_files(extensions=extensions):
            self.scan_file_streaming(context, file_info)
        
        # Stats
        critical_count = sum(1 for f in self._findings if f.severity == "critical")
        
        self._stats = {
            "critical_count": critical_count,
            "debug_enabled": self._check_debug(),
            "cloud_services": self._detect_cloud(),
            "by_type": self.group_by_type(),
            "by_severity": self.group_by_severity()
        }
        
        return self.create_result()
    
    def on_match(self, pattern_name: str, match: re.Match,
                 line_num: int, file_path: str, line: str):
        """Create finding with masking for secrets"""
        config = self.PATTERNS.get(pattern_name, {})
        severity = config.get("severity", "medium")
        
        # Mask critical values
        value = match.group(0)
        is_masked = severity == "critical"
        if is_masked and len(value) > 15:
            value = value[:10] + "***MASKED***"
        
        finding = Finding(
            category="Config",
            type=pattern_name,
            message=f"[{pattern_name}]",
            file_path=file_path,
            line_number=line_num,
            severity=severity,
            confidence="high",
            value=value[:80],
            context=line.strip()[:60],
            metadata={"masked": is_masked}
        )
        self.add_finding(finding)
    
    def _check_debug(self) -> bool:
        """Check if debug is enabled"""
        return any(f.type == "debug_true" for f in self._findings)
    
    def _detect_cloud(self) -> list:
        """Detect cloud services"""
        services = set()
        for f in self._findings:
            if "firebase" in f.type:
                services.add("firebase")
            elif "aws" in f.type:
                services.add("aws")
            elif "mongodb" in f.type:
                services.add("mongodb")
        return list(services)
