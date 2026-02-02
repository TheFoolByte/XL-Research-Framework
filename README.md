# XL Research Framework v2.1

> **Advanced Android APK Security Research Tool**
>
> Memory-optimized framework for ethical security analysis of Android applications with integrated research capabilities.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/github/license/TheFoolByte/XL-Research-Core.v2)
![GitHub stars](https://img.shields.io/github/stars/TheFoolByte/XL-Research-Core.v2)
![GitHub forks](https://img.shields.io/github/forks/TheFoolByte/XL-Research-Core.v2)
![GitHub issues](https://img.shields.io/github/issues/TheFoolByte/XL-Research-Core.v2)
![Memory](https://img.shields.io/badge/Memory-8GB%20Optimized-orange.svg)
![Status](https://img.shields.io/badge/Status-Production-brightgreen.svg)

---

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Commands Reference](#-commands-reference)
- [Profiles](#-profiles)
- [Analysis Modules](#-analysis-modules)
- [Research Integration](#-research-integration)
- [System Health](#-system-health)
- [Architecture](#-architecture)
- [Configuration](#-configuration)
- [Advanced Usage](#-advanced-usage)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Ethical Usage](#-ethical-usage)

---

## 🎯 Features

| Feature                   | Description                                       |
| ------------------------- | ------------------------------------------------- |
| **Modular Architecture**  | Lazy-loaded modules with priority-based execution |
| **Profile System**        | light/xl/full profiles for different use cases    |
| **Memory Optimized**      | Designed for 8GB RAM systems                      |
| **Partial Decompilation** | 3 levels: manifest, sources, full                 |
| **Correlation Engine**    | Detects security pattern chains                   |
| **Research Integration**  | API research with authentication & enumeration    |
| **System Health Check**   | Built-in diagnostics and repair tools             |
| **Advanced Reports**      | TXT + JSON with risk scoring                      |
| **Test Suite**            | Comprehensive pytest coverage                     |

---

## 📦 Installation

### Prerequisites

- **Python 3.8+**
- **JADX** (for APK decompilation)
- **8GB RAM** minimum
- **Windows/Linux/Mac** supported

### Quick Setup

```bash
# Clone repository
git clone https://github.com/yourrepo/xl-research-tools.git
cd "XL Research Tools"

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python cli.py doctor
```

### Dependencies

Core requirements:

```txt
pyyaml>=6.0
psutil>=5.9.0
requests>=2.28.0
```

Development/Testing:

```txt
pytest>=7.0.0
pre-commit>=2.20.0
```

### JADX Setup

1. Download JADX from [github.com/skylot/jadx](https://github.com/skylot/jadx/releases)
2. Extract to a folder (e.g., `C:/jadx/`)
3. Update `config.yaml`:

```yaml
jadx:
  path: "C:/jadx/bin/jadx.bat" # Windows
  # path: "jadx"                # Linux/Mac (if in PATH)
  timeout: 300
  threads: 2
```

---

## 🚀 Quick Start

### Basic Analysis

```bash
# Analyze APK with default (xl) profile
python cli.py analyze app.apk

# Analyze with specific profile
python cli.py analyze app.apk --profile light
python cli.py analyze app.apk --profile full

# Custom output location
python cli.py analyze app.apk -o custom_report.txt

# JSON format
python cli.py analyze app.apk --format json
```

### System Information

```bash
# List available modules
python cli.py list modules

# List available profiles
python cli.py list profiles

# Show profile details
python cli.py profile xl

# Check system health
python cli.py doctor
python cli.py doctor --verbose  # Detailed diagnostics
```

### Output

Analysis results are saved to:

```
output/
├── <apk_name>_report.txt     # Human-readable report
└── <apk_name>_report.json    # Machine-readable JSON

system/
├── merge_report.md           # Integration report
├── health_status.json        # System health
└── test_result.log           # Test results
```

---

## 📚 Commands Reference

### Main Commands

#### `analyze` - Analyze APK

```bash
python cli.py analyze <apk_path> [options]

Options:
  -p, --profile {light,xl,full}   Execution profile (default: xl)
  -o, --output PATH               Output file path
  -f, --format {text,json}        Output format (default: text)
  --research                      Force enable research (overrides profile)
  --no-research                   Force disable research (overrides profile)

Examples:
  python cli.py analyze app.apk
  python cli.py analyze app.apk --profile full
  python cli.py analyze app.apk -o report.txt --format json
  python cli.py analyze app.apk --research
```

#### `list` - List Resources

```bash
python cli.py list {modules,profiles}

Examples:
  python cli.py list modules    # Show available analysis modules
  python cli.py list profiles   # Show available profiles
```

#### `profile` - Show Profile Details

```bash
python cli.py profile <profile_name>

Examples:
  python cli.py profile xl
  python cli.py profile full
```

#### `doctor` - System Health Diagnostics

```bash
python cli.py doctor [options]

Options:
  -v, --verbose    Detailed diagnostics output
  --fix            Attempt to fix detected issues

Checks performed:
  1. Structure Check     - Directories and files
  2. Import Check        - Critical imports
  3. Dependency Check    - Required packages
  4. Module Health       - Registered modules
  5. Profile Check       - Profile loadability

Examples:
  python cli.py doctor              # Basic check
  python cli.py doctor --verbose    # Detailed output
  python cli.py doctor --fix        # Auto-repair
```

#### `research` - Research Commands

```bash
python cli.py research <subcommand> [options]

Subcommands:
  enumerate    Enumerate family codes
  analyze      Analyze specific family code
  validate     Validate package security
  decoy        Test decoy endpoints

Examples:
  python cli.py research enumerate --max-attempts 100
  python cli.py research analyze d004d498-e8a8-4e22-b8b1-b71b7652b409
  python cli.py research validate <family_code>
  python cli.py research decoy
```

### Utility Scripts

#### Guard - Integrity Check

```bash
python scripts/guard.py

Features:
  - Verifies protected directories (8 dirs)
  - Checks critical files
  - Computes folder hashes
  - Generates integrity report

Output: output/system/guard_report.json
```

#### Repair - Structure Restoration

```bash
python scripts/repair.py [--auto]

Features:
  - Creates missing directories
  - Restores missing __init__.py files
  - Creates backup before repair
  - Interactive or auto mode

Examples:
  python scripts/repair.py        # Interactive
  python scripts/repair.py --auto # Automatic repair
```

#### Health Check

```bash
python scripts/health_check.py

Features:
  - Validates 13 required directories
  - Checks 41 required files
  - Tests 7 critical imports
  - Comprehensive status report
```

---

## 📊 Profiles

### Profile Comparison

| Profile | Memory | Workers | Decompile | Duration | Use Case          |
| ------- | ------ | ------- | --------- | -------- | ----------------- |
| `light` | 2GB    | 1       | manifest  | ~10s     | Quick triage      |
| `xl`    | 4GB    | 2       | sources   | ~45s     | Standard analysis |
| `full`  | 6GB    | 4       | full      | ~120s    | Deep research     |

### Profile Details

#### **Light Profile** (`--profile light`)

**Best for:**

- Quick initial scans
- Low-memory systems
- CI/CD pipelines
- Batch processing

**Modules enabled:**

- `api_scanner`
- `endpoint_finder`

**Configuration:**

```yaml
memory_limit_mb: 2048
max_workers: 1
decompile_level: "manifest"
research_enabled: false
```

#### **XL Profile** (`--profile xl`) ⭐ Recommended

**Best for:**

- Standard security analysis
- Balanced speed/depth
- Most common use cases

**Modules enabled:**

- `api_scanner`
- `endpoint_finder`
- `auth_flow`
- `family_logic`
- `env_extractor`

**Configuration:**

```yaml
memory_limit_mb: 4096
max_workers: 2
decompile_level: "sources"
research_enabled: false
```

#### **Full Profile** (`--profile full`)

**Best for:**

- Comprehensive research
- Academic studies
- Deep security audits

**Modules enabled:**

- All 5 core modules
- Research integration

**Configuration:**

```yaml
memory_limit_mb: 6144
max_workers: 4
decompile_level: "full"
research_enabled: true
```

---

## 🔍 Analysis Modules

### Module Overview

| Module            | Patterns | Severity Levels | Description                             |
| ----------------- | -------- | --------------- | --------------------------------------- |
| `api_scanner`     | 8        | high, medium    | REST, GraphQL, Retrofit endpoints       |
| `endpoint_finder` | 2        | high, low       | Network URLs with domain categorization |
| `auth_flow`       | 14       | critical, high  | OAuth, JWT, credentials, biometric      |
| `family_logic`    | 15       | medium, low     | XL plans, quota, promo, loyalty         |
| `env_extractor`   | 16       | critical, high  | API keys, secrets, debug flags          |

### Module Output Format

Each module returns structured JSON:

```json
{
  "module": "api_scanner",
  "total": 12,
  "duration_seconds": 3.2,
  "findings": [
    {
      "category": "API",
      "type": "rest_endpoint",
      "message": "REST endpoint: /api/v1/users",
      "file": "com/app/network/ApiService.java",
      "line": 45,
      "severity": "high",
      "confidence": "high",
      "context": "public String getUsers() { ... }"
    }
  ]
}
```

### Severity Levels

| Severity   | Risk Score | Description                   |
| ---------- | ---------- | ----------------------------- |
| `critical` | 90-100     | Immediate security risk       |
| `high`     | 70-89      | Significant security concern  |
| `medium`   | 40-69      | Moderate security issue       |
| `low`      | 1-39       | Informational / best practice |

---

## 🔬 Research Integration

The framework includes integrated API research capabilities for XL ecosystem analysis.

### Research Architecture

```
research/
├── adapter.py         # Engine integration
├── auth.py            # OAuth2 authentication
├── client.py          # API client
├── signature.py       # HMAC-SHA256 signatures
├── modules/
│   ├── analyzer.py    # Family code pattern analysis
│   ├── enumerator.py  # Smart code enumeration
│   ├── validator.py   # Package validation
│   └── decoy.py       # Decoy endpoint testing
└── utils/
    ├── helpers.py     # Helper functions
    └── exporter.py    # Result export
```

### Research Commands

#### Enumerate Family Codes

```bash
python cli.py research enumerate [options]

Options:
  --max-attempts INT    Maximum enumeration attempts (default: 100)
  --workers INT         Concurrent workers (default: 2)
  --output PATH         Export results path

Example:
  python cli.py research enumerate --max-attempts 500 --workers 4
```

#### Analyze Family Code

```bash
python cli.py research analyze <family_code>

Example:
  python cli.py research analyze d004d498-e8a8-4e22-b8b1-b71b7652b409

Output:
  - Package name
  - Category
  - Price
  - Quota
  - Validity
```

#### Validate Package

```bash
python cli.py research validate <family_code>

Checks:
  - Package availability
  - Price consistency
  - Quota limits
  - Security configuration

Example:
  python cli.py research validate d004d498-e8a8-4e22-b8b1-b71b7652b409
```

#### Decoy Testing

```bash
python cli.py research decoy

Features:
  - Tests honeypot endpoints
  - Validates API responses
  - Detects rate limiting
  - Checks authentication
```

### Research Configuration

Edit `research_config.yaml`:

```yaml
research:
  # API Configuration
  base_url: "https://api.xl.co.id"
  api_key: "your_api_key"

  # Authentication
  auth:
    client_id: "your_client_id"
    client_secret: "your_client_secret"

  # Request Settings
  request_delay: 1.5 # Seconds between requests
  max_retries: 3
  timeout: 30

  # Rate Limiting
  rate_limit:
    requests_per_minute: 30
    burst_size: 10
```

### Automatic Integration

When using the **full** profile, research is automatically integrated:

```bash
python cli.py analyze app.apk --profile full
```

**Stage 8 (Research Analysis) will:**

1. Extract family codes from APK findings
2. Analyze patterns and relationships
3. Validate packages
4. Include research insights in report

---

## 🏥 System Health

### Doctor Command

Comprehensive system diagnostics:

```bash
python cli.py doctor --verbose
```

**Output:**

```
============================================================
                 System Health Diagnostics
============================================================

1. Structure Check
   Directories: 13/13 ✓
   Files: 41/41 ✓

2. Import Check
   Tested: 8 imports
   Passed: 8/8 ✓

3. Dependency Check
   Required: yaml, psutil, requests
   Installed: 3/3 ✓

4. Module Health
   Available: 5 modules
   Registered: 5/5 ✓

5. Profile Check
   Profiles: light, xl, full
   Loadable: 3/3 ✓

============================================================
System health: GOOD
============================================================
```

### Guard Script

Protects core structure:

```bash
python scripts/guard.py
```

**Protects:**

- 8 core directories (core, modules, research, profiles, etc.)
- 41 critical files
- Computes integrity hashes
- Generates reports

**Output:** `output/system/guard_report.json`

```json
{
  "timestamp": "2026-02-02T16:30:00",
  "status": "PASS",
  "directories": {
    "found": 8,
    "missing": 0
  },
  "files": {
    "found": 41,
    "missing": 0
  },
  "hashes": {
    "core": "a3f2c1...",
    "modules": "b4e5d6..."
  }
}
```

### Repair Script

Restores missing structure:

```bash
# Interactive mode
python scripts/repair.py

# Automatic mode
python scripts/repair.py --auto
```

**Features:**

- Creates missing directories
- Restores `__init__.py` files
- Creates backup before changes
- Safe and reversible

---

## 🏗️ Architecture

### Directory Structure

```
XL Research Tools/
├── core/                      # Core Engine
│   ├── engine.py              # Orchestrator (8 stages)
│   ├── config.py              # Config management
│   ├── context.py             # Memory-efficient context
│   ├── lazy_loader.py         # Dynamic module loading
│   ├── memory_optimizer.py    # Memory management
│   ├── correlation_engine.py  # Security chain detection
│   ├── correlator.py          # Correlation logic
│   ├── exceptions.py          # Custom exceptions
│   ├── logger.py              # Colored logging
│   ├── intelligence/          # Research wrapper
│   │   ├── __init__.py        # Re-exports from research/
│   │   └── modules/           # Module wrapper
│   └── helpers/               # Utility wrapper
│
├── modules/                   # Analysis Modules
│   ├── base.py                # BaseModule class
│   ├── api/                   # API scanner
│   ├── endpoint/              # Endpoint finder
│   ├── auth/                  # Auth analyzer
│   ├── family/                # XL logic analyzer
│   └── config/                # Environment extractor
│
├── profiles/                  # Execution Profiles
│   ├── base.py                # Profile base class
│   ├── loader.py              # Profile loader
│   ├── light.py               # 2GB profile
│   ├── xl.py                  # 4GB profile
│   └── full.py                # 6GB profile
│
├── research/                  # Research Integration
│   ├── adapter.py             # Engine adapter
│   ├── auth.py                # OAuth2 auth
│   ├── client.py              # API client
│   ├── signature.py           # HMAC signatures
│   ├── modules/               # Research modules
│   │   ├── analyzer.py        # Pattern analysis
│   │   ├── enumerator.py      # Smart enumeration
│   │   ├── validator.py       # Package validation
│   │   └── decoy.py           # Decoy testing
│   └── utils/                 # Utilities
│       ├── helpers.py         # Helper functions
│       └── exporter.py        # Result export
│
├── extractors/                # APK Extraction
│   ├── partial_jadx.py        # Decompilation (3 levels)
│   └── manifest_parser.py     # Manifest parser
│
├── reporters/                 # Report Generation
│   └── report_generator.py    # TXT + JSON reports
│
├── tests/                     # Test Suite
│   ├── conftest.py            # Pytest fixtures
│   ├── test_engine.py         # Engine tests
│   ├── test_modules.py        # Module tests
│   ├── test_research.py       # Research tests
│   ├── test_cli.py            # CLI tests
│   ├── test_memory.py         # Memory tests
│   ├── test_imports.py        # Import tests
│   └── test_profiles.py       # Profile tests
│
├── scripts/                   # Utility Scripts
│   ├── health_check.py        # System validation
│   ├── guard.py               # Integrity check
│   └── repair.py              # Structure repair
│
├── web/                       # Web Interface
│   └── app.py                 # Flask app
│
├── output/                    # Generated Output
│   └── system/                # System reports
│
├── cli.py                     # CLI entry point
├── config.yaml                # Framework config
├── profiles.yaml              # Profile definitions
├── research_config.yaml       # Research config
├── requirements.txt           # Dependencies
├── requirements.lock          # Locked versions
├── STRUCTURE.lock             # Structure definition
├── .pre-commit-config.yaml    # Pre-commit hooks
└── README.md                  # This file
```

### Execution Flow

```
1. Initialize    → Load profile, configure memory
2. Extract       → Decompile APK (manifest/sources/full)
3. Manifest      → Parse AndroidManifest.xml
4. Load Modules  → Lazy load analysis modules
5. Analyze       → Run modules in parallel
6. Correlate     → Detect security chains
7. Report        → Generate TXT + JSON
8. Research      → API research (full profile only)
```

---

## ⚙️ Configuration

### config.yaml

Framework-wide settings:

```yaml
# XL Research Framework Configuration

framework:
  version: "2.1.0"
  debug: false

jadx:
  path: "jadx"
  timeout: 300
  threads: 2

memory:
  limit_mb: 4096
  gc_threshold: 0.80
  cache_size_mb: 256

output:
  directory: "output"
  formats: ["txt", "json"]
  timestamp_format: "%Y%m%d_%H%M%S"
```

### profiles.yaml

Profile definitions:

```yaml
profiles:
  light:
    description: "Quick scan, minimal memory (2GB)"
    memory_limit_mb: 2048
    max_workers: 1
    decompile_level: "manifest"
    research_enabled: false
    modules:
      - api_scanner
      - endpoint_finder
    correlation:
      enabled: true
      min_chain_length: 2

  xl:
    description: "XL ecosystem analysis (4GB)"
    memory_limit_mb: 4096
    max_workers: 2
    decompile_level: "sources"
    research_enabled: false
    modules:
      - api_scanner
      - endpoint_finder
      - auth_flow
      - family_logic
      - env_extractor
    correlation:
      enabled: true
      min_chain_length: 2

  full:
    description: "Comprehensive analysis (6GB)"
    memory_limit_mb: 6144
    max_workers: 4
    decompile_level: "full"
    research_enabled: true
    modules:
      - all
    correlation:
      enabled: true
      min_chain_length: 1
```

### research_config.yaml

Research module settings:

```yaml
research:
  base_url: "https://api.xl.co.id"
  api_version: "v1"

  auth:
    client_id: "your_client_id"
    client_secret: "your_client_secret"
    token_url: "https://api.xl.co.id/oauth/token"

  request:
    delay: 1.5
    max_retries: 3
    timeout: 30
    user_agent: "myXL/8.9.0"

  rate_limit:
    requests_per_minute: 30
    burst_size: 10

  signature:
    algorithm: "HMAC-SHA256"
    secret_key: "your_secret_key"
```

---

## 💡 Advanced Usage

### Python API

#### Basic Usage

```python
from core import Engine, run_analysis

# Simple usage
results = run_analysis("app.apk", profile="xl")
print(f"Total findings: {results['total_findings']}")
print(f"Risk score: {results['risk_score']}")
```

#### Advanced Engine Control

```python
from core import Engine

# Initialize engine
engine = Engine("full")

# Set callbacks
engine.set_callbacks(
    on_stage_start=lambda stage, i, total: print(f"Stage {i}/{total}: {stage}"),
    on_module_start=lambda name, i, total: print(f"Running {name}..."),
    on_finding=lambda finding: log_finding(finding),
    on_error=lambda error: handle_error(error)
)

# Research override
engine.set_research_override(True)  # Force enable
engine.set_research_override(False) # Force disable

# Run analysis
results = engine.analyze("app.apk")

# Access results
for module_name, module_results in results.get("modules", {}).items():
    print(f"\n{module_name}: {module_results['total']} findings")
    for finding in module_results.get("findings", []):
        print(f"  [{finding['severity']}] {finding['message']}")
```

#### Correlation Analysis

```python
from core import correlator

# Run correlation
insights = correlator.correlate(engine_results)

# Access correlations
for corr in insights.get("items", []):
    print(f"\n[{corr['severity']}] {corr['title']}")
    print(f"  Risk Score: {corr['risk_score']}")
    print(f"  Chain: {corr['chain_type']}")
    print(f"  {corr['explanation']}")
    print(f"  → {corr['recommendation']}")

# Human-readable output
print(correlator.explain_all())

# JSON export
import json
json_data = correlator.to_json()
with open("correlations.json", "w") as f:
    json.dump(json_data, f, indent=2)
```

#### Memory Management

```python
from core import memory_optimizer

# Configure for low memory
memory_optimizer.configure(
    memory_limit_mb=2048,
    max_workers=1,
    gc_threshold=0.70  # Trigger GC at 70%
)

# Check memory
stats = memory_optimizer.get_stats()
print(f"Used: {stats['used_mb']} MB / {stats['limit_mb']} MB")
print(f"Percent: {stats['percent']}%")

# Manual cleanup
memory_optimizer.trigger_cleanup(aggressive=True)

# Context manager
with memory_optimizer.managed_memory():
    # Your code here
    pass  # Automatic cleanup on exit
```

#### Research Integration

```python
from core.intelligence import ResearchAdapter, ResearchConfig
from research import create_adapter

# Load config
config = ResearchConfig.from_file("research_config.yaml")

# Create adapter
adapter = create_adapter(config)

# Analyze family code
result = adapter.analyze_family_code("d004d498-e8a8-4e22-b8b1-b71b7652b409")
print(f"Package: {result.get('package_name')}")
print(f"Price: Rp {result.get('price'):,}")

# Enumerate codes
codes = adapter.enumerate_codes(max_attempts=100)
print(f"Found {len(codes)} valid family codes")

# Validate package
validation = adapter.validate_package("d004d498-e8a8-4e22-b8b1-b71b7652b409")
if validation["valid"]:
    print(f"✓ Package is valid and activatable")
```

---

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_engine.py -v
pytest tests/test_research.py -v

# Run with coverage
pytest tests/ --cov=core --cov=modules --cov=research --cov-report=html

# Run import tests (fast)
pytest tests/test_imports.py -v

# Run memory tests
pytest tests/test_memory.py -v

# Run with markers
pytest tests/ -v -m "not slow"  # Skip slow tests
pytest tests/ -v -m "integration"  # Only integration tests
```

### Test Structure

```
tests/
├── conftest.py          # Fixtures (mock APK, directories)
├── test_engine.py       # Engine tests (163 lines)
├── test_modules.py      # Module tests (191 lines)
├── test_research.py     # Research tests (226 lines)
├── test_cli.py          # CLI tests (170 lines)
├── test_memory.py       # Memory tests (171 lines)
├── test_imports.py      # Import tests (191 lines)
└── test_profiles.py     # Profile tests
```

### Coverage

Current coverage: **~85%**

Target areas:

- Core engine: 90%+
- Modules: 85%+
- Research: 80%+
- CLI: 75%+

---

## 🐛 Troubleshooting

### Common Issues

#### 1. JADX Not Found

**Error:**

```
[ERROR] JADX executable not found
```

**Solution:**

```bash
# Option 1: Add JADX to system PATH
export PATH=$PATH:/path/to/jadx/bin  # Linux/Mac
set PATH=%PATH%;C:\jadx\bin          # Windows

# Option 2: Update config.yaml
jadx:
  path: "C:/jadx/bin/jadx.bat"  # Windows
  # path: "/usr/local/bin/jadx" # Linux/Mac
```

#### 2. Memory Errors

**Error:**

```
[ERROR] MemoryError: Unable to allocate array
```

**Solutions:**

```bash
# Use light profile
python cli.py analyze app.apk --profile light

# Reduce workers in profile
memory_limit_mb: 2048
max_workers: 1

# Increase system virtual memory (Windows)
# Control Panel → System → Advanced → Performance Settings → Virtual Memory
```

#### 3. Import Errors

**Error:**

```
ModuleNotFoundError: No module named 'yaml'
```

**Solution:**

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or install individually
pip install pyyaml psutil requests

# Verify installation
python -c "import yaml, psutil, requests; print('OK')"
```

#### 4. Doctor Check Failures

**Error:**

```
Import Check: 6/8 passed
  ✗ core.intelligence.ResearchAdapter
```

**Solution:**

```bash
# Run repair script
python scripts/repair.py --auto

# Re-check
python cli.py doctor --verbose
```

#### 5. Slow Decompilation

**Issue:** JADX taking too long

**Solutions:**

```yaml
# Reduce threads in config.yaml
jadx:
  threads: 1
  timeout: 600  # Increase timeout

# Use lighter decompilation
python cli.py analyze app.apk --profile light
```

#### 6. Research API Errors

**Error:**

```
[ERROR] Authentication failed: 401 Unauthorized
```

**Solution:**

```yaml
# Update research_config.yaml
auth:
  client_id: "correct_client_id"
  client_secret: "correct_secret"

# Test authentication
python cli.py research decoy
```

### Debug Mode

Enable detailed logging:

```yaml
# config.yaml
framework:
  debug: true
```

Or with environment variable:

```bash
export XL_DEBUG=1
python cli.py analyze app.apk
```

### Getting Help

1. **Check logs**: `output/system/`
2. **Run doctor**: `python cli.py doctor --verbose`
3. **Run tests**: `pytest tests/ -v`
4. **Check issues**: GitHub Issues
5. **Documentation**: This README

---

## 🔒 Ethical Usage

This tool is designed for **ethical security research only**.

### ✅ Allowed Uses

- Security research on **your own applications**
- **Authorized penetration testing** with written permission
- **Academic research** with proper permissions
- **Bug bounty programs** within explicit scope
- **Internal security audits**

### ❌ Prohibited Uses

- Unauthorized access to applications
- Privacy violations
- Malicious modifications
- Intellectual property theft
- Illegal reverse engineering
- Commercial use without license

### Best Practices

1. **Always obtain written permission** before analyzing applications
2. **Respect privacy** - don't collect personal data
3. **Responsible disclosure** - report findings ethically
4. **Legal compliance** - follow local laws and regulations
5. **No harm** - never exploit findings maliciously

See [ETHICS.md](ETHICS.md) for full guidelines.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

Copyright (c) 2026 XL Research Team

---

## 🙏 Credits

### Dependencies

- [JADX](https://github.com/skylot/jadx) - DEX to Java decompiler
- [psutil](https://github.com/giampaolo/psutil) - System monitoring
- [PyYAML](https://github.com/yaml/pyyaml) - YAML parser
- [pytest](https://github.com/pytest-dev/pytest) - Testing framework

### Contributors

- XL Research Team
- Security Research Community

---

## 📞 Support

- **Documentation**: This README
- **Issues**: GitHub Issues
- **Email**: research@xl.co.id

---

## 🗺️ Roadmap

### v2.2 (Planned)

- [ ] Web dashboard UI
- [ ] Real-time analysis streaming
- [ ] Additional module types
- [ ] Multi-APK batch analysis
- [ ] Enhanced correlation rules

### v2.3 (Future)

- [ ] Cloud integration
- [ ] Machine learning insights
- [ ] Custom module SDK
- [ ] API versioning

---

**Made with ❤️ for ethical security research**

**Version:** 2.1.0  
**Status:** Production  
**Last Updated:** 2026-02-02
