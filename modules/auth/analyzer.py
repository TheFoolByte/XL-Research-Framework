"""
XL Research Framework - Auth Analyzer

Analyzes authentication patterns using streaming reads.
Stateless, JSON-compatible output.
"""

import re
from typing import Dict, Any
from pathlib import Path

from core.context import Context, AnalysisResult
from modules.base import BaseModule, Finding


class Analyzer(BaseModule):
    """
    Auth Flow - Analyzes authentication patterns.
    
    Detects:
    - OAuth/OAuth2 flows
    - JWT tokens and handling
    - Session management
    - Credential storage
    - Biometric auth
    - Mobile auth (OTP, MSISDN)
    """
    
    name = "auth_flow"
    description = "Authentication flow analyzer"
    priority = 20
    
    PATTERNS = {
        # OAuth
        "oauth_impl": {
            "pattern": r'oauth|OAuth2?|OAUTH',
            "severity": "medium",
        },
        "client_id": {
            "pattern": r'client[_-]?id\s*[=:]\s*["\']([^"\']{10,})["\']',
            "severity": "high",
        },
        "client_secret": {
            "pattern": r'client[_-]?secret\s*[=:]\s*["\']([^"\']{10,})["\']',
            "severity": "critical",
        },
        # JWT
        "jwt_token": {
            "pattern": r'eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.',
            "severity": "critical",
        },
        "bearer_token": {
            "pattern": r'Bearer\s+[A-Za-z0-9_-]{20,}',
            "severity": "high",
        },
        "refresh_token": {
            "pattern": r'refresh[_-]?token\s*[=:]',
            "severity": "high",
        },
        "access_token": {
            "pattern": r'access[_-]?token\s*[=:]',
            "severity": "high",
        },
        # Session
        "session_id": {
            "pattern": r'session[_-]?id|JSESSIONID|PHPSESSID',
            "severity": "high",
        },
        "shared_prefs_auth": {
            "pattern": r'SharedPreferences.*(?:token|auth|session)',
            "severity": "high",
        },
        # Credentials
        "hardcoded_password": {
            "pattern": r'password\s*[=:]\s*["\']([^"\']{4,})["\']',
            "severity": "critical",
        },
        "pin_code": {
            "pattern": r'(?:pin|PIN)[_-]?(?:code|Code)?\s*[=:]\s*["\'](\d{4,})["\']',
            "severity": "critical",
        },
        # Biometric
        "biometric": {
            "pattern": r'BiometricPrompt|FingerprintManager|fingerprint',
            "severity": "medium",
        },
        # Mobile
        "otp_code": {
            "pattern": r'otp|OTP|one[_-]?time[_-]?password',
            "severity": "medium",
        },
        "msisdn": {
            "pattern": r'msisdn|MSISDN|phone[_-]?number',
            "severity": "high",
        },
    }
    
    def __init__(self):
        super().__init__()
        self._compiled_patterns = self.compile_patterns(self.PATTERNS)
    
    def analyze(self, context: Context) -> AnalysisResult:
        """Analyze auth patterns using streaming"""
        self.reset()
        
        extensions = [".java", ".kt", ".xml", ".json", ".properties"]
        
        for file_info in context.iter_files(extensions=extensions):
            self.scan_file_streaming(context, file_info)
        
        # Stats
        critical_count = sum(1 for f in self._findings if f.severity == "critical")
        
        self._stats = {
            "critical_count": critical_count,
            "auth_methods": self._detect_auth_methods(),
            "by_type": self.group_by_type(),
            "by_severity": self.group_by_severity()
        }
        
        return self.create_result()
    
    def on_match(self, pattern_name: str, match: re.Match,
                 line_num: int, file_path: str, line: str):
        """Create finding with masking for sensitive values"""
        config = self.PATTERNS.get(pattern_name, {})
        severity = config.get("severity", "medium")
        
        # Mask critical values
        value = match.group(0)
        is_sensitive = severity == "critical"
        if is_sensitive and len(value) > 15:
            value = value[:10] + "***MASKED***"
        
        finding = Finding(
            category="Auth",
            type=pattern_name,
            message=f"[{pattern_name}] {match.group(0)[:40]}",
            file_path=file_path,
            line_number=line_num,
            severity=severity,
            confidence="high",
            value=value[:100],
            context=line.strip()[:80],
            metadata={"is_sensitive": is_sensitive}
        )
        self.add_finding(finding)
    
    def _detect_auth_methods(self) -> list:
        """Detect auth methods used"""
        methods = set()
        for f in self._findings:
            if "oauth" in f.type:
                methods.add("oauth")
            elif "jwt" in f.type or "bearer" in f.type:
                methods.add("jwt")
            elif "biometric" in f.type:
                methods.add("biometric")
            elif "otp" in f.type or "msisdn" in f.type:
                methods.add("mobile")
            elif "session" in f.type:
                methods.add("session")
        return list(methods)
