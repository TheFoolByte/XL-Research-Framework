"""
XL Research Framework - Correlation Engine

Correlates findings across modules to discover:
- Related endpoints and auth patterns
- API key exposure chains
- Data flow paths
- Security vulnerability chains
"""

from typing import Dict, List, Any, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import re


@dataclass
class Correlation:
    """A correlation between findings"""
    type: str  # chain, exposure, flow, related
    severity: str
    source_module: str
    target_module: str
    source_finding: Dict
    target_finding: Dict
    confidence: float  # 0.0 - 1.0
    description: str
    risk_increase: int = 0


class CorrelationEngine:
    """
    Correlates findings across modules to discover security patterns.
    
    Correlation Types:
    - chain: Sequential dependencies (API → Auth → Endpoint)
    - exposure: Sensitive data exposure paths
    - flow: Data flow between components
    - related: Related findings in same file/class
    """
    
    def __init__(self):
        self._correlations: List[Correlation] = []
        self._findings_by_file: Dict[str, List[Tuple[str, Dict]]] = defaultdict(list)
        self._findings_by_domain: Dict[str, List[Tuple[str, Dict]]] = defaultdict(list)
        self._findings_by_type: Dict[str, List[Tuple[str, Dict]]] = defaultdict(list)
    
    def analyze(self, results: Dict[str, Any]) -> List[Correlation]:
        """
        Analyze results and find correlations.
        
        Args:
            results: Results dict from Engine
            
        Returns:
            List of correlations
        """
        self._correlations.clear()
        self._index_findings(results)
        
        # Run correlation checks
        self._correlate_by_file()
        self._correlate_api_auth()
        self._correlate_endpoint_secrets()
        self._correlate_xl_flow()
        
        return self._correlations
    
    def _index_findings(self, results: Dict[str, Any]):
        """Index findings for fast correlation"""
        self._findings_by_file.clear()
        self._findings_by_domain.clear()
        self._findings_by_type.clear()
        
        for module_name, module_data in results.get("results", {}).items():
            for finding in module_data.get("findings", []):
                # Index by file
                file_path = finding.get("file", "")
                if file_path:
                    self._findings_by_file[file_path].append((module_name, finding))
                
                # Index by domain
                domain = self._extract_domain(finding)
                if domain:
                    self._findings_by_domain[domain].append((module_name, finding))
                
                # Index by type
                finding_type = finding.get("type", "")
                if finding_type:
                    self._findings_by_type[finding_type].append((module_name, finding))
    
    def _extract_domain(self, finding: Dict) -> str:
        """Extract domain from finding"""
        for field in ["domain", "url", "value"]:
            value = finding.get(field, "")
            if value:
                match = re.search(r'https?://([^/]+)', str(value))
                if match:
                    return match.group(1)
        return ""
    
    def _correlate_by_file(self):
        """Find related findings in same file"""
        for file_path, findings in self._findings_by_file.items():
            if len(findings) < 2:
                continue
            
            # Group by module
            modules = set(f[0] for f in findings)
            
            if len(modules) >= 2:
                # Findings from multiple modules in same file
                severity_map = {"critical": 4, "high": 3, "medium": 2, "low": 1}
                max_severity = max(
                    severity_map.get(f[1].get("severity", "low"), 1) 
                    for f in findings
                )
                
                self._correlations.append(Correlation(
                    type="related",
                    severity=["low", "low", "medium", "high", "critical"][max_severity],
                    source_module=findings[0][0],
                    target_module=findings[1][0],
                    source_finding=findings[0][1],
                    target_finding=findings[1][1],
                    confidence=0.7,
                    description=f"Multiple security patterns in {file_path}",
                    risk_increase=5
                ))
    
    def _correlate_api_auth(self):
        """Correlate API endpoints with auth findings"""
        api_findings = self._findings_by_type.get("base_url", []) + \
                       self._findings_by_type.get("rest_endpoint", [])
        auth_findings = self._findings_by_type.get("jwt_token", []) + \
                       self._findings_by_type.get("api_key", [])
        
        for api_module, api_finding in api_findings:
            api_domain = self._extract_domain(api_finding)
            
            for auth_module, auth_finding in auth_findings:
                auth_file = auth_finding.get("file", "")
                api_file = api_finding.get("file", "")
                
                # Same file or related
                if api_file and (api_file == auth_file or 
                                 api_file.split("/")[-1].replace(".java", "") in auth_file):
                    self._correlations.append(Correlation(
                        type="chain",
                        severity="high",
                        source_module=api_module,
                        target_module=auth_module,
                        source_finding=api_finding,
                        target_finding=auth_finding,
                        confidence=0.85,
                        description=f"API endpoint uses exposed auth token",
                        risk_increase=15
                    ))
    
    def _correlate_endpoint_secrets(self):
        """Find secrets exposed alongside endpoints"""
        secret_types = ["secret_key", "private_key", "client_secret", "api_key"]
        endpoint_types = ["rest_endpoint", "base_url", "retrofit_get", "retrofit_post"]
        
        # Get secrets and endpoints by file
        for file_path, findings in self._findings_by_file.items():
            has_secret = any(f[1].get("type") in secret_types for f in findings)
            has_endpoint = any(f[1].get("type") in endpoint_types for f in findings)
            
            if has_secret and has_endpoint:
                secret_finding = next(f for f in findings if f[1].get("type") in secret_types)
                endpoint_finding = next(f for f in findings if f[1].get("type") in endpoint_types)
                
                self._correlations.append(Correlation(
                    type="exposure",
                    severity="critical",
                    source_module=secret_finding[0],
                    target_module=endpoint_finding[0],
                    source_finding=secret_finding[1],
                    target_finding=endpoint_finding[1],
                    confidence=0.95,
                    description=f"Secret exposed in same file as API endpoint",
                    risk_increase=25
                ))
    
    def _correlate_xl_flow(self):
        """Correlate XL-specific data flows"""
        # Find XL endpoints
        xl_endpoints = [
            (m, f) for domain, findings in self._findings_by_domain.items()
            for m, f in findings
            if "xl" in domain.lower() or "axiata" in domain.lower()
        ]
        
        # Find family logic
        family_findings = []
        for type_name in ["prepaid", "postpaid", "plan_type", "quota"]:
            family_findings.extend(self._findings_by_type.get(type_name, []))
        
        # Correlate XL endpoints with family logic
        for ep_module, ep_finding in xl_endpoints:
            ep_file = ep_finding.get("file", "")
            
            for fam_module, fam_finding in family_findings:
                fam_file = fam_finding.get("file", "")
                
                # Same package/directory
                if ep_file and fam_file:
                    ep_package = "/".join(ep_file.split("/")[:-1])
                    fam_package = "/".join(fam_file.split("/")[:-1])
                    
                    if ep_package == fam_package:
                        self._correlations.append(Correlation(
                            type="flow",
                            severity="medium",
                            source_module=ep_module,
                            target_module=fam_module,
                            source_finding=ep_finding,
                            target_finding=fam_finding,
                            confidence=0.75,
                            description=f"XL endpoint connected to plan logic",
                            risk_increase=10
                        ))
    
    def get_summary(self) -> Dict:
        """Get correlation summary"""
        by_type = defaultdict(int)
        by_severity = defaultdict(int)
        total_risk = 0
        
        for corr in self._correlations:
            by_type[corr.type] += 1
            by_severity[corr.severity] += 1
            total_risk += corr.risk_increase
        
        return {
            "total": len(self._correlations),
            "by_type": dict(by_type),
            "by_severity": dict(by_severity),
            "risk_increase": total_risk,
            "top_correlations": [
                {
                    "type": c.type,
                    "severity": c.severity,
                    "description": c.description,
                    "confidence": c.confidence
                }
                for c in sorted(self._correlations, key=lambda x: x.risk_increase, reverse=True)[:5]
            ]
        }
    
    def to_json(self) -> List[Dict]:
        """Export correlations as JSON"""
        return [
            {
                "type": c.type,
                "severity": c.severity,
                "source_module": c.source_module,
                "target_module": c.target_module,
                "source_finding": {
                    "type": c.source_finding.get("type"),
                    "file": c.source_finding.get("file"),
                },
                "target_finding": {
                    "type": c.target_finding.get("type"),
                    "file": c.target_finding.get("file"),
                },
                "confidence": c.confidence,
                "description": c.description,
                "risk_increase": c.risk_increase
            }
            for c in self._correlations
        ]


# Singleton
correlation_engine = CorrelationEngine()
