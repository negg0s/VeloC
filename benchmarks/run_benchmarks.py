import os
import sys
import time
import subprocess
import re
from pathlib import Path

ROOT_DIR = Path("D:/VeloC")
BUILD_DIR = ROOT_DIR / "build"
BENCH_DIR = ROOT_DIR / "benchmarks"
CLANG_PATH = Path("C:/Program Files/Windhawk/Compiler/bin/clang++.exe")

def run_benchmark():
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    cpp_src = BENCH_DIR / "cpp_standard.cpp"
    cpp_exe = BUILD_DIR / "cpp_standard.exe"
    vc_src = BENCH_DIR / "veloc_benchmark.vc"
    vc_exe = BUILD_DIR / "veloc_benchmark.exe"

    print("================================================================")
    print("      VeloC vs Standard C++ Comprehensive Benchmark Suite       ")
    print("================================================================")

    # 1. Compile Standard C++
    print("\n[1/4] Compiling Standard C++ (clang++ -O3 -static)...")
    cmd_cpp = [str(CLANG_PATH), str(cpp_src), "-o", str(cpp_exe), "-O3", "-static", "-static-libgcc", "-static-libstdc++"]
    t0 = time.perf_counter()
    res_cpp = subprocess.run(cmd_cpp, capture_output=True, text=True)
    cpp_compile_time = (time.perf_counter() - t0) * 1000.0

    if res_cpp.returncode != 0:
        print("[Error compiling standard C++]:", res_cpp.stderr)
        return

    print(f"      Standard C++ Compile Time: {cpp_compile_time:.1f} ms")

    # 2. Compile VeloC
    print("\n[2/4] Compiling VeloC (transpile + compile -O3)...")
    veloc_script = ROOT_DIR / "veloc.py"
    t0 = time.perf_counter()
    res_vc = subprocess.run([sys.executable, str(veloc_script), "build", str(vc_src), "-o", str(vc_exe)],
                            capture_output=True, text=True)
    vc_compile_time = (time.perf_counter() - t0) * 1000.0

    if res_vc.returncode != 0:
        print("[Error compiling VeloC]:", res_vc.stderr)
        return

    print(f"      VeloC Total Build Time:    {vc_compile_time:.1f} ms")

    # 3. Run Standard C++
    print("\n[3/4] Running Standard C++...")
    t0 = time.perf_counter()
    out_cpp = subprocess.run([str(cpp_exe)], capture_output=True, text=True)
    cpp_wall_time = (time.perf_counter() - t0) * 1000.0
    print(out_cpp.stdout.strip())

    # 4. Run VeloC
    print("\n[4/4] Running VeloC...")
    t0 = time.perf_counter()
    out_vc = subprocess.run([str(vc_exe)], capture_output=True, text=True)
    vc_wall_time = (time.perf_counter() - t0) * 1000.0
    print(out_vc.stdout.strip())

    def extract_sim_time(text):
        m = re.search(r"Simulation Time:\s*([0-9.]+)\s*ms", text)
        return float(m.group(1)) if m else None

    def extract_init_time(text):
        m = re.search(r"Init Time:\s*([0-9.]+)\s*ms", text)
        return float(m.group(1)) if m else None

    cpp_sim = extract_sim_time(out_cpp.stdout)
    vc_sim = extract_sim_time(out_vc.stdout)
    cpp_init = extract_init_time(out_cpp.stdout)
    vc_init = extract_init_time(out_vc.stdout)

    print("\n================================================================")
    print("                     BENCHMARK RESULTS SUMMARY                  ")
    print("================================================================")
    print(f"{'Metric':<30} | {'Standard C++':<15} | {'VeloC':<15} | {'Speedup':<10}")
    print("-" * 78)
    compile_speedup = cpp_compile_time / vc_compile_time
    print(f"{'Compilation Speed':<30} | {cpp_compile_time:<12.1f} ms | {vc_compile_time:<12.1f} ms | {compile_speedup:.2f}x faster")
    if cpp_init and vc_init:
        init_speedup = cpp_init / vc_init
        print(f"{'Init Time (5M particles)':<30} | {cpp_init:<12.1f} ms | {vc_init:<12.1f} ms | {init_speedup:.2f}x faster")
    if cpp_sim and vc_sim:
        sim_speedup = cpp_sim / vc_sim
        print(f"{'Simulation Time (20 steps)':<30} | {cpp_sim:<12.1f} ms | {vc_sim:<12.1f} ms | {sim_speedup:.2f}x faster")
    wall_speedup = cpp_wall_time / vc_wall_time
    print(f"{'Total Wall Execution Time':<30} | {cpp_wall_time:<12.1f} ms | {vc_wall_time:<12.1f} ms | {wall_speedup:.2f}x faster")
    print("================================================================")

if __name__ == "__main__":
    run_benchmark()
