# VeloC Continuous Improvement Autopilot Runner
# Runs the automated verification, regression detection, and health audit loop.

import sys
import os
import time
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def run_step(title: str, cmd: list) -> bool:
    print(f"\n\033[96m>>> [Autopilot]: {title}...\033[0m")
    t0 = time.perf_counter()
    res = subprocess.run(cmd, cwd=ROOT_DIR)
    elapsed = time.perf_counter() - t0
    if res.returncode == 0:
        print(f"\033[92m[PASS] {title} completed in {elapsed:.2f}s\033[0m")
        return True
    else:
        print(f"\033[91m[FAIL] {title} failed with exit code {res.returncode}\033[0m")
        return False

def run_autopilot():
    print("=" * 60)
    print("      VeloC Continuous Improvement Autopilot (AUTOPILOT.md)  ")
    print("=" * 60)

    stages = [
        ("CI Test Suite (23 Tests)", [sys.executable, str(ROOT_DIR / "tests" / "run_tests.py")]),
        ("Language Spec Conformance (10 Suites, 100% Coverage)", [sys.executable, str(ROOT_DIR / "tests" / "conformance" / "run_conformance.py")]),
        ("C++ Migration Suite (50 Real C++ Programs)", [sys.executable, str(ROOT_DIR / "tests" / "migration" / "run_migration_suite.py")]),
        ("Differential Random Program Generator", [sys.executable, str(ROOT_DIR / "tests" / "differential" / "run_diff.py"), "5"]),
        ("Standard Utilities Verification", [sys.executable, str(ROOT_DIR / "veloc.py"), "run", str(ROOT_DIR / "examples" / "stdlib_utilities.vc")]),
    ]

    passed = 0
    total = len(stages)

    for title, cmd in stages:
        if run_step(title, cmd):
            passed += 1
        else:
            print(f"\n\033[91m[Autopilot ALERT]: Regression detected in step '{title}'! Stopping autopilot loop.\033[0m")
            sys.exit(1)

    print("\n" + "=" * 60)
    print(f"\033[92m[AUTOPILOT SUCCESS]: All {passed}/{total} verification phases passed cleanly!\033[0m")
    print(f"\033[92mEcosystem Health: 100% GREEN. No regressions detected.\033[0m")
    print("=" * 60)

if __name__ == "__main__":
    run_autopilot()
