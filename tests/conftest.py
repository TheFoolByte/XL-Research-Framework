"""
XL Research Framework - Test Configuration

Pytest configuration and shared fixtures.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path for testing
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def mock_apk_path(tmp_path):
    """Create a mock APK file for testing"""
    mock_apk = tmp_path / "test_app.apk"
    
    # Create minimal valid ZIP structure (APK is a ZIP file)
    import zipfile
    with zipfile.ZipFile(mock_apk, 'w') as zf:
        # Add mock AndroidManifest.xml
        manifest_content = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.test.mockapp"
    android:versionCode="1"
    android:versionName="1.0">
    <uses-permission android:name="android.permission.INTERNET"/>
    <application android:label="MockApp">
        <activity android:name=".MainActivity"/>
    </application>
</manifest>"""
        zf.writestr("AndroidManifest.xml", manifest_content)
        
        # Add mock Java file
        java_content = """package com.test.mockapp;
public class MainActivity {
    private static final String API_KEY = "test_api_key_12345";
    private static final String BASE_URL = "https://api.test.com/v1/";
}"""
        zf.writestr("sources/com/test/mockapp/MainActivity.java", java_content)
    
    return str(mock_apk)


@pytest.fixture
def mock_source_dir(tmp_path):
    """Create a mock source directory for testing"""
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    
    # Create mock Java file
    java_dir = source_dir / "com" / "test" / "app"
    java_dir.mkdir(parents=True)
    
    java_file = java_dir / "Config.java"
    java_file.write_text("""package com.test.app;

public class Config {
    public static final String API_KEY = "AIzaSyTest1234567890123456789";
    public static final String BASE_URL = "https://api.myxl.xlaxiata.co.id/";
    public static final String SECRET = "my_secret_key_12345";
}
""")
    
    return str(source_dir)


@pytest.fixture
def sample_analysis_results():
    """Sample analysis results for testing reporters"""
    return {
        "apk": "test_app.apk",
        "profile": "xl",
        "timestamp": "2024-01-01T12:00:00",
        "duration_seconds": 30.5,
        "total_findings": 5,
        "results": {
            "api_scanner": {
                "count": 2,
                "findings": [
                    {
                        "category": "API",
                        "type": "rest_endpoint",
                        "message": "REST endpoint found",
                        "severity": "high",
                        "file": "Config.java",
                        "value": "/api/v1/users"
                    }
                ]
            },
            "env_extractor": {
                "count": 1,
                "findings": [
                    {
                        "category": "Config",
                        "type": "generic_api_key",
                        "message": "API key detected",
                        "severity": "critical",
                        "file": "Config.java",
                        "value": "AIza***MASKED***"
                    }
                ]
            }
        }
    }


@pytest.fixture
def mock_research_config():
    """Mock research configuration"""
    return {
        "enabled": True,
        "analyzer_enabled": True,
        "enumerator_enabled": False,
        "validator_enabled": True,
        "decoy_enabled": True,
    }
