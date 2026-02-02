"""
XL Research Framework v2.1 - Partial JADX Extractor

Supports three extraction levels for memory optimization:
- manifest: Extract only AndroidManifest.xml (fastest)
- sources: Decompile Java sources only (balanced)
- full: Full decompilation with resources (comprehensive)
"""

import subprocess
import zipfile
from pathlib import Path
from typing import Optional

from core.config import config
from core.logger import log


class PartialJADX:
    """
    APK extractor with partial decompilation support.
    
    Extraction levels:
    - manifest: ZIP extract only (AndroidManifest.xml)
    - sources: JADX with --no-res (Java sources only)
    - full: JADX full decompile
    """
    
    def __init__(self):
        self._jadx_path = config.jadx_path
        self._output_base = config.output_dir / "extracted"
    
    def extract(self, apk_path: str, level: str = "sources") -> str:
        """
        Extract APK with specified level.
        
        Args:
            apk_path: Path to APK
            level: Extraction level (manifest, sources, full)
            
        Returns:
            Path to extracted directory
        """
        apk = Path(apk_path)
        
        if not apk.exists():
            raise FileNotFoundError(f"APK not found: {apk_path}")
        
        out_path = self._output_base / apk.stem
        out_path.mkdir(parents=True, exist_ok=True)
        
        log.info(f"Extraction level: {level}")
        
        if level == "manifest":
            return self._extract_manifest_only(apk, out_path)
        elif level == "sources":
            return self._jadx_sources_only(apk, out_path)
        else:  # full
            return self._jadx_full(apk, out_path)
    
    def _extract_manifest_only(self, apk: Path, output: Path) -> str:
        """
        Fastest: Extract only basic files from APK as ZIP.
        Memory efficient, but limited analysis.
        """
        log.info("Manifest-only extraction (ZIP)...")
        
        extract_dir = output / "extracted"
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with zipfile.ZipFile(apk, 'r') as zf:
                # Extract only specific files
                targets = [
                    "AndroidManifest.xml",
                    "assets/",
                    "res/values/strings.xml",
                ]
                
                for name in zf.namelist():
                    if any(name.startswith(t) or name == t for t in targets):
                        zf.extract(name, extract_dir)
            
            log.success(f"Extracted manifest and assets")
            return str(extract_dir)
            
        except Exception as e:
            log.error(f"Extraction failed: {e}")
            # Fallback to full ZIP extraction
            return self._extract_zip_full(apk, output)
    
    def _jadx_sources_only(self, apk: Path, output: Path) -> str:
        """
        Balanced: Decompile Java sources only, skip resources.
        Good balance of analysis power and memory.
        """
        if not self._has_jadx():
            log.warning("JADX not found, falling back to ZIP")
            return self._extract_zip_full(apk, output)
        
        log.info("Decompiling sources only (JADX --no-res)...")
        
        try:
            result = subprocess.run(
                [str(self._jadx_path), "-d", str(output), "--no-res", str(apk)],
                capture_output=True,
                text=True,
                shell=True,
                timeout=config.get("jadx.timeout", 300)
            )
            
            if result.returncode == 0:
                log.success("Sources decompiled")
                sources = output / "sources"
                return str(sources if sources.exists() else output)
            else:
                log.warning(f"JADX failed: {result.stderr[:100]}")
                return self._extract_zip_full(apk, output)
                
        except subprocess.TimeoutExpired:
            log.error("JADX timed out")
            return self._extract_zip_full(apk, output)
        except Exception as e:
            log.error(f"JADX error: {e}")
            return self._extract_zip_full(apk, output)
    
    def _jadx_full(self, apk: Path, output: Path) -> str:
        """
        Comprehensive: Full JADX decompilation.
        Most thorough but highest memory usage.
        """
        if not self._has_jadx():
            log.warning("JADX not found, falling back to ZIP")
            return self._extract_zip_full(apk, output)
        
        log.info("Full decompilation (JADX)...")
        
        try:
            result = subprocess.run(
                [str(self._jadx_path), "-d", str(output), str(apk)],
                capture_output=True,
                text=True,
                shell=True,
                timeout=config.get("jadx.timeout", 600)
            )
            
            if result.returncode == 0:
                log.success("Full decompilation complete")
                sources = output / "sources"
                return str(sources if sources.exists() else output)
            else:
                log.warning(f"JADX failed: {result.stderr[:100]}")
                return self._extract_zip_full(apk, output)
                
        except subprocess.TimeoutExpired:
            log.error("JADX timed out")
            return self._extract_zip_full(apk, output)
        except Exception as e:
            log.error(f"JADX error: {e}")
            return self._extract_zip_full(apk, output)
    
    def _extract_zip_full(self, apk: Path, output: Path) -> str:
        """Fallback: Full ZIP extraction"""
        log.info("Extracting APK as ZIP (fallback)...")
        
        extract_dir = output / "extracted"
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with zipfile.ZipFile(apk, 'r') as zf:
                zf.extractall(extract_dir)
            
            log.success(f"ZIP extraction complete")
            return str(extract_dir)
        except Exception as e:
            log.error(f"ZIP extraction failed: {e}")
            raise
    
    def _has_jadx(self) -> bool:
        """Check if JADX is available"""
        return Path(self._jadx_path).exists()
