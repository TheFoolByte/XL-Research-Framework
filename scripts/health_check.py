#!/usr/bin/env python
"""
XL Research Framework - Health Check Script

Validates project structure and required components.
Run: python scripts/health_check.py

Exit codes:
    0 = All checks passed
    1 = Critical failure (missing required components)
    2 = Warning (optional components missing)
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple

# Colors for output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def get_project_root() -> Path:
    """Get project root directory"""
    return Path(__file__).parent.parent


# Required structure definition
REQUIRED_FILES = [
    # Core
    "core/__init__.py",
    "core/engine.py",
    "core/config.py",
    "core/context.py",
    "core/logger.py",
    "core/lazy_loader.py",
    "core/memory_optimizer.py",
    "core/exceptions.py",
    
    # Modules
    "modules/__init__.py",
    "modules/base.py",
    "modules/api/__init__.py",
    "modules/api/analyzer.py",
    "modules/auth/__init__.py",
    "modules/auth/analyzer.py",
    "modules/config/__init__.py",
    "modules/config/analyzer.py",
    "modules/endpoint/__init__.py",
    "modules/endpoint/analyzer.py",
    "modules/family/__init__.py",
    "modules/family/analyzer.py",
    
    # Profiles
    "profiles/__init__.py",
    "profiles/base.py",
    "profiles/light.py",
    "profiles/xl.py",
    "profiles/full.py",
    
    # Research
    "research/__init__.py",
    "research/adapter.py",
    "research/auth.py",
    "research/client.py",
    "research/signature.py",
    "research/modules/__init__.py",
    "research/modules/analyzer.py",
    "research/utils/__init__.py",
    
    # Extractors
    "extractors/__init__.py",
    "extractors/partial_jadx.py",
    "extractors/manifest_parser.py",
    
    # Reporters
    "reporters/__init__.py",
    "reporters/report_generator.py",
    
    # Root
    "cli.py",
    "requirements.txt",
    "config.yaml",
]

REQUIRED_DIRS = [
    "core",
    "modules",
    "modules/api",
    "modules/auth",
    "modules/config",
    "modules/endpoint",
    "modules/family",
    "profiles",
    "research",
    "research/modules",
    "research/utils",
    "extractors",
    "reporters",
]

OPTIONAL_FILES = [
    "tests/__init__.py",
    "tests/conftest.py",
    "tests/test_engine.py",
    "tests/test_modules.py",
    "tests/test_research.py",
    "tests/test_cli.py",
    "tests/test_memory.py",
    "tests/test_imports.py",
    "research_config.yaml",
    "STRUCTURE.lock",
]


def check_files(root: Path) -> Tuple[List[str], List[str]]:
    """Check required files exist"""
    missing = []
    found = []
    
    for file_path in REQUIRED_FILES:
        full_path = root / file_path
        if full_path.exists():
            found.append(file_path)
        else:
            missing.append(file_path)
    
    return found, missing


def check_dirs(root: Path) -> Tuple[List[str], List[str]]:
    """Check required directories exist"""
    missing = []
    found = []
    
    for dir_path in REQUIRED_DIRS:
        full_path = root / dir_path
        if full_path.is_dir():
            found.append(dir_path)
        else:
            missing.append(dir_path)
    
    return found, missing


def check_optional(root: Path) -> Tuple[List[str], List[str]]:
    """Check optional files"""
    missing = []
    found = []
    
    for file_path in OPTIONAL_FILES:
        full_path = root / file_path
        if full_path.exists():
            found.append(file_path)
        else:
            missing.append(file_path)
    
    return found, missing


def check_imports() -> Tuple[int, int, List[str]]:
    """Test critical imports"""
    passed = 0
    failed = 0
    errors = []
    
    import_tests = [
        ("core.config", "config"),
        ("core.logger", "log"),
        ("core.engine", "Engine"),
        ("core.exceptions", "XLResearchError"),
        ("modules.base", "BaseModule"),
        ("profiles", "ProfileLoader"),
        ("research", "ResearchAdapter"),
    ]
    
    for module, item in import_tests:
        try:
            m = __import__(module, fromlist=[item])
            getattr(m, item)
            passed += 1
        except Exception as e:
            failed += 1
            errors.append(f"{module}.{item}: {e}")
    
    return passed, failed, errors


def print_results(title: str, items: List[str], color: str, symbol: str):
    """Print formatted results"""
    if items:
        print(f"\n{color}{title} ({len(items)}){RESET}")
        for item in items[:10]:  # Limit display
            print(f"  {symbol} {item}")
        if len(items) > 10:
            print(f"  ... and {len(items) - 10} more")


def main():
    """Run health check"""
    print("=" * 60)
    print("  XL Research Framework - Health Check")
    print("=" * 60)
    
    root = get_project_root()
    print(f"\nProject root: {root}")
    
    # Check directories
    dirs_found, dirs_missing = check_dirs(root)
    
    # Check required files
    files_found, files_missing = check_files(root)
    
    # Check optional files
    opt_found, opt_missing = check_optional(root)
    
    # Summary
    print(f"\n{'-' * 60}")
    print("  Structure Check")
    print(f"{'-' * 60}")
    
    print(f"\nDirectories: {GREEN}{len(dirs_found)}/{len(REQUIRED_DIRS)} found{RESET}")
    print(f"Required files: {GREEN}{len(files_found)}/{len(REQUIRED_FILES)} found{RESET}")
    print(f"Optional files: {YELLOW}{len(opt_found)}/{len(OPTIONAL_FILES)} found{RESET}")
    
    # Print missing
    print_results("Missing directories (CRITICAL)", dirs_missing, RED, "✗")
    print_results("Missing required files (CRITICAL)", files_missing, RED, "✗")
    print_results("Missing optional files (WARNING)", opt_missing, YELLOW, "⚠")
    
    # Check imports
    print(f"\n{'-' * 60}")
    print("  Import Check")
    print(f"{'-' * 60}")
    
    # Add project root to path for imports
    sys.path.insert(0, str(root))
    
    passed, failed, errors = check_imports()
    
    if failed == 0:
        print(f"\n{GREEN}✓ All {passed} critical imports passed{RESET}")
    else:
        print(f"\n{RED}✗ Import failures: {failed}/{passed + failed}{RESET}")
        for err in errors:
            print(f"  ✗ {err}")
    
    # Final status
    print(f"\n{'=' * 60}")
    
    if dirs_missing or files_missing:
        print(f"{RED}  HEALTH CHECK: FAILED (missing required components){RESET}")
        print("=" * 60)
        return 1
    elif failed > 0:
        print(f"{RED}  HEALTH CHECK: FAILED (import errors){RESET}")
        print("=" * 60)
        return 1
    elif opt_missing:
        print(f"{YELLOW}  HEALTH CHECK: PASSED with warnings{RESET}")
        print("=" * 60)
        return 2
    else:
        print(f"{GREEN}  HEALTH CHECK: PASSED{RESET}")
        print("=" * 60)
        return 0


if __name__ == "__main__":
    sys.exit(main())
