"""
Signature generation for XL API requests

Migrated from xl-research/src/core/signature.py
Adapted for integration with main framework.
"""
import hmac
import hashlib
import json
import time
from typing import Dict

# Use framework logger if available, fallback to basic
try:
    from core.logger import log as logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class SignatureGenerator:
    """Generates HMAC-SHA256 signatures for API requests"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.sig_key = config.get('ax_api_sig_key', '')
        self.base_secret = config.get('x_api_base_secret', '')
        
    def generate(self, method: str, path: str, 
                timestamp: str, body: Dict) -> str:
        """
        Generate HMAC-SHA256 signature
        
        Format: HMAC(secret, METHOD + PATH + TIMESTAMP + JSON_BODY)
        """
        if not self.sig_key:
            secret = b''
        else:
            # Try hex decode first, then fallback to string
            try:
                secret = bytes.fromhex(self.sig_key)
            except ValueError:
                secret = self.sig_key.encode()
        
        # Prepare payload string
        body_str = json.dumps(body, separators=(',', ':')) if body else '{}'
        payload = f"{method.upper()}{path}{timestamp}{body_str}"
        
        # Generate signature
        signature = hmac.new(
            secret,
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify(self, signature: str, method: str, path: str,
              timestamp: str, body: Dict) -> bool:
        """Verify a signature"""
        expected = self.generate(method, path, timestamp, body)
        return hmac.compare_digest(signature, expected)
    
    def generate_variant(self, variant: str = 'default') -> str:
        """
        Generate signature using different algorithms (for testing)
        
        Variants:
        - default: METHOD + PATH + TIMESTAMP + BODY
        - simple: TIMESTAMP + BODY
        - path_only: METHOD + PATH
        """
        timestamp = str(int(time.time()))
        dummy_body = {"test": "data"}
        
        if variant == 'simple':
            payload = f"{timestamp}{json.dumps(dummy_body, separators=(',', ':'))}"
        elif variant == 'path_only':
            payload = "GET/api/v1/test"
        else:  # default
            payload = f"GET/api/v1/test{timestamp}{json.dumps(dummy_body, separators=(',', ':'))}"
        
        secret = bytes.fromhex(self.sig_key) if self.sig_key else b''
        return hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()
