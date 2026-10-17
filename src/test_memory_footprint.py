"""
Compiler Memory Footprint Benchmark (Peak RSS on 100k and 1M LOC)
Measures RAM usage during parsing and transpilation of large synthetic programs.
"""

import os
import sys
import time
import tracemalloc
from pathlib import Path

ROOT_DIR = Path("D:/VeloC")
sys.path.insert(0, str(ROOT_DIR / "src"))
from lexer import Lexer
from parser import Parser
from codegen import CppCodegen
from transpiler import VeloCTranspiler

def generate_synthetic_code(lines_count: int) -> str:
    func_count = lines_count // 10
    chunks = ["// VeloC Synthetic Codebase\n"]
    for i in range(func_count):
        chunks.append(f"fn func_{i}(x: i32) -> i32 {{\n    return x * 2 + {i};\n}}\n")
    chunks.append("fn main() -> i32 {\n    return func_0(10);\n}\n")
    return "".join(chunks)

def benchmark_memory(lines_count: int):
    print(f"\n--- Benchmarking Memory on {lines_count:,} Lines of Code ---")
    tracemalloc.start()
    t0 = time.perf_counter()

    source = generate_synthetic_code(lines_count)
    gen_time = (time.perf_counter() - t0) * 1000.0

    t1 = time.perf_counter()
    transpiler = VeloCTranspiler(str(ROOT_DIR / "include"))
    cpp_out = transpiler.transpile_source(source)
    transpile_time = (time.perf_counter() - t1) * 1000.0

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"  * Generated {lines_count:,} LOC in: {gen_time:.1f} ms")
    print(f"  * Transpiled to {len(cpp_out.splitlines()):,} C++ LOC in: {transpile_time:.1f} ms")
    print(f"  * Peak Memory Allocation: {peak / (1024.0 * 1024.0):.2f} MB")
    print(f"  * Current Memory Retained: {current / (1024.0 * 1024.0):.2f} MB")

    return {
        "lines": lines_count,
        "peak_mb": round(peak / (1024.0 * 1024.0), 2),
        "transpile_ms": round(transpile_time, 1)
    }

if __name__ == "__main__":
    print("=" * 60)
    print("          VeloC Compiler Peak RSS Memory Audit                 ")
    print("=" * 60)
    m_100k = benchmark_memory(100000)
    # 1 Million LOC test
    m_1m = benchmark_memory(1000000)
    print("=" * 60)
    print(f"[SUMMARY] 100k LOC Peak: {m_100k['peak_mb']} MB in {m_100k['transpile_ms']} ms")
    print(f"[SUMMARY] 1M LOC Peak  : {m_1m['peak_mb']} MB in {m_1m['transpile_ms']} ms")
    print("=" * 60)
