"""
Enhanced API client with all endpoints from community data

Migrated from xl-research/src/core/client.py
Adapted for integration with main framework.
"""
import requests
import json
import time
from typing import Dict, Optional, Any, List
from urllib.parse import urljoin

from .auth import AuthManager
from .signature import SignatureGenerator

# Use framework logger if available, fallback to basic
try:
    from core.logger import log as logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class XLResearchClient:
    """API client for XL research endpoints"""
    
    def __init__(self, base_url: str, config: Dict[str, Any]):
        self.base_url = base_url
        self.config = config
        self.session = requests.Session()
        self.auth = AuthManager(config, self.session)
        self.signer = SignatureGenerator(config)
        
        self.access_token = None
        self.last_request_time = 0
        self.request_delay = config.get('request_delay', 1.5)
        self.max_retries = config.get('max_retries', 3)
        self.timeout = config.get('timeout', 30)
        
        # User agent
        self.user_agent = config.get('user_agent', 
            'myXL / 8.9.0(1202); com.android.vending; (samsung; SM-N935F; SDK 33; Android 13)')
    
    def _ensure_token(self) -> bool:
        """Ensure valid access token exists"""
        if not self.auth.is_token_valid():
            self.access_token = self.auth.get_token()
            if not self.access_token:
                return False
        else:
            self.access_token = self.auth.access_token
        return True
    
    def _rate_limit(self):
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request_with_retry(self, method: str, endpoint: str,
                                **kwargs) -> Optional[requests.Response]:
        """Make request with retry logic"""
        for attempt in range(self.max_retries):
            try:
                self._rate_limit()
                
                if not self._ensure_token():
                    return None
                
                url = urljoin(self.base_url, endpoint)
                timestamp = str(int(time.time()))
                
                # Prepare body for signature
                body = kwargs.get('json', {}) or kwargs.get('data', {})
                if isinstance(body, dict):
                    body_str = json.dumps(body, separators=(',', ':'))
                else:
                    body_str = str(body)
                
                # Generate signature
                signature = self.signer.generate(
                    method=method,
                    path=endpoint,
                    timestamp=timestamp,
                    body=body if isinstance(body, dict) else {}
                )
                
                # Prepare headers
                headers = kwargs.get('headers', {})
                headers.update({
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json',
                    'X-TIMESTAMP': timestamp,
                    'X-SIGNATURE': signature,
                    'User-Agent': self.user_agent,
                    'X-DEVICE-FP': self.config.get('ax_fp_key', ''),
                    'X-API-KEY': self.config.get('api_key', '')
                })
                
                kwargs['headers'] = headers
                kwargs['timeout'] = self.timeout
                
                response = self.session.request(method, url, **kwargs)
                
                return response
                
            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except requests.exceptions.ConnectionError:
                return None
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return None
                time.sleep(1)
        
        return None
    
    # --- PACKAGE ENDPOINTS ---
    
    def get_package_detail(self, family_code: str) -> Optional[Dict]:
        """Get package details by family code"""
        endpoint = f"/api/v1/package/{family_code}/detail"
        response = self._make_request_with_retry('GET', endpoint)
        
        if response and response.status_code == 200:
            return response.json()
        return None
    
    def get_package_list(self, category: str = None, 
                        limit: int = 50) -> Optional[Dict]:
        """Get list of packages (if endpoint exists)"""
        endpoint = "/api/v1/package/list"
        params = {'category': category, 'limit': limit} if category else {'limit': limit}
        
        response = self._make_request_with_retry('GET', endpoint, params=params)
        
        if response and response.status_code == 200:
            return response.json()
        return None
    
    def get_package_categories(self) -> Optional[List[str]]:
        """Get available package categories"""
        endpoint = "/api/v1/package/categories"
        response = self._make_request_with_retry('GET', endpoint)
        
        if response and response.status_code == 200:
            data = response.json()
            return data.get('categories', [])
        return None
    
    # --- PURCHASE ENDPOINTS ---
    
    def simulate_purchase(self, family_code: str, 
                         msisdn: str = None,
                         price_override: int = None,
                         payment_method: str = "balance") -> Optional[Dict]:
        """
        Simulate package purchase (for testing)
        
        Args:
            family_code: Package family code
            msisdn: Phone number (optional)
            price_override: Override price (for testing)
            payment_method: Payment method (balance, qris, qris0)
        """
        endpoint = "/api/v1/purchase"
        
        body = {
            "family_code": family_code,
            "quantity": 1,
            "payment_method": payment_method
        }
        
        if msisdn:
            body["msisdn"] = msisdn
        
        if price_override:
            body["price"] = price_override
        
        response = self._make_request_with_retry('POST', endpoint, json=body)
        
        if response:
            return {
                'status_code': response.status_code,
                'body': response.json() if response.content else None,
                'headers': dict(response.headers)
            }
        return None
    
    # --- USER ENDPOINTS ---
    
    def get_profile(self) -> Optional[Dict]:
        """Get user profile"""
        endpoint = "/api/v1/profile"
        response = self._make_request_with_retry('GET', endpoint)
        
        if response and response.status_code == 200:
            return response.json()
        return None
    
    def get_balance(self) -> Optional[Dict]:
        """Get user balance"""
        endpoint = "/api/v1/balance"
        response = self._make_request_with_retry('GET', endpoint)
        
        if response and response.status_code == 200:
            return response.json()
        return None
    
    def get_purchase_history(self, limit: int = 10) -> Optional[Dict]:
        """Get purchase history"""
        endpoint = "/api/v1/purchase/history"
        params = {'limit': limit}
        response = self._make_request_with_retry('GET', endpoint, params=params)
        
        if response and response.status_code == 200:
            return response.json()
        return None
    
    # --- DISCOVERY ENDPOINTS ---
    
    def discover_endpoints(self, common_paths: List[str] = None) -> Dict:
        """
        Discover available endpoints
        
        Returns:
            Dict of endpoint -> status_code
        """
        if common_paths is None:
            common_paths = [
                "/api/v1/package/list",
                "/api/v1/package/categories",
                "/api/v1/package/recommended",
                "/api/v1/package/promo",
                "/api/v1/profile",
                "/api/v1/balance",
                "/api/v1/purchase/history",
                "/api/v1/user/packages",
                "/api/v1/config/packages",
                "/auth/token",
                "/auth/userinfo"
            ]
        
        results = {}
        
        for path in common_paths:
            response = self._make_request_with_retry('GET', path)
            if response:
                results[path] = {
                    'status': response.status_code,
                    'size': len(response.content),
                    'has_json': 'application/json' in response.headers.get('Content-Type', '')
                }
            else:
                results[path] = {'status': 'ERROR', 'error': 'No response'}
            
            time.sleep(0.5)  # Be nice
        
        return results
