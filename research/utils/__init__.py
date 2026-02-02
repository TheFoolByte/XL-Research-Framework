"""
XL Research - Utilities Package

Provides data export and helper functions for research operations.
"""

from .exporter import ResultExporter
from .helpers import (
    generate_random_phone,
    parse_family_code_from_text,
    extract_package_info,
    format_price,
    calculate_success_rate,
    create_progress_bar,
    retry_with_backoff,
    validate_uuid,
    chunk_list,
    safe_json_loads,
    parse_url_params,
    build_url,
    generate_session_id,
    mask_sensitive_data,
    format_duration,
    get_timestamp,
    normalize_text,
    find_common_prefix
)

__all__ = [
    "exporter", 
    "helpers",
    "ResultExporter",
    "generate_random_phone",
    "parse_family_code_from_text",
    "extract_package_info",
    "format_price",
    "calculate_success_rate",
    "create_progress_bar",
    "retry_with_backoff",
    "validate_uuid",
    "chunk_list",
    "safe_json_loads",
    "parse_url_params",
    "build_url",
    "generate_session_id",
    "mask_sensitive_data",
    "format_duration",
    "get_timestamp",
    "normalize_text",
    "find_common_prefix"
]
