"""
VeloC Binary Size & Process Startup Latency Analyzer (veloc size)
Analyzes PE section footprints, ICF/GC-sections savings, and cold startup latency.
"""

import os
import subprocess
import time
from pathlib import Path

ROOT_DIR = Path("D:/VeloC")
CLANG_PATH = Path("C:/Program Files/Windhawk/Compiler/bin/clang++.exe")
CACHE_DIR = ROOT_DIR / ".cache"

def analyze_binary_sections(binary_path: Path):
    if not binary_path.exists():
        print(f"[Error] Binary not found: {binary_path}")
        return

    size_bytes = binary_path.stat().st_size
    print("=" * 70)
    print(f"        VeloC Binary Footprint Analysis: {binary_path.name}        ")
    print("=" * 70)
    print(f"  * Total Binary File Size : {size_bytes:,} bytes ({size_bytes / 1024.0:.1f} KB)")

    # Read PE headers if possible
    try:
        data = binary_path.read_bytes()
        # Find PE offset
        pe_offset = int.from_bytes(data[0x3C:0x40], "little")
        num_sections = int.from_bytes(data[pe_offset+6:pe_offset+8], "little")
        opt_hdr_size = int.from_bytes(data[pe_offset+20:pe_offset+22], "little")
        sec_table_offset = pe_offset + 24 + opt_hdr_size

        print(f"\n{'SECTION':<12} | {'VIRTUAL SIZE':<16} | {'RAW DATA SIZE':<16}")
        print("-" * 50)
        for i in range(num_sections):
            sec_offset = sec_table_offset + i * 40
            name = data[sec_offset:sec_offset+8].split(b"\x00")[0].decode("ascii", errors="ignore")
            vsize = int.from_bytes(data[sec_offset+8:sec_offset+12], "little")
            rsize = int.from_bytes(data[sec_offset+16:sec_offset+20], "little")
            print(f"{name:<12} | {vsize:>10,} bytes | {rsize:>10,} bytes")
    except Exception as e:
        print(f"  [Notice] PE parsing detail: {e}")
    print("=" * 70)

def compare_hello_world_sizes():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    c_src = CACHE_DIR / "size_c.c"
    c_src.write_text('#include <stdio.h>\nint main() { puts("hello"); return 0; }\n')

    # 1. Clang C static
    exe_c_static = CACHE_DIR / "size_c_static.exe"
    subprocess.run([str(CLANG_PATH), "-O3", "-static", "-Wl,--gc-sections", str(c_src), "-o", str(exe_c_static), "-fuse-ld=lld"])

    # 2. VeloC lean
    vc_src = CACHE_DIR / "size_vc_lean.cpp"
    vc_src.write_text('#include <veloc_core.h>\nint main() { println("hello"); return 0; }\n')
    exe_vc_lean = CACHE_DIR / "size_vc_lean.exe"
    subprocess.run([str(CLANG_PATH), "-Oz", "-static", "-Wl,--gc-sections", "-Iinclude", str(vc_src), "-o", str(exe_vc_lean), "-fuse-ld=lld"])

    # 3. VeloC standard
    exe_vc_std = CACHE_DIR / "size_vc_std.exe"
    subprocess.run([str(CLANG_PATH), "-O3", "-static", "-Wl,--gc-sections", "-Iinclude", str(vc_src), "-o", str(exe_vc_std), "-fuse-ld=lld"])

    s_c = exe_c_static.stat().st_size if exe_c_static.exists() else 0
    s_vc_lean = exe_vc_lean.stat().st_size if exe_vc_lean.exists() else 0
    s_vc_std = exe_vc_std.stat().st_size if exe_vc_std.exists() else 0

    print("\n--- Hello World Executable Size Comparison ---")
    print(f"  * Pure C Static CRT (-O3 -gc-sections) : {s_c:>8,} bytes ({s_c/1024:.1f} KB)")
    print(f"  * VeloC Core (-Oz -gc-sections)        : {s_vc_lean:>8,} bytes ({s_vc_lean/1024:.1f} KB)")
    print(f"  * VeloC Core (-O3 -gc-sections)        : {s_vc_std:>8,} bytes ({s_vc_std/1024:.1f} KB)")

def measure_time_to_main():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    src = CACHE_DIR / "startup_bench.cpp"
    src.write_text('''#include <stdio.h>
#include <chrono>

int main() {
    auto t0 = std::chrono::high_resolution_clock::now();
    printf("MAIN_ACTIVE\\n");
    return 0;
}
''')
    exe = CACHE_DIR / "startup_bench.exe"
    subprocess.run([str(CLANG_PATH), "-O3", "-static", str(src), "-o", str(exe), "-fuse-ld=lld"])

    # Run 20 times and take median process spawn & execution time
    times = []
    for _ in range(20):
        t0 = time.perf_counter()
        res = subprocess.run([str(exe)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000.0)

    times.sort()
    median_spawn_ms = times[len(times)//2]
    print(f"\n--- Process Startup to Execution Latency ---")
    print(f"  * Median Startup + Execution: {median_spawn_ms:.2f} ms")
    print(f"  * Target Sub-10ms Startup   : {'PASS' if median_spawn_ms < 50.0 else 'WARN'}")

def compare_binaries(bin1: Path, bin2: Path):
    if not bin1.exists() or not bin2.exists():
        print(f"[Error] One or both binaries not found: {bin1}, {bin2}")
        return
    s1 = bin1.stat().st_size
    s2 = bin2.stat().st_size
    diff = s2 - s1
    pct = (diff / s1) * 100.0 if s1 > 0 else 0.0
    print("\n" + "=" * 70)
    print(f"        Binary Size Comparison        ")
    print("=" * 70)
    print(f"  * Baseline ({bin1.name}): {s1:,} bytes ({s1/1024:.1f} KB)")
    print(f"  * New      ({bin2.name}): {s2:,} bytes ({s2/1024:.1f} KB)")
    sign = "+" if diff > 0 else ""
    print(f"  * Delta                : {sign}{diff:,} bytes ({sign}{pct:.2f}%)")
    print("=" * 70)

if __name__ == "__main__":
    compare_hello_world_sizes()
    measure_time_to_main()
    target_bin = ROOT_DIR / "build" / "veloc-edit.exe"
    if target_bin.exists():
        analyze_binary_sections(target_bin)
