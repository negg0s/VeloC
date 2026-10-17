import time
import subprocess
from pathlib import Path

CLANG = "C:/Program Files/Windhawk/Compiler/bin/clang++.exe"
src = Path(".cache/test_lean.cpp")

t0 = time.perf_counter()
res = subprocess.run([CLANG, "-O3", "-std=c++20", "-Iinclude", "-include-pch", ".cache/veloc_core.pch", "-fuse-ld=lld", str(src), "-o", ".cache/test_lean_pch.exe"], capture_output=True, text=True)
t1 = time.perf_counter()

print(f"Lean PCH + LLD Compile Time: {(t1 - t0)*1000:.1f} ms (rc={res.returncode})")
