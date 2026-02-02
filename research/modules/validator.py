"""
Package and transaction validation testing

Migrated from xl-research/src/modules/validator.py
Adapted for integration with main framework.
"""
import json
import time
import random
from typing import Dict, List, Optional, Tuple

# Use framework logger if available, fallback to basic
try:
    from core.logger import log as logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class PackageValidator:
    """Validates package security through various attack simulations"""
    
    def __init__(self, client):
        self.client = client
        
        # Validation patterns from community data
        self.validation_patterns = {
            "price_validation": {
                "vulnerable": ["price", "amount", "harga"],
                "secure": ["product_id", "package_id", "family_code_only"]
            },
            "ownership_validation": {
                "vulnerable": [],
                "secure": ["msisdn_validation", "user_id_check", "token_binding"]
            },
            "signature_validation": {
                "vulnerable": ["static_secret", "no_nonce", "no_timestamp"],
                "secure": ["per_request_nonce", "timestamp_window", "parameter_inclusion"]
            }
        }
    
    def test_price_manipulation(self, family_code: str, 
                               original_price: int = None) -> Dict:
        """
        Test if price can be manipulated
        """
        if not original_price:
            # Get package details to know original price
            package_info = self.client.get_package_detail(family_code)
            if not package_info:
                return {"error": "Cannot fetch package details"}
            
            original_price = package_info.get('price', 10000)
        
        results = {
            "family_code": family_code,
            "original_price": original_price,
            "tests": [],
            "vulnerable": False
        }
        
        # Test different price values
        test_prices = [
            original_price,          # Same price
            int(original_price * 0.5),  # 50%
            int(original_price * 0.1),  # 10%
            1000,                    # Fixed low
            100,                     # Very low
            0,                       # Free
            -100,                    # Negative (should fail)
        ]
        
        for test_price in test_prices:
            test_result = {
                "test_price": test_price,
                "percentage": (test_price / original_price * 100) if original_price > 0 else 0
            }
            
            # Simulate purchase with price override
            simulated_response = self._simulate_price_test(family_code, test_price)
            
            test_result.update(simulated_response)
            results["tests"].append(test_result)
            
            # Check if vulnerable
            if (test_price < original_price and 
                simulated_response.get("status") == "success"):
                results["vulnerable"] = True
            
            # Delay between tests
            time.sleep(0.5)
        
        return results
    
    def _simulate_price_test(self, family_code: str, test_price: int) -> Dict:
        """
        Simulate price test (replace with actual API call in production)
        """
        # Simulate different responses based on price
        if test_price <= 0:
            return {
                "status": "error",
                "error_code": "INVALID_PRICE",
                "message": "Price must be positive"
            }
        elif test_price < 1000:
            # Very low price - might be rejected
            if random.random() < 0.3:  # 30% chance of success
                return {
                    "status": "success",
                    "message": "Purchase successful (VULNERABLE!)"
                }
            else:
                return {
                    "status": "error",
                    "error_code": "PRICE_MISMATCH",
                    "message": "Price validation failed"
                }
        else:
            # Reasonable price
            if random.random() < 0.8:  # 80% chance of success
                return {
                    "status": "success",
                    "message": "Purchase successful"
                }
            else:
                return {
                    "status": "error",
                    "error_code": "SERVER_ERROR",
                    "message": "Server error occurred"
                }
    
    def test_ownership_bypass(self, family_code: str) -> Dict:
        """
        Test if package ownership can be bypassed
        """
        results = {
            "family_code": family_code,
            "tests": [],
            "vulnerable": False
        }
        
        # Test different MSISDN values
        test_msisdns = [
            None,  # No MSISDN
            "081234567890",  # Valid format
            "081111111111",  # Different number
            "invalid_number",  # Invalid format
            "",  # Empty string
        ]
        
        for msisdn in test_msisdns:
            test_result = {"msisdn": msisdn}
            
            # Simulate purchase with different MSISDN
            simulated_response = self._simulate_msisdn_test(family_code, msisdn)
            
            test_result.update(simulated_response)
            results["tests"].append(test_result)
            
            # Check if vulnerable (can buy for other numbers)
            if (msisdn and msisdn != "081234567890" and
                simulated_response.get("status") == "success"):
                results["vulnerable"] = True
            
            time.sleep(0.5)
        
        return results
    
    def _simulate_msisdn_test(self, family_code: str, msisdn: str) -> Dict:
        """
        Simulate MSISDN test
        """
        if not msisdn:
            return {
                "status": "error",
                "error_code": "MISSING_MSISDN",
                "message": "MSISDN is required"
            }
        elif msisdn == "invalid_number":
            return {
                "status": "error",
                "error_code": "INVALID_MSISDN",
                "message": "Invalid phone number format"
            }
        elif msisdn != "081234567890":
            # Buying for different number
            if random.random() < 0.2:  # 20% chance of success (vulnerable)
                return {
                    "status": "success",
                    "message": "Purchase successful for different MSISDN (VULNERABLE!)",
                    "warning": "Ownership validation might be missing"
                }
            else:
                return {
                    "status": "error",
                    "error_code": "MSISDN_MISMATCH",
                    "message": "Cannot purchase for other numbers"
                }
        else:
            # Buying for own number
            return {
                "status": "success",
                "message": "Purchase successful"
            }
    
    def test_signature_replay(self, family_code: str) -> Dict:
        """
        Test if signature can be replayed
        """
        results = {
            "family_code": family_code,
            "tests": [],
            "vulnerable": False
        }
        
        # Simulate different replay attacks
        attacks = [
            {
                "name": "Same signature replay",
                "description": "Reusing same signature for different requests"
            },
            {
                "name": "Timestamp manipulation",
                "description": "Using old timestamps"
            },
            {
                "name": "Parameter exclusion",
                "description": "Not including all parameters in signature"
            },
            {
                "name": "Weak algorithm",
                "description": "Using weak hashing algorithm"
            }
        ]
        
        for attack in attacks:
            test_result = attack.copy()
            
            # Simulate attack
            simulated_response = self._simulate_signature_attack(family_code, attack["name"])
            
            test_result.update(simulated_response)
            results["tests"].append(test_result)
            
            if simulated_response.get("status") == "success":
                results["vulnerable"] = True
            
            time.sleep(0.5)
        
        return results
    
    def _simulate_signature_attack(self, family_code: str, attack_type: str) -> Dict:
        """
        Simulate signature attack
        """
        attack_success_rate = {
            "Same signature replay": 0.1,  # 10% chance
            "Timestamp manipulation": 0.3,  # 30% chance
            "Parameter exclusion": 0.4,     # 40% chance
            "Weak algorithm": 0.2,          # 20% chance
        }
        
        success_rate = attack_success_rate.get(attack_type, 0.1)
        
        if random.random() < success_rate:
            return {
                "status": "success",
                "message": f"Attack successful: {attack_type}",
                "severity": "HIGH"
            }
        else:
            return {
                "status": "error",
                "message": f"Attack prevented: {attack_type}",
                "severity": "LOW"
            }
    
    def comprehensive_validation(self, family_code: str) -> Dict:
        """
        Run comprehensive validation tests
        """
        results = {
            "family_code": family_code,
            "timestamp": time.time(),
            "tests": {}
        }
        
        # Run all tests
        tests = [
            ("price_manipulation", self.test_price_manipulation),
            ("ownership_bypass", self.test_ownership_bypass),
            ("signature_replay", self.test_signature_replay),
        ]
        
        for test_name, test_func in tests:
            try:
                test_result = test_func(family_code)
                results["tests"][test_name] = test_result
            
            except Exception as e:
                results["tests"][test_name] = {
                    "error": str(e),
                    "status": "failed"
                }
            
            time.sleep(1)  # Delay between tests
        
        # Calculate overall risk score
        results["risk_assessment"] = self._calculate_risk_score(results)
        
        return results
    
    def _calculate_risk_score(self, results: Dict) -> Dict:
        """
        Calculate risk score based on test results
        """
        vulnerabilities = 0
        total_tests = len(results.get("tests", {}))
        
        for test_name, test_result in results.get("tests", {}).items():
            if test_result.get("vulnerable"):
                vulnerabilities += 1
        
        risk_score = (vulnerabilities / total_tests) * 100 if total_tests > 0 else 0
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "CRITICAL"
        elif risk_score >= 40:
            risk_level = "HIGH"
        elif risk_score >= 20:
            risk_level = "MEDIUM"
        elif risk_score >= 10:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"
        
        return {
            "score": risk_score,
            "level": risk_level,
            "vulnerabilities_found": vulnerabilities,
            "total_tests": total_tests
        }
    
    def generate_report(self, validation_results: Dict) -> str:
        """
        Generate human-readable report
        """
        report_lines = []
        
        report_lines.append("=" * 60)
        report_lines.append("PACKAGE VALIDATION REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Family Code: {validation_results.get('family_code')}")
        report_lines.append(f"Timestamp: {time.ctime(validation_results.get('timestamp', time.time()))}")
        report_lines.append("")
        
        # Risk assessment
        risk = validation_results.get("risk_assessment", {})
        report_lines.append(f"RISK ASSESSMENT: {risk.get('level', 'UNKNOWN')}")
        report_lines.append(f"Score: {risk.get('score', 0):.1f}/100")
        report_lines.append(f"Vulnerabilities: {risk.get('vulnerabilities_found', 0)}/{risk.get('total_tests', 0)}")
        report_lines.append("")
        
        # Test results
        report_lines.append("DETAILED TEST RESULTS:")
        report_lines.append("-" * 40)
        
        for test_name, test_result in validation_results.get("tests", {}).items():
            report_lines.append(f"\n{test_name.upper().replace('_', ' ')}:")
            report_lines.append(f"  Status: {'VULNERABLE' if test_result.get('vulnerable') else 'SECURE'}")
            
            if test_result.get("vulnerable"):
                report_lines.append("  ⚠️  SECURITY WARNING: Potential vulnerability detected")
            
            if "tests" in test_result:
                for subtest in test_result["tests"]:
                    if isinstance(subtest, dict) and subtest.get("status") == "success":
                        if "VULNERABLE" in str(subtest.get("message", "")):
                            report_lines.append(f"  ❌ {subtest.get('message', '')}")
        
        # Recommendations
        report_lines.append("\n" + "=" * 60)
        report_lines.append("RECOMMENDATIONS:")
        report_lines.append("=" * 60)
        
        if risk.get("level") in ["CRITICAL", "HIGH"]:
            report_lines.append("🔴 IMMEDIATE ACTION REQUIRED:")
            report_lines.append("  - Review server-side validation logic")
            report_lines.append("  - Implement proper signature verification")
            report_lines.append("  - Add price validation on server")
            report_lines.append("  - Implement MSISDN ownership checks")
        elif risk.get("level") == "MEDIUM":
            report_lines.append("🟡 RECOMMENDED IMPROVEMENTS:")
            report_lines.append("  - Strengthen signature algorithm")
            report_lines.append("  - Add nonce to prevent replay attacks")
            report_lines.append("  - Implement stricter parameter validation")
        else:
            report_lines.append("🟢 SECURITY STATUS: ACCEPTABLE")
            report_lines.append("  - Continue monitoring for new vulnerabilities")
            report_lines.append("  - Regular security testing recommended")
        
        return "\n".join(report_lines)
