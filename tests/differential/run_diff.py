import os
import sys
import subprocess
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
from tests.differential.generator import VeloCProgramGenerator

DIFF_DIR = ROOT_DIR / ".cache" / "differential"
DIFF_DIR.mkdir(parents=True, exist_ok=True)

CLANG_PATH = Path("C:/Program Files/Windhawk/Compiler/bin/clang++.exe")
INCLUDE_DIR = ROOT_DIR / "include"

def run_differential_suite(count: int = 25):
    print("==================================================")
    print(f"       VeloC Differential Testing Engine         ")
    print("==================================================")
    print(f"Target: Running {count} randomized differential programs...")
    print(f"Comparing VeloC AST (-O3 -march=native) vs Reference C++ (-O0)...")

    passed = 0
    failed = 0

    for i in range(1, count + 1):
        gen = VeloCProgramGenerator(seed=1000 + i)
        vc_code = gen.gen_program()
        vc_file = DIFF_DIR / f"diff_test_{i}.vc"
        vc_file.write_text(vc_code, encoding="utf-8")

        # 1. Compile & run via VeloC compiler (-O3 -march=native)
        build_res = subprocess.run([sys.executable, str(ROOT_DIR / "veloc.py"), "build", str(vc_file)],
                                   capture_output=True, text=True)
        if build_res.returncode != 0:
            print(f"  [FAIL] Test #{i}: VeloC build failed!\n{build_res.stderr}")
            failed += 1
            continue

        exe_file = ROOT_DIR / "build" / f"diff_test_{i}.exe"
        run_veloc = subprocess.run([str(exe_file)], capture_output=True, text=True)
        veloc_output = run_veloc.stdout.strip()

        # 2. Compile generated C++ source directly at -O0 as reference baseline
        cpp_source = ROOT_DIR / ".cache" / f"diff_test_{i}.cpp"
        ref_exe = DIFF_DIR / f"diff_test_{i}_ref.exe"
        ref_cmd = [
            str(CLANG_PATH),
            str(cpp_source),
            "-o", str(ref_exe),
            "-O0",
            "-static",
            f"-I{INCLUDE_DIR}",
            "-lws2_32"
        ]
        ref_build = subprocess.run(ref_cmd, capture_output=True, text=True)
        if ref_build.returncode != 0:
            print(f"  [FAIL] Test #{i}: Reference C++ -O0 build failed!\n{ref_build.stderr}")
            failed += 1
            continue

        run_ref = subprocess.run([str(ref_exe)], capture_output=True, text=True)
        ref_output = run_ref.stdout.strip()

        # 3. Compare checksums
        if veloc_output == ref_output and "CHECKSUM=" in veloc_output:
            passed += 1
            if i % 5 == 0 or i == count:
                print(f"  [PASS] Test #{i:<2} Verified match: {veloc_output}")
        else:
            print(f"  [FAIL] Test #{i}: Checksum MISMATCH!\n         VeloC: {veloc_output}\n         Ref:   {ref_output}")
            failed += 1

    print("==================================================")
    print(f"Differential Testing Results: {passed} passed, {failed} failed")
    print("==================================================")
    return failed == 0

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    success = run_differential_suite(count)
    sys.exit(0 if success else 1)
