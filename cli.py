"""
XL Research Framework v2.1 - CLI Interface

Modern CLI with profile-based execution.

Usage:
    python cli.py analyze <apk> --profile <light|xl|full>
    python cli.py list modules
    python cli.py profile <name>
    python cli.py research enumerate --max-attempts 100
    python cli.py research analyze <family_code>
    python cli.py research validate <family_code>
"""

import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from core import __version__, log, config
from core.engine import Engine
from core.lazy_loader import loader
from profiles import ProfileLoader


def print_banner():
    """Print framework banner"""
    print(f"""
╔════════════════════════════════════════════════════════════╗
║         XL RESEARCH FRAMEWORK v{__version__}                   ║
║         APK Security Research & Auditing                   ║
╚════════════════════════════════════════════════════════════╝
""")


def cmd_analyze(args):
    """Run analysis with Engine"""
    apk_path = args.apk
    profile = args.profile or "xl"
    
    if not os.path.exists(apk_path):
        log.error(f"APK not found: {apk_path}")
        return 1
    
    # Handle research flag override
    research_override = None
    if hasattr(args, 'research') and args.research:
        research_override = True
        log.info("Research analysis: ENABLED (--research flag)")
    elif hasattr(args, 'no_research') and args.no_research:
        research_override = False
        log.info("Research analysis: DISABLED (--no-research flag)")
    
    # Run analysis via Engine
    engine = Engine(profile)
    
    # Apply research override if specified
    if research_override is not None:
        engine.set_research_override(research_override)
    
    results = engine.analyze(apk_path)
    
    if "error" in results:
        log.error(results["error"])
        return 1
    
    # Generate advanced report
    from reporters import generate_report
    
    config.ensure_dirs()
    
    if args.output:
        output_dir = Path(args.output).parent
    else:
        output_dir = config.reports_dir
    
    report_paths = generate_report(results, output_dir=str(output_dir))
    
    log.success("Reports generated:")
    log.info(f"  TXT:  {report_paths['txt']}")
    log.info(f"  JSON: {report_paths['json']}")
    
    return 0


def _write_text_report(results: dict, path: str):
    """Write text report"""
    with open(path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("      XL RESEARCH FRAMEWORK - ANALYSIS REPORT\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"APK: {results.get('apk', 'N/A')}\n")
        f.write(f"Profile: {results.get('profile', 'N/A')}\n")
        f.write(f"Duration: {results.get('duration_seconds', 0):.1f}s\n")
        f.write(f"Total Findings: {results.get('total_findings', 0)}\n")
        f.write("\n" + "-" * 60 + "\n")
        
        for name, data in results.get("results", {}).items():
            f.write(f"\n[{name.upper()}] - {data.get('count', 0)} findings\n")
            
            for finding in data.get("findings", [])[:15]:
                sev = finding.get("severity", "info")[:4].upper()
                msg = finding.get("message", "")[:55]
                f.write(f"  [{sev}] {msg}\n")
            
            if data.get("count", 0) > 15:
                f.write(f"  ... and {data['count'] - 15} more\n")
        
        f.write("\n" + "=" * 60 + "\n")


def cmd_list_modules(args):
    """List available modules"""
    print_banner()
    
    log.header("Available Modules")
    
    modules = loader.list_available()
    
    for name in modules:
        mod = loader.load(name)
        if mod:
            print(f"  • {name:12} - {mod.description}")
    
    return 0


def cmd_show_profile(args):
    """Show profile details"""
    print_banner()
    
    try:
        profile = ProfileLoader.load(args.name)
    except ValueError as e:
        log.error(str(e))
        return 1
    
    log.header(f"Profile: {profile.name}")
    
    print(f"Description: {profile.description}")
    print(f"Memory Limit: {profile.memory_limit_mb} MB")
    print(f"Max Files: {profile.max_files or 'unlimited'}")
    print(f"File Types: {', '.join(profile.file_types)}")
    print(f"Modules: {', '.join(profile.modules)}")
    print(f"Decompile: {profile.decompile_level}")
    print(f"Timeout: {profile.timeout_seconds}s")
    
    return 0


def cmd_list_profiles(args):
    """List all profiles"""
    print_banner()
    
    log.header("Available Profiles")
    
    profiles = ProfileLoader.list_all()
    
    for name, desc in profiles.items():
        print(f"  • {name:8} - {desc}")
    
    return 0


def cmd_doctor(args):
    """
    Run system health diagnostics.
    
    Checks:
    - Project structure
    - Import integrity
    - Dependency availability
    - Module health
    """
    verbose = args.verbose if hasattr(args, 'verbose') else False
    fix_mode = args.fix if hasattr(args, 'fix') else False
    
    log.header("System Health Diagnostics")
    
    issues = []
    passed = 0
    
    # 1. Structure Check
    log.section("1. Structure Check")
    try:
        from scripts.health_check import check_files, check_dirs, get_project_root, REQUIRED_FILES, REQUIRED_DIRS
        root = get_project_root()
        
        dirs_found, dirs_missing = check_dirs(root)
        files_found, files_missing = check_files(root)
        
        log.info(f"Directories: {len(dirs_found)}/{len(REQUIRED_DIRS)}")
        log.info(f"Files: {len(files_found)}/{len(REQUIRED_FILES)}")
        
        if dirs_missing:
            for d in dirs_missing:
                issues.append(f"Missing directory: {d}")
                log.error(f"  ✗ {d}")
        else:
            passed += 1
            log.success("  ✓ All directories present")
        
        if files_missing:
            for f in files_missing:
                issues.append(f"Missing file: {f}")
                if verbose:
                    log.error(f"  ✗ {f}")
        else:
            passed += 1
            log.success("  ✓ All files present")
            
    except ImportError:
        log.warning("Health check module not available")
        issues.append("scripts/health_check.py not found")
    
    # 2. Import Check
    log.section("2. Import Check")
    import_tests = [
        ("core.engine", "Engine"),
        ("core.config", "config"),
        ("core.exceptions", "XLResearchError"),
        ("core.intelligence", "ResearchAdapter"),
        ("core.helpers", "validate_uuid"),
        ("modules.base", "BaseModule"),
        ("profiles", "ProfileLoader"),
        ("research", "ResearchAdapter"),
    ]
    
    import_pass = 0
    import_fail = 0
    
    for module, item in import_tests:
        try:
            m = __import__(module, fromlist=[item])
            getattr(m, item)
            import_pass += 1
            if verbose:
                log.info(f"  ✓ {module}.{item}")
        except Exception as e:
            import_fail += 1
            issues.append(f"Import failed: {module}.{item}")
            log.error(f"  ✗ {module}.{item}: {e}")
    
    if import_fail == 0:
        passed += 1
        log.success(f"  ✓ All {import_pass} imports passed")
    else:
        log.warning(f"  {import_pass} passed, {import_fail} failed")
    
    # 3. Dependency Check
    log.section("3. Dependency Check")
    deps = ["yaml", "psutil", "requests"]
    dep_pass = 0
    
    for dep in deps:
        try:
            __import__(dep)
            dep_pass += 1
            if verbose:
                log.info(f"  ✓ {dep}")
        except ImportError:
            issues.append(f"Missing dependency: {dep}")
            log.error(f"  ✗ {dep} not installed")
    
    if dep_pass == len(deps):
        passed += 1
        log.success(f"  ✓ All {dep_pass} dependencies available")
    
    # 4. Module Health
    log.section("4. Module Health")
    try:
        from core.lazy_loader import loader
        available = loader.list_available()
        log.info(f"Available modules: {len(available)}")
        
        if available:
            passed += 1
            log.success(f"  ✓ {len(available)} modules registered")
            if verbose:
                for mod in available:
                    log.info(f"    • {mod}")
    except Exception as e:
        issues.append(f"Module loader error: {e}")
        log.error(f"  ✗ Loader error: {e}")
    
    # 5. Profile Check
    log.section("5. Profile Check")
    profiles = ["light", "xl", "full"]
    profile_pass = 0
    
    for profile in profiles:
        try:
            p = ProfileLoader.load(profile)
            profile_pass += 1
            if verbose:
                log.info(f"  ✓ {profile}: {p.description}")
        except Exception as e:
            issues.append(f"Profile load failed: {profile}")
            log.error(f"  ✗ {profile}: {e}")
    
    if profile_pass == len(profiles):
        passed += 1
        log.success(f"  ✓ All {profile_pass} profiles load correctly")
    
    # Summary
    print()
    log.header("Summary")
    
    total_checks = 5
    
    if len(issues) == 0:
        log.success(f"✓ All {passed}/{total_checks} checks passed")
        log.success("System health: GOOD")
        return 0
    else:
        log.warning(f"Checks: {passed}/{total_checks} passed")
        log.error(f"Issues found: {len(issues)}")
        
        if verbose:
            print()
            log.header("Issues")
            for issue in issues:
                log.error(f"  • {issue}")
        
        if fix_mode:
            log.info("\nAttempting repairs...")
            log.info("Run: python scripts/repair.py")
        
        return 1


def cmd_research(args):
    """Research subcommands handler"""
    try:
        from research import create_adapter, ResearchConfig
        from research.adapter import load_research_config
    except ImportError as e:
        log.error(f"Research module not available: {e}")
        return 1
    
    # Load research configuration
    config_path = Path(__file__).parent / "research_config.yaml"
    research_config = load_research_config(str(config_path))
    
    if not research_config:
        log.error("Failed to load research configuration")
        return 1
    
    # Create adapter
    adapter = create_adapter({
        'enabled': True,
        'config_path': str(config_path)
    })
    
    if not adapter:
        log.error("Failed to create research adapter")
        return 1
    
    if not adapter.initialize():
        log.error("Failed to initialize research adapter")
        return 1
    
    try:
        if args.research_command == "enumerate":
            return cmd_research_enumerate(args, adapter)
        elif args.research_command == "analyze":
            return cmd_research_analyze(args, adapter)
        elif args.research_command == "validate":
            return cmd_research_validate(args, adapter)
        elif args.research_command == "decoy":
            return cmd_research_decoy(args, adapter)
        else:
            log.error(f"Unknown research command: {args.research_command}")
            return 1
    finally:
        adapter.cleanup()


def cmd_research_enumerate(args, adapter):
    """Enumerate family codes"""
    log.header("Family Code Enumeration")
    
    max_attempts = args.max_attempts or 100
    categories = args.categories.split(',') if args.categories else None
    
    log.info(f"Max attempts: {max_attempts}")
    log.info(f"Target categories: {categories or 'All'}")
    
    result = adapter.enumerate_codes(
        max_attempts=max_attempts,
        target_categories=categories
    )
    
    if result:
        log.success(f"Found {result.get('found', 0)} codes")
        log.info(f"Success rate: {result.get('success_rate', 0):.2%}")
        
        # Show found codes
        found = result.get('found_codes', [])
        for code_info in found[:10]:
            code = code_info.get('family_code', 'Unknown')
            log.info(f"  • {code}")
        
        if len(found) > 10:
            log.info(f"  ... and {len(found) - 10} more")
        
        # Export results
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            log.success(f"Results saved to: {output_path}")
    else:
        log.warning("No codes found")
    
    return 0


def cmd_research_analyze(args, adapter):
    """Analyze family codes"""
    log.header("Family Code Analysis")
    
    codes = args.codes
    if not codes:
        log.error("No family codes provided")
        return 1
    
    code_list = codes.split(',') if ',' in codes else [codes]
    
    log.info(f"Analyzing {len(code_list)} codes")
    
    result = adapter.analyze_family_codes(code_list)
    
    if result:
        log.success(f"Valid: {result.get('valid', 0)}/{result.get('total', 0)}")
        
        # Show analyses
        for analysis in result.get('analyses', [])[:5]:
            code = analysis.get('family_code', 'Unknown')[:20]
            patterns = analysis.get('patterns', [])
            category = patterns[0].get('category', 'Unknown') if patterns else 'Unknown'
            log.info(f"  • {code}... → {category}")
        
        # Export results
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            log.success(f"Results saved to: {output_path}")
    else:
        log.warning("Analysis failed")
    
    return 0


def cmd_research_validate(args, adapter):
    """Validate package security"""
    log.header("Package Validation")
    
    family_code = args.family_code
    if not family_code:
        log.error("Family code required")
        return 1
    
    log.info(f"Validating: {family_code}")
    
    result = adapter.validate_package(family_code)
    
    if result:
        risk = result.get('risk_assessment', {})
        log.info(f"Risk Level: {risk.get('level', 'Unknown')}")
        log.info(f"Risk Score: {risk.get('score', 0):.1f}/100")
        log.info(f"Vulnerabilities: {risk.get('vulnerabilities_found', 0)}/{risk.get('total_tests', 0)}")
        
        # Show vulnerable tests
        for test_name, test_result in result.get('tests', {}).items():
            if test_result.get('vulnerable'):
                log.warning(f"  ⚠️ {test_name}: VULNERABLE")
            else:
                log.info(f"  ✓ {test_name}: Secure")
        
        # Export results
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            log.success(f"Results saved to: {output_path}")
    else:
        log.warning("Validation failed")
    
    return 0


def cmd_research_decoy(args, adapter):
    """Check decoy endpoints"""
    log.header("Decoy System Check")
    
    result = adapter.get_decoy(args.decoy_type or "default-balance")
    
    if result:
        log.success(f"Decoy type: {args.decoy_type or 'default-balance'}")
        log.info(f"Option code: {result.get('option_code', 'N/A')}")
        
        # Export results
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            log.success(f"Results saved to: {output_path}")
    else:
        log.warning("Failed to fetch decoy")
    
    return 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        prog="xlrf",
        description="XL Research Framework - APK Security Research"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # analyze
    analyze_p = subparsers.add_parser("analyze", help="Analyze APK")
    analyze_p.add_argument("apk", help="Path to APK file")
    analyze_p.add_argument("-p", "--profile", choices=["light", "xl", "full"], 
                          default="xl", help="Execution profile")
    analyze_p.add_argument("-o", "--output", help="Output file path")
    analyze_p.add_argument("-f", "--format", choices=["text", "json"], 
                          default="text", help="Output format")
    analyze_p.add_argument("--research", action="store_true",
                          help="Force enable research analysis (overrides profile)")
    analyze_p.add_argument("--no-research", action="store_true",
                          help="Force disable research analysis (overrides profile)")
    
    # doctor
    doctor_p = subparsers.add_parser("doctor", help="System health diagnostics")
    doctor_p.add_argument("--fix", action="store_true", help="Attempt to fix issues")
    doctor_p.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    # list
    list_p = subparsers.add_parser("list", help="List resources")
    list_p.add_argument("resource", choices=["modules", "profiles"])
    
    # profile
    profile_p = subparsers.add_parser("profile", help="Show profile details")
    profile_p.add_argument("name", help="Profile name")
    
    # research
    research_p = subparsers.add_parser("research", help="Research operations")
    research_sub = research_p.add_subparsers(dest="research_command", help="Research commands")
    
    # research enumerate
    enum_p = research_sub.add_parser("enumerate", help="Enumerate family codes")
    enum_p.add_argument("-n", "--max-attempts", type=int, default=100, help="Max enumeration attempts")
    enum_p.add_argument("-c", "--categories", help="Target categories (comma-separated)")
    enum_p.add_argument("-o", "--output", help="Output file path")
    
    # research analyze
    analyze_r = research_sub.add_parser("analyze", help="Analyze family codes")
    analyze_r.add_argument("codes", help="Family code(s) to analyze (comma-separated)")
    analyze_r.add_argument("-o", "--output", help="Output file path")
    
    # research validate
    validate_p = research_sub.add_parser("validate", help="Validate package security")
    validate_p.add_argument("family_code", help="Family code to validate")
    validate_p.add_argument("-o", "--output", help="Output file path")
    
    # research decoy
    decoy_p = research_sub.add_parser("decoy", help="Check decoy endpoints")
    decoy_p.add_argument("-t", "--decoy-type", default="default-balance", help="Decoy type")
    decoy_p.add_argument("-o", "--output", help="Output file path")
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.command == "analyze":
        return cmd_analyze(args)
    elif args.command == "list":
        if args.resource == "modules":
            return cmd_list_modules(args)
        else:
            return cmd_list_profiles(args)
    elif args.command == "profile":
        return cmd_show_profile(args)
    elif args.command == "research":
        return cmd_research(args)
    elif args.command == "doctor":
        return cmd_doctor(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
