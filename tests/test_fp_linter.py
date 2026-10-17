"""
VeloC Floating-Point Linter Test Suite
Verifies detection of:
- FP-001: exact float equality comparison (x == y)
- FP-002: NaN/Inf checks under fast-math mode
- FP-003: Unchecked division by float
"""

import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "src"))

from fp_policy import FloatingPointLinter

def test_linter():
    code = """
fn bad_fp_code(x: f32, y: f32) -> f32 {
    if (x == 1.234f) {
        return 0.0f;
    }
    let z = x / y;
    return z;
}

#[fp(fast)]
fn bad_fast_code(x: f32) -> bool {
    if (isnan(x)) {
        return true;
    }
    return false;
}
"""
    linter = FloatingPointLinter(code, "test_linter.vc")
    findings = linter.lint()

    rules_found = [f["rule"] for f in findings]
    print(f"Linter findings ({len(findings)}): {rules_found}")

    assert "FP-001" in rules_found, "FP-001 (float comparison) must be detected"
    assert "FP-002" in rules_found, "FP-002 (isnan in fast scope) must be detected"
    assert "FP-003" in rules_found, "FP-003 (unchecked division) must be detected"

    print("[PASS] All floating-point linter rules triggered as expected.")
    return True

if __name__ == "__main__":
    success = test_linter()
    sys.exit(0 if success else 1)
