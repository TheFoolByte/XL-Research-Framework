"""
XL Research Framework - Family Analyzer

Detects XL-specific business logic using streaming reads.
Stateless, JSON-compatible output.
"""

import re
from typing import Dict, Any
from pathlib import Path

from core.context import Context, AnalysisResult
from modules.base import BaseModule, Finding


class Analyzer(BaseModule):
    """
    Family Logic - XL-specific business logic analyzer.
    
    Detects:
    - Plan types (prepaid/postpaid)
    - Quota management
    - Promo/voucher systems
    - Loyalty programs
    - Balance handling
    - USSD codes
    - XL products
    """
    
    name = "family_logic"
    description = "XL family and plan logic analyzer"
    priority = 30
    
    PATTERNS = {
        # Plan types
        "prepaid": {
            "pattern": r'prepaid|prabayar|PREPAID',
            "severity": "high",
            "category": "plan"
        },
        "postpaid": {
            "pattern": r'postpaid|pascabayar|POSTPAID',
            "severity": "high",
            "category": "plan"
        },
        "plan_type": {
            "pattern": r'planType|plan[_-]?type|subscriberType',
            "severity": "high",
            "category": "plan"
        },
        # Quota
        "data_quota": {
            "pattern": r'kuota|quota|internet[_-]?quota|data[_-]?quota',
            "severity": "medium",
            "category": "quota"
        },
        "remaining_quota": {
            "pattern": r'remaining[_-]?quota|sisa[_-]?kuota',
            "severity": "medium",
            "category": "quota"
        },
        # Promo
        "promo": {
            "pattern": r'promo(?:tion)?|PROMO',
            "severity": "medium",
            "category": "promo"
        },
        "voucher": {
            "pattern": r'voucher|VOUCHER|kupon|kode[_-]?promo',
            "severity": "medium",
            "category": "promo"
        },
        "discount": {
            "pattern": r'discount|diskon|potongan|cashback',
            "severity": "medium",
            "category": "promo"
        },
        # Loyalty
        "loyalty": {
            "pattern": r'loyalty|LOYALTY|member[_-]?point|poin',
            "severity": "medium",
            "category": "loyalty"
        },
        "tier": {
            "pattern": r'tier|TIER|silver|gold|platinum',
            "severity": "low",
            "category": "loyalty"
        },
        # Balance
        "balance": {
            "pattern": r'balance|saldo|BALANCE',
            "severity": "high",
            "category": "balance"
        },
        "pulsa": {
            "pattern": r'pulsa|credit|PULSA',
            "severity": "high",
            "category": "balance"
        },
        "topup": {
            "pattern": r'topup|top[_-]?up|isi[_-]?ulang',
            "severity": "medium",
            "category": "balance"
        },
        # USSD
        "ussd_code": {
            "pattern": r'\*\d{2,4}[#*]',
            "severity": "high",
            "category": "ussd"
        },
        # Products
        "xtra_product": {
            "pattern": r'XTRA|xtra|Xtra(?:Combo|Kuota)?',
            "severity": "medium",
            "category": "product"
        },
        "combo_product": {
            "pattern": r'COMBO|combo|Combo(?:Plus|Lite)?',
            "severity": "medium",
            "category": "product"
        },
        "hotrod_product": {
            "pattern": r'HOTROD|hotrod|Hotrod',
            "severity": "medium",
            "category": "product"
        },
    }
    
    def __init__(self):
        super().__init__()
        self._compiled_patterns = self.compile_patterns(self.PATTERNS)
    
    def analyze(self, context: Context) -> AnalysisResult:
        """Analyze XL family logic using streaming"""
        self.reset()
        
        extensions = [".java", ".kt", ".json", ".xml"]
        
        for file_info in context.iter_files(extensions=extensions):
            self.scan_file_streaming(context, file_info)
        
        # Stats
        self._stats = {
            "has_prepaid": any(f.type == "prepaid" for f in self._findings),
            "has_postpaid": any(f.type == "postpaid" for f in self._findings),
            "by_category": self._group_by_category(),
            "by_type": self.group_by_type()
        }
        
        return self.create_result()
    
    def on_match(self, pattern_name: str, match: re.Match,
                 line_num: int, file_path: str, line: str):
        """Create XL-specific finding"""
        config = self.PATTERNS.get(pattern_name, {})
        category = config.get("category", "other")
        
        finding = Finding(
            category="Family",
            type=pattern_name,
            message=f"[{category}] {pattern_name}: {match.group(0)[:30]}",
            file_path=file_path,
            line_number=line_num,
            severity=config.get("severity", "medium"),
            confidence="high",
            value=match.group(0),
            context=line.strip()[:80],
            metadata={"category": category}
        )
        self.add_finding(finding)
    
    def _group_by_category(self) -> Dict[str, int]:
        """Group findings by XL category"""
        counts: Dict[str, int] = {}
        for f in self._findings:
            cat = f.metadata.get("category", "other")
            counts[cat] = counts.get(cat, 0) + 1
        return counts
