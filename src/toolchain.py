"""Toolchain resolution shared by veloc.py and src/* modules.

Order (VELOC_CLANG / VELOC_LLD env, PATH, then typical Windows locations). A
missing toolchain is reported explicitly by callers instead of being assumed.
"""
import os
import shutil
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent          # .../src
ROOT_DIR = PACKAGE_ROOT.parent                           # repo root


def _guard_env_path(name: str) -> str | None:
    value = os.environ.get(name, "").strip()
    return value or None


def find_clang() -> Path | None:
    candidates: list[Path] = []
    env = _guard_env_path("VELOC_CLANG")
    if env:
        candidates.append(Path(env))
    which = shutil.which("clang++") or shutil.which("clang")
    if which:
        candidates.append(Path(which))
    if sys.platform == "win32":
        candidates.append(Path("C:/Program Files/LLVM/bin/clang++.exe"))
        candidates.append(Path("C:/Program Files/Windhawk/Compiler/bin/clang++.exe"))
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def find_lld(clang_path: Path | None = None) -> Path | None:
    candidates: list[Path] = []
    env = _guard_env_path("VELOC_LLD")
    if env:
        candidates.append(Path(env))
    which = shutil.which("ld.lld")
    if which:
        candidates.append(Path(which))
    if clang_path is not None:
        candidates.append(clang_path.with_name("ld.lld.exe"))
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


CLANG_PATH = find_clang()
LLD_PATH = find_lld(CLANG_PATH)


def clang_status_line() -> str:
    if CLANG_PATH is None:
        return "clang++ NOT FOUND (set VELOC_CLANG or install LLVM on PATH)"
    version = "unknown"
    try:
        import subprocess
        res = subprocess.run([str(CLANG_PATH), "--version"], capture_output=True, text=True, timeout=10)
        if res.returncode == 0 and res.stdout:
            version = res.stdout.splitlines()[0].strip()
    except Exception:
        pass
    return f"{CLANG_PATH} ({version})"
