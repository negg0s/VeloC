"""
VeloC 1.0.0 GA Distribution Packager
Packages complete release archives for Windows and Linux with SHA-256 integrity manifests.
"""

import os
import sys
import shutil
import hashlib
import zipfile
import tarfile
from pathlib import Path

ROOT = Path("D:/VeloC")
DIST_DIR = ROOT / "dist"

INSTALL_PS1 = """# VeloC Windows Installation Script
$installPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Write-Host "Installing VeloC 1.0.0 GA from: $installPath" -ForegroundColor Cyan

# Add to user PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$installPath*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$installPath", "User")
    Write-Host "[SUCCESS] Added VeloC to User PATH!" -ForegroundColor Green
} else {
    Write-Host "[INFO] VeloC is already in User PATH." -ForegroundColor Yellow
}

Write-Host "VeloC 1.0.0 GA is ready to use! Restart terminal and run: veloc dev-setup" -ForegroundColor Green
"""

INSTALL_SH = """#!/usr/bin/env bash
# VeloC Linux/macOS Installation Script
set -e
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo -e "\\033[36mInstalling VeloC 1.0.0 GA from: $INSTALL_DIR\\033[0m"

BIN_PATH="/usr/local/bin/veloc"
if [ -w "/usr/local/bin" ]; then
    ln -sf "$INSTALL_DIR/veloc.py" "$BIN_PATH"
    chmod +x "$INSTALL_DIR/veloc.py"
    echo -e "\\033[32m[SUCCESS] Linked VeloC to $BIN_PATH\\033[0m"
else
    echo "Run with sudo to install globally: sudo ln -sf $INSTALL_DIR/veloc.py /usr/local/bin/veloc"
fi
"""

def compute_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with file_path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def package_distribution(version: str = "1.0.0"):
    print("=" * 60)
    print(f"        Building VeloC {version} GA Distribution Packages        ")
    print("=" * 60)

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    pkg_name = f"veloc-{version}-windows-x64"
    staging_dir = DIST_DIR / pkg_name

    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy essential files
    copy_files = [
        "veloc.py", "veloc.bat", "README.md", "CHANGELOG.md", "DECISIONS.md",
        "SECURITY.md", "LICENSE", "ROADMAP.md"
    ]
    for cf in copy_files:
        src_f = ROOT / cf
        if src_f.exists():
            shutil.copy2(src_f, staging_dir / cf)

    # 2. Copy directories
    copy_dirs = ["include", "src", "cmake", "docs", "examples"]
    for cd in copy_dirs:
        src_d = ROOT / cd
        if src_d.exists():
            shutil.copytree(src_d, staging_dir / cd, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.o", "*.obj", "*.exe"))

    # 3. Add installation scripts
    (staging_dir / "install.ps1").write_text(INSTALL_PS1, encoding="utf-8")
    (staging_dir / "install.sh").write_text(INSTALL_SH, encoding="utf-8")

    # 4. Create ZIP archive
    zip_path = DIST_DIR / f"{pkg_name}.zip"
    print(f"[*] Compressing Windows ZIP archive: {zip_path.name}...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_f:
        for file in staging_dir.rglob("*"):
            if file.is_file():
                rel_path = file.relative_to(DIST_DIR)
                zip_f.write(file, rel_path)

    # 5. Create tar.gz archive for Linux/Unix
    tar_name = f"veloc-{version}-linux-x64.tar.gz"
    tar_path = DIST_DIR / tar_name
    print(f"[*] Compressing Linux Tarball archive: {tar_name}...")
    with tarfile.open(tar_path, "w:gz") as tar_f:
        for file in staging_dir.rglob("*"):
            if file.is_file():
                rel_path = file.relative_to(staging_dir)
                tar_f.add(file, arcname=f"veloc-{version}/{rel_path}")

    # 6. Generate SHA256SUMS manifest
    zip_hash = compute_sha256(zip_path)
    tar_hash = compute_sha256(tar_path)
    manifest = f"""# VeloC {version} GA Release Checksums
{zip_hash}  {zip_path.name}
{tar_hash}  {tar_path.name}
"""
    manifest_path = DIST_DIR / "SHA256SUMS"
    manifest_path.write_text(manifest, encoding="utf-8")

    print("[+] Packaging Complete!")
    print(f"  * Windows ZIP: {zip_path} ({zip_path.stat().st_size / 1024 / 1024:.2f} MB)")
    print(f"    SHA-256: {zip_hash}")
    print(f"  * Linux Tarball: {tar_path} ({tar_path.stat().st_size / 1024 / 1024:.2f} MB)")
    print(f"    SHA-256: {tar_hash}")
    print(f"  * Checksums: {manifest_path}")

    return {
        "zip": zip_path,
        "tar": tar_path,
        "manifest": manifest_path,
        "zip_hash": zip_hash,
        "tar_hash": tar_hash
    }

if __name__ == "__main__":
    package_distribution()
