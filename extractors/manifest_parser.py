"""
XL Research Framework v2 - Manifest Parser

Parses AndroidManifest.xml for app metadata, permissions, and components.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from core.logger import log


# Android XML namespace
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"


@dataclass
class ManifestInfo:
    """Parsed manifest information"""
    package: str = ""
    version_name: str = ""
    version_code: str = ""
    min_sdk: str = ""
    target_sdk: str = ""
    permissions: List[str] = field(default_factory=list)
    activities: List[Dict] = field(default_factory=list)
    services: List[Dict] = field(default_factory=list)
    receivers: List[Dict] = field(default_factory=list)
    providers: List[Dict] = field(default_factory=list)
    uses_features: List[str] = field(default_factory=list)


class ManifestParser:
    """
    Parser for AndroidManifest.xml.
    
    Extracts:
    - Package info
    - Permissions
    - Components (activities, services, receivers, providers)
    - SDK versions
    """
    
    def parse(self, source_dir: str) -> Optional[ManifestInfo]:
        """
        Parse AndroidManifest.xml from source directory.
        
        Args:
            source_dir: Path to extracted APK sources
            
        Returns:
            ManifestInfo or None if not found
        """
        manifest_path = self._find_manifest(source_dir)
        
        if not manifest_path:
            log.warning("AndroidManifest.xml not found")
            return None
        
        log.info(f"Parsing manifest: {manifest_path}")
        
        try:
            return self._parse_file(manifest_path)
        except Exception as e:
            log.error(f"Failed to parse manifest: {e}")
            return None
    
    def _find_manifest(self, source_dir: str) -> Optional[Path]:
        """Find AndroidManifest.xml in source directory"""
        source = Path(source_dir)
        
        # Common locations
        candidates = [
            source / "AndroidManifest.xml",
            source / "resources" / "AndroidManifest.xml",
            source.parent / "AndroidManifest.xml",
        ]
        
        for path in candidates:
            if path.exists():
                return path
        
        # Search recursively
        for path in source.rglob("AndroidManifest.xml"):
            return path
        
        return None
    
    def _parse_file(self, path: Path) -> ManifestInfo:
        """Parse manifest file"""
        tree = ET.parse(path)
        root = tree.getroot()
        
        info = ManifestInfo()
        
        # Package info
        info.package = root.get("package", "")
        info.version_name = root.get(f"{ANDROID_NS}versionName", "")
        info.version_code = root.get(f"{ANDROID_NS}versionCode", "")
        
        # SDK versions
        uses_sdk = root.find("uses-sdk")
        if uses_sdk is not None:
            info.min_sdk = uses_sdk.get(f"{ANDROID_NS}minSdkVersion", "")
            info.target_sdk = uses_sdk.get(f"{ANDROID_NS}targetSdkVersion", "")
        
        # Permissions
        for perm in root.findall("uses-permission"):
            name = perm.get(f"{ANDROID_NS}name", "")
            if name:
                info.permissions.append(name)
        
        # Components
        app = root.find("application")
        if app is not None:
            info.activities = self._parse_components(app, "activity")
            info.services = self._parse_components(app, "service")
            info.receivers = self._parse_components(app, "receiver")
            info.providers = self._parse_components(app, "provider")
        
        # Features
        for feature in root.findall("uses-feature"):
            name = feature.get(f"{ANDROID_NS}name", "")
            if name:
                info.uses_features.append(name)
        
        return info
    
    def _parse_components(self, app: ET.Element, tag: str) -> List[Dict]:
        """Parse component elements"""
        components = []
        
        for elem in app.findall(tag):
            name = elem.get(f"{ANDROID_NS}name", "")
            exported = elem.get(f"{ANDROID_NS}exported", "")
            
            # Get intent filters
            intents = []
            for intent in elem.findall("intent-filter"):
                actions = [a.get(f"{ANDROID_NS}name", "") 
                          for a in intent.findall("action")]
                categories = [c.get(f"{ANDROID_NS}name", "") 
                             for c in intent.findall("category")]
                intents.append({
                    "actions": actions,
                    "categories": categories
                })
            
            components.append({
                "name": name,
                "exported": exported,
                "intent_filters": intents
            })
        
        return components
