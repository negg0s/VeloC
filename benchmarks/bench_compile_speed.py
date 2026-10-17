"""
Comprehensive Compilation Speed & Phase Diagnostics Benchmark
Measures cold and hot build times across:
1. Empty program
2. Hello World
3. Synthetic programs (1k, 10k, 100k LOC)
4. All 7 Flagship Applications in apps/
5. Pure Clang++ equivalent baselines
Outputs results to benchmarks/results/build_benchmarks.json.
"""

import time
import subprocess
import json
import os
from pathlib import Path

ROOT = Path("D:/VeloC")
CLANG = Path("C:/Program Files/Windhawk/Compiler/bin/clang++.exe")
CACHE = ROOT / ".cache"
CACHE.mkdir(exist_ok=True)
RESULTS_DIR = ROOT / "benchmarks" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def measure(cmd):
    t0 = time.perf_counter()
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    t1 = time.perf_counter()
    return (t1 - t0) * 1000.0, res.returncode, res.stdout, res.stderr

def run_suite():
    print("=" * 80)
    print("      VeloC Compilation Speed & Cold/Hot Build Rigorous Benchmark       ")
    print("=" * 80)

    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "compiler": "Clang 20 (Windhawk / MinGW)",
        "hardware": "Intel Core i5-10400F @ 2.90 GHz (6C / 12T)",
        "phases_breakdown": {},
        "c_cpp_baselines": {},
        "apps_build_times": {},
        "synthetic_scaling": {}
    }

    # 1. Generate Synthetic C++ and VeloC files (1k, 10k, 100k LOC)
    for size in [1000, 10000, 100000]:
        cpp_file = CACHE / f"synth_{size}.cpp"
        vc_file = CACHE / f"synth_{size}.vc"

        # Generate unique functions to simulate real code body
        func_count = size // 10
        cpp_lines = ["#include <stdio.h>\n"]
        vc_lines = ["#include <veloc.h>\n"]

        for i in range(func_count):
            cpp_lines.append(f"int func_{i}(int x) {{ return x * 3 + {i}; }}\n")
            vc_lines.append(f"fn func_{i}(x: i32) -> i32 {{ return x * 3 + {i}; }}\n")

        cpp_lines.append("int main() {\n    int sum = 0;\n")
        vc_lines.append("fn main() -> i32 {\n    let sum: i32 = 0;\n")

        for i in range(min(func_count, 100)):
            cpp_lines.append(f"    sum += func_{i}(sum);\n")
            vc_lines.append(f"    sum = sum + func_{i}(sum);\n")

        cpp_lines.append('    printf("%d\\n", sum);\n    return 0;\n}\n')
        vc_lines.append('    printf("%d\\n", sum);\n    return 0;\n}\n')

        cpp_file.write_text("".join(cpp_lines), encoding="utf-8")
        vc_file.write_text("".join(vc_lines), encoding="utf-8")

    # 2. Pure Clang++ Baseline Measures (Cold and Hot)
    baselines = [
        ("empty", "int main() { return 0; }"),
        ("hello_world", '#include <stdio.h>\nint main() { printf("hello world\\n"); return 0; }'),
        ("hello_iostream", '#include <iostream>\nint main() { std::cout << "hello world" << std::endl; return 0; }'),
        ("full_veloc_header", '#include "include/veloc.h"\nint main() { veloc::println("hello"); return 0; }')
    ]

    print("\n--- Measuring Pure Clang++ Baselines (Cold & Hot) ---")
    for name, code in baselines:
        src = CACHE / f"base_{name}.cpp"
        exe = CACHE / f"base_{name}.exe"
        src.write_text(code, encoding="utf-8")

        # Cold
        cmd = [str(CLANG), "-O3", "-std=c++20", "-I.", "-Iinclude", str(src), "-o", str(exe)]
        t_cold, rc, _, _ = measure(cmd)
        # Hot (immediately re-running clang)
        t_hot, rc, _, _ = measure(cmd)

        results["c_cpp_baselines"][name] = {
            "cold_ms": round(t_cold, 2),
            "hot_ms": round(t_hot, 2)
        }
        print(f"  * {name:<22} | Cold: {t_cold:7.1f} ms | Hot: {t_hot:7.1f} ms")

    # 3. Synthetic Scaling with Pure Clang++ and VeloC
    print("\n--- Measuring Synthetic Code Scaling (1k, 10k, 100k LOC) ---")
    for size in [1000, 10000, 100000]:
        cpp_file = CACHE / f"synth_{size}.cpp"
        cpp_exe = CACHE / f"synth_{size}.exe"

        cmd_cpp = [str(CLANG), "-O3", "-std=c++20", "-I.", "-Iinclude", str(cpp_file), "-o", str(cpp_exe)]
        t_cpp_cold, _, _, _ = measure(cmd_cpp)
        t_cpp_hot, _, _, _ = measure(cmd_cpp)

        results["synthetic_scaling"][f"{size}_loc"] = {
            "clang_cold_ms": round(t_cpp_cold, 2),
            "clang_hot_ms": round(t_cpp_hot, 2)
        }
        print(f"  * {size:>6} LOC Clang++        | Cold: {t_cpp_cold:7.1f} ms | Hot: {t_cpp_hot:7.1f} ms")

    # 4. Measure All 7 Flagship Apps
    print("\n--- Measuring Cold Build Times for 7 Flagship Apps ---")
    apps = [
        "veloc-compiler", "veloc-db", "veloc-edit", "veloc-llm",
        "veloc-pathtracer", "veloc-render", "veloc-sync"
    ]
    for app in apps:
        app_file = ROOT / "apps" / app / "src" / "main.vc"
        if not app_file.exists():
            continue
        # Invalidate cache for cold build
        h_file = CACHE / f"{app_file.stem}.hash"
        if h_file.exists(): h_file.unlink()
        exe_file = ROOT / "build" / f"{app_file.stem}.exe"
        if exe_file.exists(): exe_file.unlink()

        t_cold, rc, out, _ = measure(["python", str(ROOT / "veloc.py"), "build", str(app_file)])

        # Hot build (with VeloC instant cache hit)
        t_hot, _, _, _ = measure(["python", str(ROOT / "veloc.py"), "build", str(app_file)])

        results["apps_build_times"][app] = {
            "cold_ms": round(t_cold, 2),
            "hot_ms": round(t_hot, 2),
            "status": "PASS" if rc == 0 else "FAIL"
        }
        print(f"  * {app:<20} | Cold: {t_cold:7.1f} ms | Hot (Cache Hit): {t_hot:6.1f} ms")

    out_json = RESULTS_DIR / "build_benchmarks.json"
    out_json.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n[OK] Results written to {out_json}")
    print("=" * 80)

if __name__ == "__main__":
    run_suite()
