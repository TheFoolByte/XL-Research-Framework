"""
XL Research Framework - Core Helpers

Utility functions and helpers used across the framework.
Migrated from research/utils/ for unified architecture.
"""

# Re-export from research utils for backward compatibility
try:
    from research.utils.helpers import (
        generate_random_phone,
        validate_uuid,
        format_price,
        mask_string,
        random_delay,
    )
    from research.utils.exporter import ResultExporter
except ImportError:
    # Fallback stubs
    def generate_random_phone():
        return "0812345678901"
    
    def validate_uuid(uuid_str):
        import re
        pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(pattern, uuid_str, re.IGNORECASE))
    
    def format_price(amount):
        return f"Rp {amount:,}"
    
    def mask_string(s, visible=4):
        if len(s) <= visible:
            return s
        return s[:visible] + '*' * (len(s) - visible)
    
    def random_delay(min_s=0.5, max_s=2.0):
        import time, random
        time.sleep(random.uniform(min_s, max_s))
    
    ResultExporter = None

__all__ = [
    'generate_random_phone',
    'validate_uuid',
    'format_price',
    'mask_string',
    'random_delay',
    'ResultExporter',
]
