"""
VeloC Crater: Ecosystem-wide Regression & Compatibility Gate
Tests that every registered package and flagship app compiles cleanly with current compiler.
"""

import sys
import subprocess
import time
from pathlib import Path

ROOT_DIR = Path("D:/VeloC")

def run_crater(root: Path = ROOT_DIR):
    print("=" * 80)
    print("                VeloC Crater: Ecosystem-Wide Build Verification                 ")
    print("=" * 80)

    targets = []
    # Discover apps
    apps_dir = root / "apps"
    if apps_dir.exists():
        for app in sorted(apps_dir.glob("*/src/main.vc")):
            targets.append(("App", app.parent.parent.name, app))

    # Discover packages
    pkgs_dir = root / "packages"
    if pkgs_dir.exists():
        for pkg in sorted(pkgs_dir.glob("*/src/main.vc")):
            targets.append(("Package", pkg.parent.parent.name, pkg))
        # Also include any standalone src files in packages if main.vc doesn't exist
        for pkg in sorted(pkgs_dir.glob("*/src/lib.vc")):
            targets.append(("Package", pkg.parent.parent.name, pkg))

    if not targets:
        print("[Warn] No apps or packages found for crater run.")
        return 0

    print(f"Discovered {len(targets)} targets across ecosystem:\n")
    print(f"{'TYPE':<10} | {'NAME':<24} | {'STATUS':<10} | {'DURATION':<10}")
    print("-" * 62)

    passed = 0
    failed = 0

    for kind, name, file_path in targets:
        t0 = time.time()
        cmd = [sys.executable, str(root / "veloc.py"), "build", str(file_path)]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        dur = (time.time() - t0) * 1000.0

        if res.returncode == 0:
            status = "PASS"
            passed += 1
            print(f"{kind:<10} | {name:<24} | \033[92m{status:<10}\033[0m | {dur:>7.1f} ms")
        else:
            status = "FAIL"
            failed += 1
            print(f"{kind:<10} | {name:<24} | \033[91m{status:<10}\033[0m | {dur:>7.1f} ms")
            print(f"    [Error Details]: {res.stdout.strip()[:200]}")

    print("-" * 62)
    print(f"Crater Summary: Total: {len(targets)} | Passed: {passed} | Failed: {failed}")
    if failed == 0:
        print("\033[92m[CRATER SUCCESS] 100% of ecosystem builds cleanly!\033[0m")
        return 0
    else:
        print("\033[91m[CRATER FAILURE] Regressions detected in ecosystem builds!\033[0m")
        return 1

if __name__ == "__main__":
    sys.exit(run_crater())
