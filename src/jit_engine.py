"""
VeloC In-Process JIT Execution Engine
Provides ultra-low-latency in-memory compilation and dynamic function symbol invocation
for REPL, Jupyter Notebook kernel, and interactive rapid prototyping.
"""

import os
import sys
import time
import ctypes
import hashlib
import subprocess
from pathlib import Path
from typing import Any, Tuple, Optional, Callable

ROOT = Path("D:/VeloC")
CACHE_DIR = ROOT / ".cache" / "jit"
CLANG_PATH = Path("C:/Program Files/Windhawk/Compiler/bin/clang++.exe")

class JITEngine:
    def __init__(self, cache_dir: Path = CACHE_DIR, clang_path: Path = CLANG_PATH):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.clang_path = clang_path
        self._loaded_modules = {}

    def compile_and_load(self, cpp_code: str, symbol_name: str = "veloc_entry") -> Tuple[Callable, float]:
        """
        Compiles C++ snippet into a dynamic shared library in-memory / cache,
        loads it into the current process address space, and returns the callable function.
        """
        t0 = time.perf_counter()
        code_hash = hashlib.sha256(cpp_code.encode("utf-8")).hexdigest()[:16]
        dll_path = self.cache_dir / f"jit_{code_hash}.dll"
        cpp_path = self.cache_dir / f"jit_{code_hash}.cpp"

        if not dll_path.exists():
            cpp_path.write_text(cpp_code, encoding="utf-8")
            # Compile with Clang 64-bit DLL flags
            cmd = [
                str(self.clang_path),
                "-target", "x86_64-w64-windows-gnu",
                "-shared",
                "-O2",
                "-mavx2",
                "-I", str(ROOT / "include"),
                str(cpp_path),
                "-o", str(dll_path)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                raise RuntimeError(f"JIT Compilation Failed:\n{res.stderr}")

        # Load shared library via ctypes
        cdll = ctypes.CDLL(str(dll_path))
        self._loaded_modules[code_hash] = cdll

        func = getattr(cdll, symbol_name)
        compile_time_ms = (time.perf_counter() - t0) * 1000.0
        return func, compile_time_ms

    def eval_expression(self, expr: str) -> Tuple[float, float, float]:
        """
        Evaluates a mathematical or scalar expression JIT in-process.
        Returns (result, compile_time_ms, exec_time_us).
        """
        wrapper_code = f"""#include "veloc.h"

extern "C" __declspec(dllexport) double veloc_entry() {{
    return (double)({expr});
}}
"""
        func, compile_ms = self.compile_and_load(wrapper_code, "veloc_entry")
        func.restype = ctypes.c_double
        
        t_exec_start = time.perf_counter()
        val = func()
        exec_us = (time.perf_counter() - t_exec_start) * 1000000.0
        return val, compile_ms, exec_us

if __name__ == "__main__":
    jit = JITEngine()
    print("[*] Testing VeloC In-Process JIT Execution Engine...")
    
    # 1. Cold JIT compilation
    val, comp_ms, exec_us = jit.eval_expression("3.1415926535 * 42.0 + 100.0")
    print(f"  [Cold JIT] Result: {val:.4f} | Compile: {comp_ms:.2f} ms | Exec: {exec_us:.2f} µs")
    assert abs(val - 231.94689) < 1e-4, "Incorrect JIT computation result"

    # 2. Warm JIT invocation
    val_warm, comp_warm_ms, exec_warm_us = jit.eval_expression("3.1415926535 * 42.0 + 100.0")
    print(f"  [Warm JIT] Result: {val_warm:.4f} | Load: {comp_warm_ms:.2f} ms | Exec: {exec_warm_us:.2f} µs")
    assert comp_warm_ms < 5.0, f"Warm JIT load took too long: {comp_warm_ms:.2f} ms"
    print("[SUCCESS] VeloC In-Process JIT Engine verified operational!")
