"""
XL Research Framework - CLI Tests

Tests for command line interface.
"""

import pytest
import subprocess
import sys
from pathlib import Path


# Project root for CLI
PROJECT_ROOT = Path(__file__).parent.parent


class TestCLIImport:
    """Test CLI module imports"""
    
    def test_cli_module_import(self):
        """CLI module should import without errors"""
        # Test by running Python import
        result = subprocess.run(
            [sys.executable, "-c", "import cli"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Import failed: {result.stderr}"


class TestCLIHelp:
    """Test CLI help output"""
    
    def test_main_help(self):
        """Main CLI should show help"""
        result = subprocess.run(
            [sys.executable, "cli.py", "--help"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "XL Research Framework" in result.stdout or "usage" in result.stdout.lower()
    
    def test_analyze_help(self):
        """Analyze command should show help"""
        result = subprocess.run(
            [sys.executable, "cli.py", "analyze", "--help"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "apk" in result.stdout.lower() or "profile" in result.stdout.lower()
    
    def test_research_help(self):
        """Research command should show help"""
        result = subprocess.run(
            [sys.executable, "cli.py", "research", "--help"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "enumerate" in result.stdout.lower()
        assert "analyze" in result.stdout.lower()
    
    def test_list_help(self):
        """List command should show help"""
        result = subprocess.run(
            [sys.executable, "cli.py", "list", "--help"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0


class TestCLIVersion:
    """Test CLI version output"""
    
    def test_version_flag(self):
        """--version should show version"""
        result = subprocess.run(
            [sys.executable, "cli.py", "--version"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        # Version should contain a number
        assert any(c.isdigit() for c in result.stdout)


class TestCLIListModules:
    """Test list modules command"""
    
    def test_list_modules(self):
        """list modules should work"""
        result = subprocess.run(
            [sys.executable, "cli.py", "list", "modules"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        
        # Should not crash
        assert result.returncode == 0


class TestCLIProfile:
    """Test profile command"""
    
    def test_profile_light(self):
        """profile light should work"""
        result = subprocess.run(
            [sys.executable, "cli.py", "profile", "light"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
    
    def test_profile_xl(self):
        """profile xl should work"""
        result = subprocess.run(
            [sys.executable, "cli.py", "profile", "xl"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
    
    def test_profile_full(self):
        """profile full should work"""
        result = subprocess.run(
            [sys.executable, "cli.py", "profile", "full"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0


class TestCLIAnalyze:
    """Test analyze command (requires mock APK)"""
    
    def test_analyze_missing_apk(self):
        """analyze should fail gracefully for missing APK"""
        result = subprocess.run(
            [sys.executable, "cli.py", "analyze", "nonexistent.apk"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        
        # Should fail but not crash
        assert result.returncode != 0 or "not found" in result.stderr.lower() or "not found" in result.stdout.lower()


class TestCLIResearch:
    """Test research subcommand"""
    
    def test_research_enumerate_help(self):
        """research enumerate --help should work"""
        result = subprocess.run(
            [sys.executable, "cli.py", "research", "enumerate", "--help"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "max" in result.stdout.lower() or "attempts" in result.stdout.lower()
    
    def test_research_analyze_help(self):
        """research analyze --help should work"""
        result = subprocess.run(
            [sys.executable, "cli.py", "research", "analyze", "--help"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
    
    def test_research_validate_help(self):
        """research validate --help should work"""
        result = subprocess.run(
            [sys.executable, "cli.py", "research", "validate", "--help"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
    
    def test_research_decoy_help(self):
        """research decoy --help should work"""
        result = subprocess.run(
            [sys.executable, "cli.py", "research", "decoy", "--help"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
