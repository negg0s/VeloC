"""
VeloC Precompiled Header (PCH) & Toolchain Optimizer Manager
Generates and manages cached PCH files for veloc.h and veloc_core.h,
matching compiler flags bit-for-bit to ensure flawless AST cache hits.
"""

import os
import hashlib
import subprocess
import time
from pathlib import Path

ROOT_DIR = Path("D:/VeloC")
INCLUDE_DIR = ROOT_DIR / "include"
CACHE_DIR = ROOT_DIR / ".cache"
CLANG_PATH = Path("C:/Program Files/Windhawk/Compiler/bin/clang++.exe")
LLD_PATH = Path("C:/Program Files/Windhawk/Compiler/bin/ld.lld.exe")

class PchManager:
    def __init__(self, root: Path = ROOT_DIR):
        self.root = root
        self.cache_dir = root / ".cache"
        self.include_dir = root / "include"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_pch_flags(self, opt_level: str = "-O3", profile: str = "max-perf", fp_mode: str = "strict", enable_ftz: bool = False) -> list:
        from fp_policy import FloatingPointPolicy
        fp_policy = FloatingPointPolicy(fp_mode, enable_ftz=enable_ftz)
        math_flags = fp_policy.get_compiler_flags()
        flags = [
            "-std=c++20",
            opt_level,
            "-march=native",
            "-static",
            "-fwrapv",
            "-fstack-protector-strong",
            "-ftrivial-auto-var-init=zero",
            *math_flags,
            "-fno-exceptions",
            "-fno-rtti",
            "-fomit-frame-pointer",
            "-I.",
            f"-I{self.include_dir}"
        ]
        return flags

    def get_compiler_fingerprint(self, opt_level: str = "-O3", profile: str = "max-perf", fp_mode: str = "strict", enable_ftz: bool = False) -> str:
        flags_str = " ".join(self.get_pch_flags(opt_level, profile, fp_mode, enable_ftz))
        clang_mtime = str(CLANG_PATH.stat().st_mtime) if CLANG_PATH.exists() else "0"
        key = f"{CLANG_PATH}:{clang_mtime}:{flags_str}"
        return hashlib.sha256(key.encode()).hexdigest()[:12]

    def ensure_pch(self, header_name: str = "veloc.h", opt_level: str = "-O3", profile: str = "max-perf", fp_mode: str = "strict", enable_ftz: bool = False, verbose: bool = False) -> Path:
        header_path = self.include_dir / header_name
        if not header_path.exists():
            return None

        header_bytes = header_path.read_bytes()
        header_hash = hashlib.sha256(header_bytes).hexdigest()[:12]
        comp_hash = self.get_compiler_fingerprint(opt_level, profile, fp_mode, enable_ftz)
        pch_stem = f"{header_path.stem}_{comp_hash}_{header_hash}"
        pch_path = self.cache_dir / f"{pch_stem}.pch"

        if pch_path.exists():
            return pch_path

        if verbose:
            print(f"[VeloC PCH] Precompiling {header_name} ({opt_level}, profile={profile})...")

        t0 = time.perf_counter()
        flags = self.get_pch_flags(opt_level, profile)
        cmd = [
            str(CLANG_PATH),
            "-x", "c++-header",
            *flags,
            str(header_path),
            "-o", str(pch_path)
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        dur = (time.perf_counter() - t0) * 1000.0

        if res.returncode == 0:
            if verbose:
                print(f"[VeloC PCH] Generated {pch_path.name} in {dur:.1f} ms")
            return pch_path
        else:
            if verbose:
                print(f"[VeloC PCH Warning] Failed to generate PCH: {res.stderr[:250]}")
            return None
