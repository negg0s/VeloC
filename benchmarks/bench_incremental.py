import os
import sys
import time
import subprocess
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

CAS_BENCH_DIR = ROOT_DIR / "projects" / "bench_incremental"

def generate_multi_module_project(num_modules: int = 10, funcs_per_mod: int = 5) -> Path:
    proj_dir = CAS_BENCH_DIR / f"project_{num_modules}_mods"
    if proj_dir.exists():
        shutil.rmtree(proj_dir)
    src_dir = proj_dir / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    module_names = []
    for m in range(num_modules):
        mod_name = f"module_{m}"
        module_names.append(mod_name)
        mod_file = src_dir / f"{mod_name}.vc"
        lines = [
            f"// Synthetic Module {mod_name}",
            "#include <veloc.h>",
            "#include <cstdint>",
        ]
        for f in range(funcs_per_mod):
            lines.append(f"i64 compute_{m}_{f}(i64 x) {{")
            lines.append(f"    i64 r = (x * 31 + {m * 10 + f}) ^ 0x5bf03635;")
            lines.append(f"    return r;")
            lines.append("}")
        mod_file.write_text("\n".join(lines), encoding="utf-8")

    # Generate main entrypoint
    main_file = src_dir / "main.vc"
    main_lines = [
        "// Synthetic Project Main",
        "#include <veloc.h>",
        "#include <cstdio>",
    ]
    for m in module_names:
        main_lines.append(f'#include "{m}.vc"')
    main_lines.append("i32 main() {")
    main_lines.append("    i64 total = 0;")
    for m in range(num_modules):
        main_lines.append(f"    total += compute_{m}_0(100);")
    main_lines.append('    printf("TOTAL=%lld\\n", (long long)total);')
    main_lines.append("    return 0;")
    main_lines.append("}")
    main_file.write_text("\n".join(main_lines), encoding="utf-8")

    return main_file

def run_incremental_benchmark():
    print("==================================================")
    print("      VeloC Query & Incremental Build Benchmark   ")
    print("==================================================")

    for num_mods in [10, 50]:
        print(f"\n--- Testing Synthetic Project with {num_mods} modules ({num_mods * 5 + 1} functions) ---")
        main_file = generate_multi_module_project(num_mods, funcs_per_mod=5)

        # 1. Cold Build
        subprocess.run([sys.executable, str(ROOT_DIR / "veloc.py"), "clean"], capture_output=True)
        t0 = time.perf_counter()
        res_cold = subprocess.run([sys.executable, str(ROOT_DIR / "veloc.py"), "build", str(main_file)],
                                  capture_output=True, text=True)
        t_cold = (time.perf_counter() - t0) * 1000.0
        assert res_cold.returncode == 0, f"Cold build failed: {res_cold.stdout} {res_cold.stderr}"
        print(f"  [COLD BUILD] Time: {t_cold:.1f} ms")

        # 2. Warm Build (0 changes)
        t0 = time.perf_counter()
        res_warm = subprocess.run([sys.executable, str(ROOT_DIR / "veloc.py"), "build", str(main_file)],
                                  capture_output=True, text=True)
        t_warm = (time.perf_counter() - t0) * 1000.0
        assert res_warm.returncode == 0
        print(f"  [WARM BUILD] Time: {t_warm:.1f} ms (Instant Cache Hit: < 50 ms target)")

        # 3. 1-Line Edit in module_0
        mod0 = main_file.parent / "module_0.vc"
        content = mod0.read_text(encoding="utf-8")
        edited = content.replace("x * 31", "x * 37") # 1-line edit
        mod0.write_text(edited, encoding="utf-8")

        t0 = time.perf_counter()
        res_edit = subprocess.run([sys.executable, str(ROOT_DIR / "veloc.py"), "build", str(main_file)],
                                  capture_output=True, text=True)
        t_edit = (time.perf_counter() - t0) * 1000.0
        assert res_edit.returncode == 0
        print(f"  [1-LINE EDIT] Time: {t_edit:.1f} ms (Transpilation & Incremental Rebuild)")

    print("\n==================================================")
    print("Incremental Benchmark Completed Successfully!")
    print("==================================================")

if __name__ == "__main__":
    run_incremental_benchmark()
