"""
XL Research Framework - Advanced Report Generator

Generates comprehensive, human-readable reports with:
- API keys summary
- Endpoints mapping  
- Auth flow analysis
- Family logic detection
- Risk scoring

Output formats: TXT (human-readable) + JSON (structured)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

from core.config import config
from core.logger import log


@dataclass
class RiskScore:
    """Risk scoring results"""
    total_score: int = 0
    max_score: int = 100
    level: str = "low"  # low, medium, high, critical
    breakdown: Dict[str, int] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ReportData:
    """Structured report data"""
    apk_name: str
    package: str = ""
    timestamp: str = ""
    profile: str = ""
    duration: float = 0.0
    
    # Summaries
    api_keys: List[Dict] = field(default_factory=list)
    endpoints: List[Dict] = field(default_factory=list)
    auth_flow: Dict = field(default_factory=dict)
    family_logic: Dict = field(default_factory=dict)
    
    # Risk
    risk: RiskScore = field(default_factory=RiskScore)
    
    # Stats
    total_findings: int = 0
    critical_findings: int = 0


class ReportGenerator:
    """
    Advanced report generator with risk scoring.
    
    Features:
    - Human-readable TXT format
    - Structured JSON export
    - Risk scoring system
    - Categorized findings
    """
    
    # Risk weights
    RISK_WEIGHTS = {
        "critical": 25,
        "high": 15,
        "medium": 5,
        "low": 1,
    }
    
    def __init__(self, results: Dict[str, Any], context=None, manifest=None):
        self.results = results
        self.context = context
        self.manifest = manifest
        self.report = ReportData(
            apk_name=results.get("apk", "Unknown"),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            profile=results.get("profile", "unknown"),
            duration=results.get("duration_seconds", 0),
        )
        
        if manifest:
            self.report.package = getattr(manifest, 'package', '')
    
    def generate(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        Generate both TXT and JSON reports.
        
        Returns:
            Dict with 'txt' and 'json' paths
        """
        # Process results
        self._extract_api_keys()
        self._extract_endpoints()
        self._analyze_auth()
        self._analyze_family()
        self._calculate_risk()
        
        # Determine output paths
        if output_dir:
            out = Path(output_dir)
        else:
            out = config.reports_dir
        
        out.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{self.report.apk_name}_{timestamp}"
        
        # Generate reports
        txt_path = out / f"{base_name}_report.txt"
        json_path = out / f"{base_name}_report.json"
        
        self._write_txt(txt_path)
        self._write_json(json_path)
        
        return {
            "txt": str(txt_path),
            "json": str(json_path)
        }
    
    def _extract_api_keys(self):
        """Extract API keys from results"""
        keys = []
        
        for name, result in self.results.get("results", {}).items():
            for finding in result.get("findings", []):
                if any(k in finding.get("type", "").lower() for k in ["key", "secret", "token"]):
                    keys.append({
                        "type": finding.get("type", ""),
                        "value": finding.get("value", "")[:50] + "...",
                        "file": finding.get("file", ""),
                        "severity": finding.get("severity", "medium")
                    })
        
        self.report.api_keys = keys[:20]  # Limit
        self.report.critical_findings += sum(1 for k in keys if k["severity"] == "critical")
    
    def _extract_endpoints(self):
        """Extract endpoints from results"""
        endpoints = []
        
        result = self.results.get("results", {}).get("endpoint_finder", {})
        for finding in result.get("findings", [])[:30]:
            endpoints.append({
                "url": finding.get("url", ""),
                "domain": finding.get("domain", ""),
                "category": finding.get("category", ""),
                "is_xl": finding.get("is_xl", False)
            })
        
        self.report.endpoints = endpoints
    
    def _analyze_auth(self):
        """Analyze authentication patterns"""
        result = self.results.get("results", {}).get("auth_flow", {})
        
        findings = result.get("findings", [])
        
        self.report.auth_flow = {
            "total": len(findings),
            "methods": list(set(f.get("category", "") for f in findings)),
            "has_oauth": any(f.get("category") == "oauth" for f in findings),
            "has_jwt": any(f.get("category") == "jwt" for f in findings),
            "has_biometric": any(f.get("category") == "biometric" for f in findings),
            "sensitive_count": sum(1 for f in findings if f.get("is_sensitive")),
            "top_findings": findings[:5]
        }
    
    def _analyze_family(self):
        """Analyze XL family logic"""
        result = self.results.get("results", {}).get("family_logic", {})
        
        findings = result.get("findings", [])
        
        # Group by category
        by_category = {}
        for f in findings:
            cat = f.get("category", "other")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(f)
        
        self.report.family_logic = {
            "total": len(findings),
            "categories": list(by_category.keys()),
            "has_prepaid": any(f.get("type") == "prepaid" for f in findings),
            "has_postpaid": any(f.get("type") == "postpaid" for f in findings),
            "has_quota": any(f.get("category") == "quota" for f in findings),
            "has_promo": any(f.get("category") == "promo" for f in findings),
            "by_category": {k: len(v) for k, v in by_category.items()},
            "top_findings": findings[:5]
        }
    
    def _calculate_risk(self):
        """Calculate risk score"""
        score = 0
        breakdown = {}
        recommendations = []
        
        # Count by severity
        for name, result in self.results.get("results", {}).items():
            for finding in result.get("findings", []):
                severity = finding.get("severity", "low")
                weight = self.RISK_WEIGHTS.get(severity, 1)
                score += weight
                breakdown[severity] = breakdown.get(severity, 0) + 1
        
        # Cap at 100
        score = min(score, 100)
        
        # Determine level
        if score >= 75:
            level = "critical"
        elif score >= 50:
            level = "high"
        elif score >= 25:
            level = "medium"
        else:
            level = "low"
        
        # Generate recommendations
        if breakdown.get("critical", 0) > 0:
            recommendations.append("URGENT: Remove hardcoded secrets/API keys")
        if self.report.auth_flow.get("has_oauth") and breakdown.get("critical", 0) > 0:
            recommendations.append("Review OAuth client secret exposure")
        if any("debug" in str(f).lower() for f in self.report.api_keys):
            recommendations.append("Disable debug mode in production")
        
        self.report.risk = RiskScore(
            total_score=score,
            level=level,
            breakdown=breakdown,
            recommendations=recommendations
        )
        
        self.report.total_findings = sum(breakdown.values())
    
    def _write_txt(self, path: Path):
        """Write human-readable TXT report"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(self._generate_txt())
        log.success(f"TXT report: {path}")
    
    def _write_json(self, path: Path):
        """Write JSON report"""
        data = {
            "meta": {
                "apk": self.report.apk_name,
                "package": self.report.package,
                "timestamp": self.report.timestamp,
                "profile": self.report.profile,
                "duration_seconds": self.report.duration,
            },
            "summary": {
                "total_findings": self.report.total_findings,
                "critical_findings": self.report.critical_findings,
                "risk_score": self.report.risk.total_score,
                "risk_level": self.report.risk.level,
            },
            "api_keys": self.report.api_keys,
            "endpoints": self.report.endpoints,
            "auth_flow": self.report.auth_flow,
            "family_logic": self.report.family_logic,
            "risk": asdict(self.report.risk),
        }
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        log.success(f"JSON report: {path}")
    
    def _generate_txt(self) -> str:
        """Generate human-readable TXT content"""
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append("         XL RESEARCH FRAMEWORK - ANALYSIS REPORT")
        lines.append("=" * 70)
        lines.append("")
        
        # Meta
        lines.append(f"APK:       {self.report.apk_name}")
        lines.append(f"Package:   {self.report.package or 'N/A'}")
        lines.append(f"Profile:   {self.report.profile}")
        lines.append(f"Analyzed:  {self.report.timestamp}")
        lines.append(f"Duration:  {self.report.duration:.1f}s")
        lines.append("")
        
        # Risk Score
        lines.append("-" * 70)
        lines.append("                      RISK ASSESSMENT")
        lines.append("-" * 70)
        lines.append("")
        
        risk = self.report.risk
        risk_bar = self._render_risk_bar(risk.total_score)
        
        lines.append(f"  RISK SCORE:  {risk.total_score}/100  [{risk.level.upper()}]")
        lines.append(f"  {risk_bar}")
        lines.append("")
        
        lines.append("  Breakdown:")
        for sev, count in risk.breakdown.items():
            lines.append(f"    • {sev.upper():10} {count:3} findings")
        lines.append("")
        
        if risk.recommendations:
            lines.append("  ⚠️  Recommendations:")
            for rec in risk.recommendations:
                lines.append(f"    → {rec}")
            lines.append("")
        
        # API Keys
        lines.append("-" * 70)
        lines.append("                        API KEYS")
        lines.append("-" * 70)
        lines.append("")
        
        if self.report.api_keys:
            for key in self.report.api_keys[:10]:
                sev = key["severity"][:4].upper()
                lines.append(f"  [{sev}] {key['type']}")
                lines.append(f"         Value: {key['value']}")
                lines.append(f"         File:  {key['file']}")
                lines.append("")
        else:
            lines.append("  No API keys detected.")
            lines.append("")
        
        # Endpoints
        lines.append("-" * 70)
        lines.append("                       ENDPOINTS")
        lines.append("-" * 70)
        lines.append("")
        
        if self.report.endpoints:
            xl_endpoints = [e for e in self.report.endpoints if e.get("is_xl")]
            other_endpoints = [e for e in self.report.endpoints if not e.get("is_xl")]
            
            if xl_endpoints:
                lines.append("  🔷 XL Endpoints:")
                for ep in xl_endpoints[:5]:
                    lines.append(f"     • {ep['url'][:60]}")
                lines.append("")
            
            if other_endpoints:
                lines.append("  📡 Other Endpoints:")
                for ep in other_endpoints[:10]:
                    lines.append(f"     • [{ep['category']:8}] {ep['domain']}")
                lines.append("")
        else:
            lines.append("  No endpoints detected.")
            lines.append("")
        
        # Auth Flow
        lines.append("-" * 70)
        lines.append("                      AUTH FLOW")
        lines.append("-" * 70)
        lines.append("")
        
        auth = self.report.auth_flow
        if auth.get("total", 0) > 0:
            lines.append(f"  Total auth patterns: {auth.get('total', 0)}")
            lines.append(f"  Auth methods: {', '.join(auth.get('methods', []))}")
            lines.append("")
            lines.append("  Detection:")
            lines.append(f"    • OAuth:    {'✓' if auth.get('has_oauth') else '✗'}")
            lines.append(f"    • JWT:      {'✓' if auth.get('has_jwt') else '✗'}")
            lines.append(f"    • Biometric: {'✓' if auth.get('has_biometric') else '✗'}")
            lines.append("")
        else:
            lines.append("  No auth patterns detected.")
            lines.append("")
        
        # Family Logic
        lines.append("-" * 70)
        lines.append("                     FAMILY LOGIC")
        lines.append("-" * 70)
        lines.append("")
        
        family = self.report.family_logic
        if family.get("total", 0) > 0:
            lines.append(f"  Total patterns: {family.get('total', 0)}")
            lines.append("")
            lines.append("  Plan Types:")
            lines.append(f"    • Prepaid:  {'✓' if family.get('has_prepaid') else '✗'}")
            lines.append(f"    • Postpaid: {'✓' if family.get('has_postpaid') else '✗'}")
            lines.append("")
            lines.append("  Features:")
            lines.append(f"    • Quota:    {'✓' if family.get('has_quota') else '✗'}")
            lines.append(f"    • Promo:    {'✓' if family.get('has_promo') else '✗'}")
            lines.append("")
            
            lines.append("  By Category:")
            for cat, count in family.get("by_category", {}).items():
                lines.append(f"    • {cat:12} {count:3}")
            lines.append("")
        else:
            lines.append("  No family logic detected.")
            lines.append("")
        
        # Footer
        lines.append("=" * 70)
        lines.append("                     END OF REPORT")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def _render_risk_bar(self, score: int) -> str:
        """Render visual risk bar"""
        filled = int(score / 5)  # 20 chars total
        empty = 20 - filled
        
        if score >= 75:
            char = "█"
        elif score >= 50:
            char = "▓"
        elif score >= 25:
            char = "▒"
        else:
            char = "░"
        
        return f"  [{char * filled}{'░' * empty}]"


def generate_report(results: Dict, context=None, manifest=None, output_dir=None) -> Dict[str, str]:
    """
    Convenience function to generate reports.
    
    Args:
        results: Analysis results from Engine
        context: Optional Context
        manifest: Optional ManifestInfo
        output_dir: Optional output directory
        
    Returns:
        Dict with 'txt' and 'json' paths
    """
    generator = ReportGenerator(results, context, manifest)
    return generator.generate(output_dir)
