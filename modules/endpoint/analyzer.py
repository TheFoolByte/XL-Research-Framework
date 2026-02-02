"""
XL Research Framework - Endpoint Analyzer

Discovers network endpoints using streaming reads.
Stateless, JSON-compatible output.
"""

import re
from typing import Dict, Any, Set
from urllib.parse import urlparse
from pathlib import Path

from core.context import Context, AnalysisResult
from modules.base import BaseModule, Finding


class Analyzer(BaseModule):
    """
    Endpoint Finder - Discovers network URLs.
    
    Detects:
    - HTTP/HTTPS endpoints
    - WebSocket connections
    - XL-specific domains
    - Firebase/Cloud services
    - CDN endpoints
    """
    
    name = "endpoint_finder"
    description = "Network endpoint discovery"
    priority = 15
    
    # Domain categories
    DOMAIN_CATEGORIES = {
        "xl": ["xl.co.id", "xlaxiata", "myxl", "axis.co.id"],
        "firebase": ["firebase", "firebaseio.com", "fcm.googleapis"],
        "google": ["googleapis.com", "google.com", "gstatic.com"],
        "analytics": ["analytics", "crashlytics", "appsflyer", "adjust.com"],
        "aws": ["amazonaws.com", "s3.", "cloudfront"],
        "azure": ["azure", "blob.core.windows"],
    }
    
    PATTERNS = {
        "http_url": {
            "pattern": r'https?://[a-zA-Z0-9\-_.~:/?#\[\]@!$&\'()*+,;=%]+',
            "severity": "info",
        },
        "websocket": {
            "pattern": r'wss?://[a-zA-Z0-9\-_.~:/?#\[\]@!$&\'()*+,;=%]+',
            "severity": "medium",
        },
    }
    
    def __init__(self):
        super().__init__()
        self._compiled_patterns = self.compile_patterns(self.PATTERNS)
        self._seen_domains: Set[str] = set()
    
    def analyze(self, context: Context) -> AnalysisResult:
        """Find endpoints using streaming"""
        self.reset()
        self._seen_domains.clear()
        
        extensions = [".java", ".kt", ".json", ".xml", ".properties"]
        
        for file_info in context.iter_files(extensions=extensions):
            self.scan_file_streaming(context, file_info)
        
        # Stats
        xl_count = sum(1 for f in self._findings 
                       if f.metadata.get("is_xl", False))
        
        self._stats = {
            "unique_domains": len(self._seen_domains),
            "xl_endpoints": xl_count,
            "by_category": self._count_by_category(),
            "by_severity": self.group_by_severity()
        }
        
        return self.create_result()
    
    def on_match(self, pattern_name: str, match: re.Match,
                 line_num: int, file_path: str, line: str):
        """Process URL match with deduplication"""
        url = match.group(0)
        domain = self._extract_domain(url)
        
        # Skip duplicates
        if domain in self._seen_domains:
            return
        self._seen_domains.add(domain)
        
        category = self._categorize_domain(domain)
        is_xl = category == "xl"
        
        finding = Finding(
            category="Endpoint",
            type=pattern_name,
            message=f"{'[XL] ' if is_xl else ''}{url[:70]}",
            file_path=file_path,
            line_number=line_num,
            severity="high" if is_xl else "info",
            confidence="high",
            value=url[:300],
            context=line.strip()[:100],
            metadata={
                "domain": domain,
                "category": category,
                "is_xl": is_xl
            }
        )
        self.add_finding(finding)
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc or url[:50]
        except:
            return url[:50]
    
    def _categorize_domain(self, domain: str) -> str:
        """Categorize domain"""
        domain_lower = domain.lower()
        for category, patterns in self.DOMAIN_CATEGORIES.items():
            if any(p in domain_lower for p in patterns):
                return category
        return "generic"
    
    def _count_by_category(self) -> Dict[str, int]:
        """Count findings by category"""
        counts: Dict[str, int] = {}
        for f in self._findings:
            cat = f.metadata.get("category", "generic")
            counts[cat] = counts.get(cat, 0) + 1
        return counts
