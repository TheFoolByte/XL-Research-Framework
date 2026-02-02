"""
Decoy system integration for price manipulation testing
Based on community data: https://me.mashu.lol/pg-decoy-*.json

Migrated from xl-research/src/modules/decoy.py
Adapted for integration with main framework.
"""
import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

# Use framework logger if available, fallback to basic
try:
    from core.logger import log as logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class DecoyManager:
    """Manages decoy endpoints for price manipulation testing"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.decoy_base_url = "https://me.mashu.lol/pg-decoy-"
        
        # Decoy types from community data
        self.decoy_types = [
            "default-balance",
            "default-qris", 
            "default-qris0",
            "prio-balance",
            "prio-qris",
            "prio-qris0"
        ]
        
        # Cache for decoy data
        self.decoy_cache = {}
        self.cache_expiry = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Decoy patterns from your data
        self.prio_patterns = ["PRIORITAS", "PRIOHYBRID", "60"]
        
    def fetch_decoy(self, decoy_type: str, force_refresh: bool = False) -> Optional[Dict]:
        """
        Fetch decoy data from endpoint
        """
        # Check cache first
        current_time = time.time()
        if (not force_refresh and 
            decoy_type in self.decoy_cache and
            decoy_type in self.cache_expiry and
            current_time < self.cache_expiry[decoy_type]):
            return self.decoy_cache[decoy_type]
        
        url = f"{self.decoy_base_url}{decoy_type}.json"
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                decoy_data = response.json()
                
                # Cache the data
                self.decoy_cache[decoy_type] = decoy_data
                self.cache_expiry[decoy_type] = current_time + self.cache_ttl
                
                return decoy_data
            else:
                return None
                
        except Exception as e:
            if hasattr(logger, 'error'):
                logger.error(f"Error fetching decoy {decoy_type}: {str(e)}")
            return None
    
    def get_option_code(self, package_type: str = "default", 
                       payment_method: str = "balance") -> Optional[str]:
        """
        Get option_code for decoy based on package and payment type
        """
        decoy_type = f"{package_type}-{payment_method}"
        
        decoy_data = self.fetch_decoy(decoy_type)
        if decoy_data:
            return decoy_data.get("option_code")
        
        return None
    
    def analyze_package_for_decoy(self, package_name: str) -> Tuple[str, str]:
        """
        Analyze package name to determine decoy type
        Returns: (package_type, payment_method)
        """
        package_lower = package_name.lower()
        
        # Determine package type
        package_type = "default"
        for pattern in self.prio_patterns:
            if pattern.lower() in package_lower:
                package_type = "prio"
                break
        
        # Default payment method (can be overridden)
        payment_method = "balance"
        
        return package_type, payment_method
    
    def simulate_purchase_with_decoy(self, family_code: str, 
                                    original_price: int,
                                    package_name: str = "") -> Dict:
        """
        Simulate purchase with decoy integration
        """
        result = {
            "family_code": family_code,
            "original_price": original_price,
            "decoy_applied": False,
            "simulated_price": original_price,
            "option_code": None,
            "tests": []
        }
        
        # Determine decoy type
        if package_name:
            package_type, payment_method = self.analyze_package_for_decoy(package_name)
        else:
            package_type, payment_method = "default", "balance"
        
        # Get option code
        option_code = self.get_option_code(package_type, payment_method)
        
        if option_code:
            result["option_code"] = option_code
            result["decoy_applied"] = True
            
            # Test different price reductions
            test_prices = [
                original_price,          # No reduction
                int(original_price * 0.5),  # 50% off
                int(original_price * 0.1),  # 90% off
                1000,                    # Fixed low price
                0                        # Free
            ]
            
            for test_price in test_prices:
                test_result = {
                    "test_price": test_price,
                    "decoy_type": f"{package_type}-{payment_method}",
                    "option_code": option_code,
                    "expected_success": test_price <= original_price
                }
                result["tests"].append(test_result)
        
        return result
    
    def find_working_decoy(self, family_code: str, 
                          original_price: int,
                          max_attempts: int = 10) -> Optional[Dict]:
        """
        Try to find a working decoy for a package
        """
        working_decoys = []
        
        for decoy_type in self.decoy_types:
            decoy_data = self.fetch_decoy(decoy_type)
            if not decoy_data:
                continue
            
            option_code = decoy_data.get("option_code")
            if not option_code:
                continue
            
            # Simulate success based on pattern
            if "prio" in decoy_type and "PRIO" in family_code.upper():
                success_rate = 0.7
            elif "default" in decoy_type:
                success_rate = 0.5
            else:
                success_rate = 0.3
            
            if success_rate > 0.5:  # Consider it potentially working
                working_decoys.append({
                    "decoy_type": decoy_type,
                    "option_code": option_code,
                    "confidence": success_rate,
                    "last_updated": decoy_data.get("last_fetched_at", 0)
                })
            
            time.sleep(0.5)  # Be nice
        
        if working_decoys:
            # Return the one with highest confidence
            working_decoys.sort(key=lambda x: x["confidence"], reverse=True)
            return working_decoys[0]
        
        return None
    
    def validate_decoy_system(self) -> Dict:
        """
        Validate all decoy endpoints
        """
        results = {
            "total_endpoints": len(self.decoy_types),
            "working": 0,
            "failing": 0,
            "details": {}
        }
        
        for decoy_type in self.decoy_types:
            url = f"{self.decoy_base_url}{decoy_type}.json"
            
            try:
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    results["details"][decoy_type] = {
                        "status": "WORKING",
                        "has_option_code": "option_code" in data,
                        "response_time": response.elapsed.total_seconds()
                    }
                    results["working"] += 1
                else:
                    results["details"][decoy_type] = {
                        "status": "FAILING",
                        "status_code": response.status_code
                    }
                    results["failing"] += 1
                    
            except Exception as e:
                results["details"][decoy_type] = {
                    "status": "ERROR",
                    "error": str(e)
                }
                results["failing"] += 1
        
        return results
