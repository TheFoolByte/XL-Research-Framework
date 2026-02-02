#!/usr/bin/env python
"""
XL Research Framework - Repair Script

Restores missing files and rebuilds project structure.

Usage:
    python scripts/repair.py           # Check and prompt
    python scripts/repair.py --auto    # Auto-repair without prompts
"""

import sys
import os
import shutil
from pathlib import Path
from datetime import datetime

# Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


def get_project_root() -> Path:
    """Get project root directory"""
    return Path(__file__).parent.parent


# Required directory structure
REQUIRED_STRUCTURE = {
    "core": [
        "__init__.py",
    ],
    "core/intelligence": [
        "__init__.py",
    ],
    "core/helpers": [
        "__init__.py",
    ],
    "modules": [
        "__init__.py",
    ],
    "modules/api": [
        "__init__.py",
    ],
    "modules/auth": [
        "__init__.py",
    ],
    "modules/config": [
        "__init__.py",
    ],
    "modules/endpoint": [
        "__init__.py",
    ],
    "modules/family": [
        "__init__.py",
    ],
    "profiles": [
        "__init__.py",
    ],
    "extractors": [
        "__init__.py",
    ],
    "reporters": [
        "__init__.py",
    ],
    "research": [
        "__init__.py",
    ],
    "research/modules": [
        "__init__.py",
    ],
    "research/utils": [
        "__init__.py",
    ],
    "tests": [
        "__init__.py",
    ],
    "scripts": [
        "__init__.py",
    ],
}

# Template for empty __init__.py
INIT_TEMPLATE = '''"""
{package_name} Package
"""
'''


def create_directory(root: Path, dir_path: str) -> bool:
    """Create a directory if it doesn't exist"""
    full_path = root / dir_path
    if not full_path.exists():
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"{GREEN}  ✓ Created: {dir_path}/{RESET}")
        return True
    return False


def create_init_file(root: Path, file_path: str) -> bool:
    """Create an __init__.py file if it doesn't exist"""
    full_path = root / file_path
    if not full_path.exists():
        package_name = full_path.parent.name.title()
        content = INIT_TEMPLATE.format(package_name=package_name)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"{GREEN}  ✓ Created: {file_path}{RESET}")
        return True
    return False


def check_and_repair_structure(root: Path, auto: bool = False) -> dict:
    """Check structure and repair missing parts"""
    created_dirs = []
    created_files = []
    
    for dir_path, files in REQUIRED_STRUCTURE.items():
        # Check directory
        full_dir = root / dir_path
        if not full_dir.exists():
            if auto:
                create_directory(root, dir_path)
                created_dirs.append(dir_path)
            else:
                print(f"{YELLOW}  ? Missing: {dir_path}/{RESET}")
        
        # Check files in directory
        for file_name in files:
            file_path = f"{dir_path}/{file_name}"
            full_file = root / file_path
            
            if not full_file.exists():
                if auto:
                    # Ensure parent exists
                    full_file.parent.mkdir(parents=True, exist_ok=True)
                    create_init_file(root, file_path)
                    created_files.append(file_path)
                else:
                    print(f"{YELLOW}  ? Missing: {file_path}{RESET}")
    
    return {
        "created_dirs": created_dirs,
        "created_files": created_files,
    }


def install_dependencies() -> bool:
    """Install missing dependencies"""
    print(f"\n{CYAN}Installing dependencies...{RESET}")
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print(f"{GREEN}  ✓ Dependencies installed{RESET}")
            return True
        else:
            print(f"{RED}  ✗ Dependency install failed{RESET}")
            return False
    except Exception as e:
        print(f"{RED}  ✗ Error: {e}{RESET}")
        return False


def create_backup(root: Path) -> str:
    """Create backup of current state"""
    backup_dir = root / "output" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}"
    
    # Just record the state, don't copy everything
    state_file = backup_dir / f"{backup_name}.json"
    
    import json
    state = {
        "timestamp": timestamp,
        "dirs": [str(p) for p in root.iterdir() if p.is_dir()],
        "files": [str(p) for p in root.glob("*.py")],
    }
    
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
    
    print(f"{GREEN}  ✓ Backup created: {state_file.name}{RESET}")
    return str(state_file)


def main():
    """Main entry point"""
    root = get_project_root()
    auto_mode = "--auto" in sys.argv
    
    print("=" * 60)
    print("  XL Research Framework - Repair")
    print("=" * 60)
    print(f"\nProject root: {root}")
    print(f"Mode: {'AUTO' if auto_mode else 'INTERACTIVE'}")
    
    # Create backup first
    print(f"\n{'-' * 60}")
    print("  Creating Backup")
    print(f"{'-' * 60}")
    backup_path = create_backup(root)
    
    # Check and repair structure
    print(f"\n{'-' * 60}")
    print("  Checking Structure")
    print(f"{'-' * 60}")
    
    result = check_and_repair_structure(root, auto=auto_mode)
    
    if not auto_mode:
        # Show what would be created
        response = input(f"\n{CYAN}Proceed with repairs? [y/N]: {RESET}").strip().lower()
        if response == 'y':
            result = check_and_repair_structure(root, auto=True)
    
    # Summary
    print(f"\n{'-' * 60}")
    print("  Summary")
    print(f"{'-' * 60}")
    
    print(f"Directories created: {len(result['created_dirs'])}")
    print(f"Files created: {len(result['created_files'])}")
    
    if result['created_dirs'] or result['created_files']:
        print(f"\n{GREEN}Repair complete!{RESET}")
        print(f"Run: python scripts/guard.py")
    else:
        print(f"\n{GREEN}No repairs needed.{RESET}")
    
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
