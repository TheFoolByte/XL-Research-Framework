"""
XL Research Framework - Advanced Correlator System

Correlates findings across modules to produce linked insights.

Detections:
- API → Auth relations
- Auth → Family relations  
- Endpoint → Payment chains
- Secret exposure paths

Output: Explainable, human-readable insights with evidence.
"""

from typing import Dict, List, Any, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import re


@dataclass
class Insight:
    """
    A correlated insight with explanation.
    
    Explainable: includes evidence and risk assessment.
    """
    id: str
    title: str
    description: str
    chain_type: str  # api_auth, auth_family, endpoint_payment, exposure
    severity: str
    confidence: float
    risk_score: int  # 0-100
    
    # Evidence
    source_module: str
    source_findings: List[Dict] = field(default_factory=list)
    target_module: str = ""
    target_findings: List[Dict] = field(default_factory=list)
    
    # Files involved
    files: List[str] = field(default_factory=list)
    
    # Explanation
    explanation: str = ""
    impact: str = ""
    recommendation: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """JSON-serializable output"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "chain_type": self.chain_type,
            "severity": self.severity,
            "confidence": self.confidence,
            "risk_score": self.risk_score,
            "source_module": self.source_module,
            "target_module": self.target_module,
            "files": self.files[:5],
            "explanation": self.explanation,
            "impact": self.impact,
            "recommendation": self.recommendation,
            "evidence_count": len(self.source_findings) + len(self.target_findings)
        }
    
    def explain(self) -> str:
        """Human-readable explanation"""
        lines = [
            f"{'='*60}",
            f"INSIGHT: {self.title}",
            f"{'='*60}",
            f"",
            f"Type: {self.chain_type}",
            f"Severity: {self.severity.upper()}  |  Risk Score: {self.risk_score}/100",
            f"Confidence: {self.confidence:.0%}",
            f"",
            f"DESCRIPTION:",
            f"  {self.description}",
            f"",
            f"CHAIN:",
            f"  {self.source_module} → {self.target_module}",
            f"",
            f"FILES INVOLVED:",
        ]
        for f in self.files[:3]:
            lines.append(f"  • {f}")
        
        if self.explanation:
            lines.extend([
                f"",
                f"EXPLANATION:",
                f"  {self.explanation}",
            ])
        
        if self.impact:
            lines.extend([
                f"",
                f"IMPACT:",
                f"  {self.impact}",
            ])
        
        if self.recommendation:
            lines.extend([
                f"",
                f"RECOMMENDATION:",
                f"  {self.recommendation}",
            ])
        
        return "\n".join(lines)


class Correlator:
    """
    Advanced correlator that links findings across modules.
    
    Detection Chains:
    1. API → Auth: API endpoints using exposed auth tokens
    2. Auth → Family: Auth patterns connected to plan logic
    3. Endpoint → Payment: Network calls to payment services
    4. Exposure: Secrets exposed alongside endpoints
    
    Output: Explainable insights with evidence and recommendations.
    """
    
    def __init__(self):
        self._insights: List[Insight] = []
        self._findings_by_file: Dict[str, List[Tuple[str, Dict]]] = defaultdict(list)
        self._findings_by_module: Dict[str, List[Dict]] = defaultdict(list)
        self._insight_counter = 0
    
    def correlate(self, results: Dict[str, Any]) -> List[Insight]:
        """
        Correlate findings from all modules.
        
        Args:
            results: Results dict from Engine with 'results' key
            
        Returns:
            List of Insight objects with explanations
        """
        self._insights.clear()
        self._insight_counter = 0
        
        # Index findings
        self._index_findings(results)
        
        # Run correlation chains
        self._detect_api_auth_chain()
        self._detect_auth_family_chain()
        self._detect_endpoint_payment_chain()
        self._detect_exposure_chain()
        self._detect_same_file_relations()
        
        # Sort by risk score
        self._insights.sort(key=lambda x: x.risk_score, reverse=True)
        
        return self._insights
    
    def _index_findings(self, results: Dict[str, Any]):
        """Index findings by file and module"""
        self._findings_by_file.clear()
        self._findings_by_module.clear()
        
        for module_name, module_data in results.get("results", {}).items():
            findings = module_data.get("findings", [])
            self._findings_by_module[module_name] = findings
            
            for finding in findings:
                file_path = finding.get("file", "")
                if file_path:
                    self._findings_by_file[file_path].append((module_name, finding))
    
    def _next_id(self) -> str:
        """Generate insight ID"""
        self._insight_counter += 1
        return f"INS-{self._insight_counter:03d}"
    
    # ==================== DETECTION CHAINS ====================
    
    def _detect_api_auth_chain(self):
        """
        Detect API → Auth relations.
        
        Pattern: API endpoints that use or expose auth mechanisms.
        """
        api_findings = self._findings_by_module.get("api_scanner", [])
        auth_findings = self._findings_by_module.get("auth_flow", [])
        
        if not api_findings or not auth_findings:
            return
        
        # Find API files with auth patterns
        for api in api_findings:
            api_file = api.get("file", "")
            if not api_file:
                continue
            
            # Check auth findings in same file
            related_auth = [
                f for m, f in self._findings_by_file.get(api_file, [])
                if m == "auth_flow"
            ]
            
            if related_auth:
                # Check for token exposure
                has_token = any(
                    "token" in f.get("type", "").lower() or 
                    "bearer" in f.get("type", "").lower()
                    for f in related_auth
                )
                
                has_secret = any(
                    f.get("severity") == "critical"
                    for f in related_auth
                )
                
                if has_token or has_secret:
                    insight = Insight(
                        id=self._next_id(),
                        title="API with Exposed Authentication",
                        description=f"API endpoint in {api_file.split('/')[-1]} uses tokens that may be exposed",
                        chain_type="api_auth",
                        severity="high" if has_secret else "medium",
                        confidence=0.85,
                        risk_score=75 if has_secret else 50,
                        source_module="api_scanner",
                        source_findings=[api],
                        target_module="auth_flow",
                        target_findings=related_auth,
                        files=[api_file],
                        explanation="This API endpoint has authentication tokens defined in the same file. "
                                   "If the token is hardcoded or logged, it could be extracted.",
                        impact="Attackers could intercept or extract tokens to make unauthorized API calls.",
                        recommendation="Use secure token storage (Android Keystore) and avoid logging tokens."
                    )
                    self._insights.append(insight)
    
    def _detect_auth_family_chain(self):
        """
        Detect Auth → Family relations.
        
        Pattern: Authentication tied to plan/subscriber logic.
        """
        auth_findings = self._findings_by_module.get("auth_flow", [])
        family_findings = self._findings_by_module.get("family_logic", [])
        
        if not auth_findings or not family_findings:
            return
        
        # Find auth patterns with plan type logic
        auth_files = set(f.get("file", "") for f in auth_findings if f.get("file"))
        family_files = set(f.get("file", "") for f in family_findings if f.get("file"))
        
        # Same package analysis
        for auth_file in auth_files:
            auth_pkg = "/".join(auth_file.split("/")[:-1])
            
            related_family_files = [
                f for f in family_files
                if "/".join(f.split("/")[:-1]) == auth_pkg
            ]
            
            if related_family_files:
                # Get related family findings
                related_family = [
                    f for f in family_findings
                    if f.get("file") in related_family_files
                ]
                
                # Check for plan-based auth
                has_plan = any(
                    f.get("metadata", {}).get("category") == "plan"
                    for f in related_family
                )
                
                if has_plan:
                    insight = Insight(
                        id=self._next_id(),
                        title="Plan-Based Authentication Flow",
                        description=f"Authentication logic is tied to subscriber plan type",
                        chain_type="auth_family",
                        severity="medium",
                        confidence=0.75,
                        risk_score=45,
                        source_module="auth_flow",
                        source_findings=[f for f in auth_findings if f.get("file") == auth_file],
                        target_module="family_logic",
                        target_findings=related_family[:3],
                        files=[auth_file] + related_family_files[:2],
                        explanation="The authentication system appears to check subscriber plan type "
                                   "(prepaid/postpaid) which may affect access control.",
                        impact="Different user types may have different security levels or bypass routes.",
                        recommendation="Ensure consistent security regardless of plan type."
                    )
                    self._insights.append(insight)
    
    def _detect_endpoint_payment_chain(self):
        """
        Detect Endpoint → Payment chains.
        
        Pattern: Network endpoints related to payment/transaction.
        """
        endpoint_findings = self._findings_by_module.get("endpoint_finder", [])
        
        if not endpoint_findings:
            return
        
        # Payment keywords
        payment_keywords = [
            "payment", "pay", "transaction", "billing", "topup", 
            "purchase", "checkout", "order", "invoice"
        ]
        
        payment_endpoints = []
        for ep in endpoint_findings:
            value = ep.get("value", "").lower()
            if any(kw in value for kw in payment_keywords):
                payment_endpoints.append(ep)
        
        if payment_endpoints:
            # Group by domain
            by_domain = defaultdict(list)
            for ep in payment_endpoints:
                domain = ep.get("metadata", {}).get("domain", "unknown")
                by_domain[domain].append(ep)
            
            for domain, eps in by_domain.items():
                insight = Insight(
                    id=self._next_id(),
                    title=f"Payment Endpoint Chain: {domain[:30]}",
                    description=f"Found {len(eps)} payment-related endpoints on {domain}",
                    chain_type="endpoint_payment",
                    severity="high",
                    confidence=0.90,
                    risk_score=70,
                    source_module="endpoint_finder",
                    source_findings=eps[:5],
                    target_module="",
                    files=list(set(ep.get("file", "") for ep in eps))[:3],
                    explanation=f"Multiple payment-related API calls to {domain}. "
                               "These handle financial transactions.",
                    impact="Compromise of these endpoints could lead to financial fraud or data theft.",
                    recommendation="Ensure SSL pinning, proper authentication, and request signing."
                )
                self._insights.append(insight)
    
    def _detect_exposure_chain(self):
        """
        Detect secret exposure paths.
        
        Pattern: Secrets in same file as API endpoints.
        """
        env_findings = self._findings_by_module.get("env_extractor", [])
        endpoint_findings = self._findings_by_module.get("endpoint_finder", [])
        
        if not env_findings:
            return
        
        # Critical secrets
        critical_secrets = [
            f for f in env_findings
            if f.get("severity") == "critical"
        ]
        
        for secret in critical_secrets:
            secret_file = secret.get("file", "")
            
            # Check for endpoints in same file
            related_endpoints = [
                f for m, f in self._findings_by_file.get(secret_file, [])
                if m == "endpoint_finder"
            ]
            
            if related_endpoints:
                insight = Insight(
                    id=self._next_id(),
                    title=f"Critical Secret Near Endpoint",
                    description=f"Secret '{secret.get('type')}' found alongside API endpoints",
                    chain_type="exposure",
                    severity="critical",
                    confidence=0.95,
                    risk_score=90,
                    source_module="env_extractor",
                    source_findings=[secret],
                    target_module="endpoint_finder",
                    target_findings=related_endpoints[:3],
                    files=[secret_file],
                    explanation=f"A critical secret ({secret.get('type')}) is defined in the same file "
                               "as network endpoints. This creates an exposure path.",
                    impact="Attackers could extract the secret and use it to access protected APIs.",
                    recommendation="Move secrets to secure storage. Never hardcode in source files."
                )
                self._insights.append(insight)
    
    def _detect_same_file_relations(self):
        """Detect multiple security patterns in same file"""
        for file_path, findings in self._findings_by_file.items():
            modules = set(m for m, _ in findings)
            
            # File with 3+ different module findings = complex security
            if len(modules) >= 3:
                severities = [f.get("severity", "info") for _, f in findings]
                has_critical = "critical" in severities
                has_high = "high" in severities
                
                if has_critical or has_high:
                    insight = Insight(
                        id=self._next_id(),
                        title=f"Security Hotspot: {file_path.split('/')[-1]}",
                        description=f"Multiple security patterns ({len(modules)} types) in single file",
                        chain_type="hotspot",
                        severity="high" if has_critical else "medium",
                        confidence=0.80,
                        risk_score=65 if has_critical else 40,
                        source_module=list(modules)[0],
                        source_findings=[f for _, f in findings[:5]],
                        files=[file_path],
                        explanation=f"This file contains findings from {len(modules)} different security areas: "
                                   f"{', '.join(modules)}. High-risk concentration.",
                        impact="Concentrated security logic may have interconnected vulnerabilities.",
                        recommendation="Review file carefully. Consider separating concerns."
                    )
                    self._insights.append(insight)
    
    # ==================== OUTPUT ====================
    
    def get_summary(self) -> Dict[str, Any]:
        """Get correlation summary"""
        by_type = defaultdict(int)
        by_severity = defaultdict(int)
        total_risk = 0
        
        for insight in self._insights:
            by_type[insight.chain_type] += 1
            by_severity[insight.severity] += 1
            total_risk += insight.risk_score
        
        return {
            "total_insights": len(self._insights),
            "by_chain_type": dict(by_type),
            "by_severity": dict(by_severity),
            "total_risk_score": total_risk,
            "avg_risk_score": round(total_risk / len(self._insights), 1) if self._insights else 0,
            "top_insights": [i.to_dict() for i in self._insights[:5]]
        }
    
    def explain_all(self) -> str:
        """Get human-readable explanation of all insights"""
        if not self._insights:
            return "No correlations detected."
        
        lines = [
            "=" * 70,
            "          CORRELATION ANALYSIS REPORT",
            "=" * 70,
            "",
            f"Total Insights: {len(self._insights)}",
            f"Critical: {sum(1 for i in self._insights if i.severity == 'critical')}",
            f"High: {sum(1 for i in self._insights if i.severity == 'high')}",
            "",
        ]
        
        for insight in self._insights:
            lines.append(insight.explain())
            lines.append("")
        
        return "\n".join(lines)
    
    def to_json(self) -> List[Dict]:
        """Export all insights as JSON"""
        return [i.to_dict() for i in self._insights]


# Singleton
correlator = Correlator()
