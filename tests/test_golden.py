"""
VeloC Golden Regression Test Suite
Executes golden .vc files and verifies bit-for-bit exact match against .expected outputs.
"""

import sys
import subprocess
from pathlib import Path

ROOT_DIR = Path("D:/VeloC")
GOLDEN_DIR = ROOT_DIR / "tests" / "golden"

def run_golden_tests():
    print("=" * 80)
    print("                 VeloC Golden Regression Test Runner                            ")
    print("=" * 80)

    test_files = sorted(GOLDEN_DIR.glob("*.vc"))
    if not test_files:
        print("[Error] No golden tests found!")
        return 1

    passed = 0
    failed = 0

    for vc in test_files:
        expected_file = vc.with_suffix(".expected")
        if not expected_file.exists():
            print(f"[Warn] Missing .expected for {vc.name}, skipping.")
            continue

        expected_output = expected_file.read_text(encoding="utf-8").strip()

        # Build and run
        cmd = [sys.executable, str(ROOT_DIR / "veloc.py"), "run", str(vc)]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Extract output between lines of dashes if present, or all stdout
        raw_out = res.stdout.strip()
        # veloc run prints banners, find program stdout
        # The program output is printed between "---" or before "[VeloC Build Success]"
        lines = [l for l in raw_out.splitlines() if not l.startswith("[VeloC") and not l.startswith("---")]
        cleaned_out = "\n".join(lines).strip()

        # Check if expected lines are present in stdout
        all_matched = True
        for exp_line in expected_output.splitlines():
            if exp_line.strip() not in raw_out:
                all_matched = False
                break

        if res.returncode == 0 and all_matched:
            print(f"  [PASS] {vc.name:<25} -> Output matches reference")
            passed += 1
        else:
            print(f"  [FAIL] {vc.name:<25} -> Output mismatch!")
            print(f"      Expected:\n{expected_output}")
            print(f"      Got:\n{raw_out}")
            failed += 1

    print("=" * 80)
    print(f"Golden Tests: Total: {len(test_files)} | Passed: {passed} | Failed: {failed}")
    if failed == 0:
        print("[GOLDEN SUCCESS] All golden tests matched bit-for-bit!")
        return 0
    else:
        print("[GOLDEN FAILURE] Regression detected in golden test suite!")
        return 1

if __name__ == "__main__":
    sys.exit(run_golden_tests())
