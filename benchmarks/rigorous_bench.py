import os
import sys
import subprocess
import json
from pathlib import Path

ROOT_DIR = Path("D:/VeloC")
BUILD_DIR = ROOT_DIR / "build"
BENCH_DIR = ROOT_DIR / "benchmarks"
RESULTS_DIR = BENCH_DIR / "results"
CLANG_PATH = Path("C:/Program Files/Windhawk/Compiler/bin/clang++.exe")
INCLUDE_DIR = ROOT_DIR / "include"

def run_scientific_benchmarks(update_readme: bool = False):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    src_cpp = BENCH_DIR / "rigorous_bench.cpp"
    exe_path = BUILD_DIR / "rigorous_bench.exe"
    json_path = RESULTS_DIR / "cometlake_i5_10400f.json"

    print("[VeloC Benchmark Suite] Compiling rigorous_bench.cpp with Clang 20 (-O3 -march=native -ffast-math -static)...")
    cmd = [
        str(CLANG_PATH),
        str(src_cpp),
        "-o", str(exe_path),
        "-O3",
        "-march=native",
        "-ffast-math",
        "-fno-exceptions",
        "-fno-rtti",
        "-static",
        f"-I{INCLUDE_DIR}",
        "-lws2_32"
    ]
    res_comp = subprocess.run(cmd, capture_output=True, text=True)
    if res_comp.returncode != 0:
        print("[Build Error]:", res_comp.stderr)
        sys.exit(res_comp.returncode)

    print("[VeloC Benchmark Suite] Executing 30-run scientific measurement suite...")
    res_run = subprocess.run([str(exe_path)], capture_output=True, text=True)
    print(res_run.stdout)
    if res_run.returncode != 0:
        print("[Execution Error]:", res_run.stderr)
        sys.exit(res_run.returncode)

    if not json_path.exists():
        print(f"[Error]: Results JSON was not found at {json_path}")
        return

    data = json.loads(json_path.read_text(encoding="utf-8"))
    print("\nVerified Honest Benchmark Measurements:")
    print(f"{'Benchmark':<30} | {'Data Size':<25} | {'Baseline (Median)':<18} | {'VeloC (Median)':<18} | {'Speedup'}")
    print("-" * 105)
    for b in data.get("benchmarks", []):
        print(f"{b['name']:<30} | {b['data_size']:<25} | {b['baseline_median_ms']:<15.2f} ms | {b['veloc_median_ms']:<15.2f} ms | {b['speedup']:.2f}x")

if __name__ == "__main__":
    update_readme = "--update-readme" in sys.argv
    run_scientific_benchmarks(update_readme=update_readme)
