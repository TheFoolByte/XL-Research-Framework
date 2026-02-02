#!/usr/bin/env python
"""
XL Research Framework - Guard Script

Prevents accidental deletion and verifies core folder integrity.

Usage:
    python scripts/guard.py           # Check integrity
    python scripts/guard.py --watch   # Watch mode (continuous)
"""

import sys
import os
import hashlib
import json
from pathlib import Path
from datetime import datetime

# Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def get_project_root() -> Path:
    """Get project root directory"""
    return Path(__file__).parent.parent


# Protected directories that MUST exist
PROTECTED_DIRS = [
    "core",
    "modules",
    "profiles",
    "extractors",
    "reporters",
    "research",
    "tests",
    "scripts",
]

# Protected files that MUST NOT be deleted
PROTECTED_FILES = [
    "cli.py",
    "config.yaml",
    "requirements.txt",
    "core/__init__.py",
    "core/engine.py",
    "core/config.py",
    "modules/__init__.py",
    "modules/base.py",
]


def compute_folder_hash(folder: Path) -> str:
    """Compute simple hash of folder structure"""
    hasher = hashlib.sha256()
    
    for item in sorted(folder.rglob("*")):
        if item.is_file() and "__pycache__" not in str(item):
            rel_path = item.relative_to(folder)
            hasher.update(str(rel_path).encode())
    
    return hasher.hexdigest()[:16]


def check_protected_dirs(root: Path) -> tuple:
    """Check if all protected directories exist"""
    missing = []
    found = []
    
    for dir_name in PROTECTED_DIRS:
        dir_path = root / dir_name
        if dir_path.is_dir():
            found.append(dir_name)
        else:
            missing.append(dir_name)
    
    return found, missing


def check_protected_files(root: Path) -> tuple:
    """Check if all protected files exist"""
    missing = []
    found = []
    
    for file_path in PROTECTED_FILES:
        full_path = root / file_path
        if full_path.exists():
            found.append(file_path)
        else:
            missing.append(file_path)
    
    return found, missing


def generate_integrity_report(root: Path) -> dict:
    """Generate integrity report"""
    dirs_found, dirs_missing = check_protected_dirs(root)
    files_found, files_missing = check_protected_files(root)
    
    # Compute hashes for each protected directory
    dir_hashes = {}
    for dir_name in dirs_found:
        dir_path = root / dir_name
        dir_hashes[dir_name] = compute_folder_hash(dir_path)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "root": str(root),
        "directories": {
            "found": dirs_found,
            "missing": dirs_missing,
            "total_protected": len(PROTECTED_DIRS),
        },
        "files": {
            "found": files_found,
            "missing": files_missing,
            "total_protected": len(PROTECTED_FILES),
        },
        "hashes": dir_hashes,
        "status": "PASS" if (not dirs_missing and not files_missing) else "FAIL",
    }
    
    return report


def main():
    """Main entry point"""
    root = get_project_root()
    
    print("=" * 60)
    print("  XL Research Framework - Guard")
    print("=" * 60)
    print(f"\nProject root: {root}")
    
    # Generate report
    report = generate_integrity_report(root)
    
    # Display results
    print(f"\n{'-' * 60}")
    print("  Protected Directories")
    print(f"{'-' * 60}")
    
    dirs_found = report["directories"]["found"]
    dirs_missing = report["directories"]["missing"]
    
    print(f"Found: {len(dirs_found)}/{report['directories']['total_protected']}")
    
    if dirs_missing:
        print(f"\n{RED}MISSING DIRECTORIES:{RESET}")
        for d in dirs_missing:
            print(f"  ✗ {d}")
    else:
        print(f"{GREEN}  ✓ All protected directories present{RESET}")
    
    print(f"\n{'-' * 60}")
    print("  Protected Files")
    print(f"{'-' * 60}")
    
    files_missing = report["files"]["missing"]
    
    if files_missing:
        print(f"\n{RED}MISSING FILES:{RESET}")
        for f in files_missing:
            print(f"  ✗ {f}")
    else:
        print(f"{GREEN}  ✓ All protected files present{RESET}")
    
    # Save report
    output_dir = root / "output" / "system"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = output_dir / "guard_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved: {report_path}")
    
    # Final status
    print(f"\n{'=' * 60}")
    if report["status"] == "PASS":
        print(f"{GREEN}  GUARD STATUS: PASS{RESET}")
    else:
        print(f"{RED}  GUARD STATUS: FAIL{RESET}")
        print(f"  Run: python scripts/repair.py")
    print("=" * 60)
    
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
