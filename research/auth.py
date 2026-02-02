"""
Authentication module for XL API

Migrated from xl-research/src/core/auth.py
Adapted for integration with main framework.
"""
import base64
import time
from typing import Dict, Optional
import requests

# Use framework logger if available, fallback to basic
try:
    from core.logger import log as logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    
    # Add compatibility methods
    if not hasattr(logger, 'info'):
        pass  # logging already has these


class AuthManager:
    """Manages OAuth2 authentication for API requests"""
    
    def __init__(self, config: Dict, session: requests.Session):
        self.config = config
        self.session = session
        self.access_token = None
        self.token_expiry = 0
        self.token_refresh_margin = 300  # 5 minutes
        
    def get_basic_auth(self) -> str:
        """Get Basic Auth header from config"""
        basic_auth = self.config.get('basic_auth', '')
        if not basic_auth:
            # Fallback: try to construct from client_id:client_secret
            client_id = self.config.get('client_id', '')
            client_secret = self.config.get('client_secret', '')
            if client_id and client_secret:
                basic_auth = base64.b64encode(
                    f"{client_id}:{client_secret}".encode()
                ).decode()
        return basic_auth
    
    def get_token(self, force_refresh: bool = False) -> Optional[str]:
        """
        Get OAuth2 access token
        """
        # Check if token is still valid
        if not force_refresh and self.is_token_valid():
            return self.access_token
        
        # Use base_url if available (for mock server), otherwise fall back to base_ciam_url
        base_url = self.config.get('base_url') or self.config.get('base_ciam_url', 'https://gede.ciam.xlaxiata.co.id')
        basic_auth = self.get_basic_auth()
        
        if not basic_auth:
            # For mock server, create a dummy basic auth
            basic_auth = 'bW9jazptb2Nr'  # base64('mock:mock')
        
        headers = {
            'Authorization': f'Basic {basic_auth}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': self.config.get('user_agent', 'ResearchClient/1.0')
        }
        
        data = {
            'grant_type': 'client_credentials'
        }
        
        try:
            response = self.session.post(
                f'{base_url}/oauth/token',
                headers=headers,
                data=data,
                timeout=self.config.get('timeout', 30)
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)
                self.token_expiry = time.time() + expires_in - self.token_refresh_margin
                
                if hasattr(logger, 'info'):
                    logger.info("Token acquired successfully")
                
                return self.access_token
            else:
                if hasattr(logger, 'error'):
                    logger.error(f"Token request failed: {response.status_code}")
                return None
                
        except Exception as e:
            if hasattr(logger, 'error'):
                logger.error(f"Token request error: {str(e)}")
            return None
    
    def is_token_valid(self) -> bool:
        """Check if token is still valid"""
        if not self.access_token:
            return False
        return time.time() < self.token_expiry
    
    def clear_token(self):
        """Clear current token"""
        self.access_token = None
        self.token_expiry = 0
