"""
Diagnostic benchmark script: Profiles compilation stages of VeloC and pure Clang++
"""

import time
import subprocess
import json
from pathlib import Path

CLANG = Path("C:/Program Files/Windhawk/Compiler/bin/clang++.exe")
ROOT = Path("D:/VeloC")
CACHE = ROOT / ".cache"
CACHE.mkdir(exist_ok=True)

def measure_cmd(cmd):
    t0 = time.perf_counter()
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    t1 = time.perf_counter()
    return (t1 - t0) * 1000.0, res.returncode, res.stdout, res.stderr

def run_diagnostics():
    print("=" * 80)
    print("           VeloC & Clang++ Baseline Cold Build Diagnostics                      ")
    print("=" * 80)

    # 1. Empty C++
    f_empty = CACHE / "diag_empty.cpp"
    f_empty.write_text("int main() { return 0; }\n")
    t_empty, rc, out, err = measure_cmd([str(CLANG), "-O3", str(f_empty), "-o", str(CACHE / "diag_empty.exe")])

    # 2. stdio only C++
    f_stdio = CACHE / "diag_stdio.cpp"
    f_stdio.write_text('#include <stdio.h>\nint main() { printf("hi\\n"); return 0; }\n')
    t_stdio, rc, out, err = measure_cmd([str(CLANG), "-O3", str(f_stdio), "-o", str(CACHE / "diag_stdio.exe")])

    # 3. iostream + vector + string (Standard C++)
    f_std = CACHE / "diag_std.cpp"
    f_std.write_text('#include <iostream>\n#include <vector>\n#include <string>\nint main() { std::cout << "hi" << std::endl; return 0; }\n')
    t_std, rc, out, err = measure_cmd([str(CLANG), "-O3", "-std=c++20", str(f_std), "-o", str(CACHE / "diag_std.exe")])

    # 4. Pure C++ with full include/veloc.h
    f_veloc = CACHE / "diag_veloc.cpp"
    f_veloc.write_text('#include "include/veloc.h"\nint main() { veloc::println("hi"); return 0; }\n')
    t_veloc, rc, out, err = measure_cmd([str(CLANG), "-O3", "-std=c++20", f"-I{ROOT}", str(f_veloc), "-o", str(CACHE / "diag_veloc.exe")])

    # 5. Full veloc.py cold compile on minimal hello.vc
    f_vc = CACHE / "diag_hello.vc"
    f_vc.write_text('#include <veloc.h>\nfn main() -> i32 { println("hi"); return 0; }\n')
    # ensure no cache
    h_target = CACHE / "diag_hello.hash"
    if h_target.exists(): h_target.unlink()
    e_target = ROOT / "build" / "diag_hello.exe"
    if e_target.exists(): e_target.unlink()

    t_py, rc, out, err = measure_cmd(["python", str(ROOT / "veloc.py"), "build", str(f_vc)])

    print(f"1. Empty C++ main()                    : {t_empty:7.1f} ms")
    print(f"2. C++ <stdio.h> only                   : {t_stdio:7.1f} ms")
    print(f"3. C++ standard (<iostream>, <vector>)  : {t_std:7.1f} ms")
    print(f"4. C++ with full veloc.h (3716 lines)   : {t_veloc:7.1f} ms")
    print(f"5. VeloC cold build (Python + Clang)    : {t_py:7.1f} ms")
    print("=" * 80)

    # Let's run clang with -ftime-trace on veloc.h
    trace_file = CACHE / "diag_veloc.json"
    if trace_file.exists(): trace_file.unlink()
    cmd_trace = [str(CLANG), "-O3", "-std=c++20", f"-I{ROOT}", "-ftime-trace", str(f_veloc), "-o", str(CACHE / "diag_veloc_trace.exe")]
    t_tr, rc, out, err = measure_cmd(cmd_trace)
    print(f"Clang -ftime-trace executed in {t_tr:.1f} ms")

    if trace_file.exists():
        data = json.loads(trace_file.read_text(encoding="utf-8"))
        events = data.get("traceEvents", [])
        # Find top duration events
        events_with_dur = [e for e in events if "dur" in e and "name" in e]
        events_with_dur.sort(key=lambda x: x["dur"], reverse=True)
        print("\n[Clang Top-10 Time Sinks from -ftime-trace]:")
        for e in events_with_dur[:15]:
            dur_ms = e["dur"] / 1000.0
            name = e["name"]
            arg = e.get("args", {}).get("detail", "")
            print(f"  - {dur_ms:6.1f} ms : {name:<20} {arg[:50]}")

if __name__ == "__main__":
    run_diagnostics()
