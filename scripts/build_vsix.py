"""
VeloC VS Code Extension VSIX Packager
Packages editors/vscode into a standards-compliant .vsix archive for VS Code & Open-VSX.
"""

import os
import sys
import json
import zipfile
from pathlib import Path

ROOT = Path("D:/VeloC")
VSCODE_DIR = ROOT / "editors" / "vscode"
DIST_DIR = ROOT / "dist"

CONTENT_TYPES_XML = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="application/json" />
  <Default Extension="js" ContentType="application/javascript" />
  <Default Extension="vsixmanifest" ContentType="text/xml" />
</Types>
"""

VSIX_MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
  <Metadata>
    <Identity Id="veloc-vscode" Version="1.0.0" Language="en-US" Publisher="veloc-lang" />
    <DisplayName>VeloC Language Support</DisplayName>
    <Description>Rich language support for the high-performance VeloC programming language</Description>
  </Metadata>
  <Installation>
    <InstallationTarget Id="Microsoft.VisualStudio.Code"/>
  </Installation>
  <Dependencies/>
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true" />
  </Assets>
</PackageManifest>
"""

def build_vsix() -> Path:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    vsix_path = DIST_DIR / "veloc-vscode-1.0.0.vsix"
    
    print(f"[*] Packaging VeloC VS Code Extension into: {vsix_path.name}...")
    with zipfile.ZipFile(vsix_path, "w", zipfile.ZIP_DEFLATED) as zip_f:
        zip_f.writestr("[Content_Types].xml", CONTENT_TYPES_XML)
        zip_f.writestr("extension.vsixmanifest", VSIX_MANIFEST)
        
        for file in VSCODE_DIR.rglob("*"):
            if file.is_file() and not file.name.endswith(".vsix"):
                rel_path = file.relative_to(VSCODE_DIR)
                zip_f.write(file, f"extension/{rel_path}")

    print(f"[+] VSIX Package created successfully: {vsix_path} ({vsix_path.stat().st_size} bytes)")
    return vsix_path

if __name__ == "__main__":
    build_vsix()
