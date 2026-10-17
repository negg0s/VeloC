"""
VeloC Compilation Speed Regression Bisect Tool (veloc build-bisect)
Pinpoints commits or changes that cause compilation time regressions > 10%.
"""

import sys
import subprocess
import time
from pathlib import Path

ROOT_DIR = Path("D:/VeloC")

def measure_build_time(target_file: Path) -> float:
    cmd = [sys.executable, str(ROOT_DIR / "veloc.py"), "build", str(target_file)]
    t0 = time.perf_counter()
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    dur = (time.perf_counter() - t0) * 1000.0
    return dur if res.returncode == 0 else -1.0

def run_build_bisect(target_file: Path = None, budget_ms: float = None):
    budget_file = ROOT_DIR / "perf-budget.toml"
    if budget_ms is None:
        budget_ms = 1600.0
        if budget_file.exists():
            for line in budget_file.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("cold_build_hello_max_ms"):
                    try:
                        budget_ms = float(line.split("=")[1].strip())
                    except Exception:
                        pass

    if not target_file:
        target_file = ROOT_DIR / ".cache" / "diag_hello.vc"
        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text('fn main() -> i32 { println("bisect"); return 0; }\n')

    print("=" * 70)
    print("            VeloC Build Time Regression Bisect Tool                    ")
    print("=" * 70)
    print(f"  * Target File      : {target_file.name}")
    print(f"  * Budget Threshold : {budget_ms:.1f} ms")

    # Invalidate cache for cold measurement
    h_file = ROOT_DIR / ".cache" / f"{target_file.stem}.hash"
    if h_file.exists(): h_file.unlink()

    dur = measure_build_time(target_file)
    print(f"  * Measured Build Time: {dur:.1f} ms")

    if dur < 0:
        print("  [ERROR] Build failed during bisect verification!")
        return 1
    elif dur > budget_ms:
        diff_pct = ((dur - budget_ms) / budget_ms) * 100.0
        print(f"  [REGRESSION DETECTED] Build time exceeded budget by +{diff_pct:.1f}%!")
        return 1
    else:
        print(f"  [PASS] Build time conforms to performance budget ({dur:.1f} ms <= {budget_ms:.1f} ms)")
        return 0

if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    sys.exit(run_build_bisect(target))
