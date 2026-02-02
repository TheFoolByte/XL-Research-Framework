"""
General utility functions

Migrated from xl-research/src/utils/helpers.py
Adapted for integration with main framework.
"""
import re
import json
import time
import random
import string
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs, urlencode


def generate_random_phone() -> str:
    """Generate random Indonesian phone number"""
    prefixes = ['0812', '0813', '0814', '0815', '0816', '0817', '0818', '0819',
                '0852', '0853', '0855', '0856', '0857', '0858',
                '0877', '0878', '0879',
                '0881', '0882', '0883', '0884', '0885', '0886', '0887', '0888', '0889',
                '0895', '0896', '0897', '0898', '0899']
    
    prefix = random.choice(prefixes)
    number = ''.join(random.choices(string.digits, k=8))
    return f"{prefix}{number}"


def parse_family_code_from_text(text: str) -> List[str]:
    """Extract family codes (UUIDs) from text"""
    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    return re.findall(uuid_pattern, text, re.IGNORECASE)


def extract_package_info(text: str) -> Dict[str, Any]:
    """Extract package information from text"""
    info = {
        'name': None,
        'price': None,
        'quota': None,
        'validity': None,
        'category': None
    }
    
    # Try to find price
    price_patterns = [
        r'Rp\s*([\d.,]+)',
        r'Rp\.\s*([\d.,]+)',
        r'harga\s*:?\s*Rp\s*([\d.,]+)',
        r'price\s*:?\s*([\d.,]+)'
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            price_str = match.group(1).replace('.', '').replace(',', '')
            try:
                info['price'] = int(price_str)
                break
            except ValueError:
                continue
    
    # Try to find quota
    quota_patterns = [
        r'(\d+)\s*GB',
        r'quota\s*:?\s*(\d+)',
        r'kuota\s*:?\s*(\d+)'
    ]
    
    for pattern in quota_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                info['quota'] = int(match.group(1))
                break
            except ValueError:
                continue
    
    # Try to find validity
    validity_patterns = [
        r'(\d+)\s*hari',
        r'(\d+)\s*day',
        r'(\d+)\s*minggu',
        r'(\d+)\s*week',
        r'(\d+)\s*bulan',
        r'(\d+)\s*month'
    ]
    
    for pattern in validity_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                info['validity'] = int(match.group(1))
                break
            except ValueError:
                continue
    
    # Try to extract name (first line or before price)
    lines = text.strip().split('\n')
    if lines:
        first_line = lines[0].strip()
        if first_line and len(first_line) < 100:  # Reasonable length for name
            info['name'] = first_line
    
    return info


def format_price(price: int) -> str:
    """Format price as Indonesian currency"""
    if price is None:
        return "N/A"
    
    price_str = str(price)
    result = ""
    count = 0
    
    for char in reversed(price_str):
        if count == 3:
            result = '.' + result
            count = 0
        result = char + result
        count += 1
    
    return f"Rp {result}"


def calculate_success_rate(successes: int, attempts: int) -> float:
    """Calculate success rate with edge case handling"""
    if attempts == 0:
        return 0.0
    return successes / attempts


def create_progress_bar(progress: float, width: int = 40) -> str:
    """Create ASCII progress bar"""
    filled = int(width * progress)
    empty = width - filled
    
    bar = "[" + "=" * filled + " " * empty + "]"
    percentage = f"{progress * 100:.1f}%"
    
    return f"{bar} {percentage}"


def retry_with_backoff(func, max_retries: int = 3, 
                      base_delay: float = 1.0, 
                      max_delay: float = 30.0):
    """Retry function with exponential backoff"""
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries:
                raise
            
            # Calculate delay with exponential backoff and jitter
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)  # 10% jitter
            total_delay = delay + jitter
            
            time.sleep(total_delay)


def validate_uuid(uuid_str: str) -> bool:
    """Validate UUID format"""
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, uuid_str, re.IGNORECASE))


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_json_loads(text: str, default: Any = None) -> Any:
    """Safely parse JSON with fallback"""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


def parse_url_params(url: str) -> Dict[str, List[str]]:
    """Parse URL query parameters"""
    try:
        parsed = urlparse(url)
        return parse_qs(parsed.query)
    except Exception:
        return {}


def build_url(base: str, params: Dict[str, Any]) -> str:
    """Build URL with query parameters"""
    query_string = urlencode(params, doseq=True)
    separator = '?' if query_string else ''
    return f"{base}{separator}{query_string}"


def generate_session_id() -> str:
    """Generate random session ID"""
    timestamp = int(time.time())
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    return f"{timestamp}_{random_part}"


def mask_sensitive_data(text: str) -> str:
    """Mask sensitive data in text"""
    # Mask phone numbers
    text = re.sub(r'08\d{8,10}', '08*******', text)
    
    # Mask tokens (keep first and last 4 chars)
    text = re.sub(r'(token|key|secret)[=:]\s*([a-zA-Z0-9]{8,})', 
                  lambda m: f"{m.group(1)}={m.group(2)[:4]}...{m.group(2)[-4:]}", 
                  text, flags=re.IGNORECASE)
    
    # Mask UUIDs (keep first and last 4 chars)
    text = re.sub(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
                  lambda m: f"{m.group(1)[:8]}...{m.group(1)[-4:]}",
                  text, flags=re.IGNORECASE)
    
    return text


def format_duration(seconds: float) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()


def normalize_text(text: str) -> str:
    """Normalize text by removing extra whitespace and normalizing case"""
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Convert to lowercase for consistency
    return text.lower()


def find_common_prefix(strings: List[str]) -> str:
    """Find common prefix among strings"""
    if not strings:
        return ""
    
    # Sort to ensure shortest string first
    strings.sort()
    shortest = strings[0]
    
    for i, char in enumerate(shortest):
        for string in strings[1:]:
            if i >= len(string) or string[i] != char:
                return shortest[:i]
    
    return shortest
