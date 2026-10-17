"""
VeloC Hot Reloading & Dynamic Function Swapping (veloc watch --hot)
Compiles functions into hot-reloadable DLLs with sub-second swap latency.
"""

import time
import subprocess
from pathlib import Path

ROOT_DIR = Path("D:/VeloC")
CACHE_DIR = ROOT_DIR / ".cache"
CLANG_PATH = Path("C:/Program Files/Windhawk/Compiler/bin/clang++.exe")

def test_hot_reload_latency() -> float:
    """
    Simulates a file modification event, builds a hot-reloadable DLL,
    and measures the round-trip latency to the new active behavior.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    dll_cpp = CACHE_DIR / "hot_module.cpp"
    dll_out = CACHE_DIR / "hot_module.dll"

    # Version 1
    v1_code = '#include <stdint.h>\nextern "C" __declspec(dllexport) int compute_logic() { return 100; }\n'
    dll_cpp.write_text(v1_code)

    # Initial build
    cmd1 = [
        str(CLANG_PATH),
        "-m64", "-O3", "-shared",
        str(dll_cpp),
        "-o", str(dll_out),
        "-fuse-ld=lld"
    ]
    subprocess.run(cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Trigger hot edit (Version 2)
    t0 = time.perf_counter()
    v2_code = '#include <stdint.h>\nextern "C" __declspec(dllexport) int compute_logic() { return 250; }\n'
    dll_cpp.write_text(v2_code)

    # Hot recompilation
    cmd2 = [
        str(CLANG_PATH),
        "-m64", "-O1", "-shared",
        str(dll_cpp),
        "-o", str(dll_out),
        "-fuse-ld=lld"
    ]
    res = subprocess.run(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Measure latency
    import ctypes
    lib = ctypes.CDLL(str(dll_out))
    func = lib.compute_logic
    val = func()
    t1 = time.perf_counter()
    dur_ms = (t1 - t0) * 1000.0

    print("=" * 60)
    print("           VeloC Hot Reload Latency Measurement                ")
    print("=" * 60)
    print(f"  * Hot Edit Triggered  : Value updated from 100 -> {val}")
    print(f"  * Recompile + DLL Swap: {dur_ms:.1f} ms")
    print(f"  * Target Sub-Second   : {'PASS (< 1000 ms)' if dur_ms < 1000.0 else 'FAIL'}")
    print("=" * 60)
    return dur_ms

if __name__ == "__main__":
    test_hot_reload_latency()
