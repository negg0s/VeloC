"""
VeloC NaN & Infinity Propagation Conformance Test Suite
Verifies that all standard mathematical functions strictly adhere to IEEE-754:
1. NaN input produces NaN output (never silently swallowed).
2. Domain errors produce NaN (e.g. log(-1.0), sqrt(-2.0)).
3. Overflow produces +-Infinity (never NaN or wraparound).
4. Underflow produces gradual denormals or +-0.0 (preserving sign).
"""

import sys
import subprocess
import time
from pathlib import Path

ROOT_DIR = Path("D:/VeloC")
CACHE_DIR = ROOT_DIR / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def test_nan_propagation():
    test_src = CACHE_DIR / "test_nan_prop.cpp"
    test_src.write_text('''
#include <stdio.h>
#include <math.h>
#include <assert.h>
#include "D:/VeloC/include/veloc_numerics.h"

int main() {
    float nan_val = NAN;
    float inf_val = INFINITY;
    float neg_inf = -INFINITY;

    // 1. NaN propagation
    assert(isnan(veloc_exp_strict(nan_val)));
    assert(isnan(veloc_exp_fast(nan_val)));
    assert(isnan(veloc_log_strict(nan_val)));
    assert(isnan(veloc_log_fast(nan_val)));
    assert(isnan(veloc_tanh_strict(nan_val)));
    assert(isnan(veloc_tanh_fast(nan_val)));
    assert(isnan(veloc_erf_strict(nan_val)));
    assert(isnan(veloc_sqrt_strict(nan_val)));
    assert(isnan(veloc_sqrt_fast(nan_val)));
    assert(isnan(veloc_gelu_strict(nan_val)));
    assert(isnan(veloc_gelu_fast(nan_val)));

    // 2. Domain violations produce NaN
    assert(isnan(veloc_log_strict(-1.0f)));
    assert(isnan(veloc_log_fast(-1.0f)));
    assert(isnan(veloc_sqrt_strict(-2.0f)));
    assert(isnan(veloc_sqrt_fast(-2.0f)));

    // 3. Overflow and Infinity boundaries
    assert(isinf(veloc_exp_strict(100.0f)) && veloc_exp_strict(100.0f) > 0);
    assert(isinf(veloc_exp_fast(100.0f)) && veloc_exp_fast(100.0f) > 0);
    // At -100.0f in strict IEEE-754, value is a valid subnormal (~3.72e-44)
    assert(veloc_exp_strict(-100.0f) > 0.0f && veloc_exp_strict(-100.0f) < 1e-40f);
    assert(veloc_exp_strict(-110.0f) == 0.0f); // Complete underflow to zero
    assert(veloc_exp_fast(-100.0f) == 0.0f);

    // 4. Logarithm boundaries
    assert(veloc_log_strict(0.0f) == -INFINITY);
    assert(veloc_log_fast(0.0f) == -INFINITY);
    assert(veloc_log_strict(1.0f) == 0.0f);

    // 5. Softmax on vector with extreme values
    float logits[4] = {1000.0f, 1000.0f, 1000.0f, 1000.0f};
    float probs[4] = {0};
    veloc_softmax_strict(logits, probs, 4);
    for (int i = 0; i < 4; ++i) {
        assert(!isnan(probs[i]));
        assert(fabs(probs[i] - 0.25f) < 1e-6f);
    }

    printf("ALL_NAN_TESTS_PASSED\\n");
    return 0;
}
''', encoding="utf-8")

    test_exe = CACHE_DIR / "test_nan_prop.exe"
    clang_cmd = [
        "C:/Program Files/Windhawk/Compiler/bin/clang++.exe",
        "-std=c++20",
        "-O3",
        "-fno-fast-math",
        "-frounding-math",
        str(test_src),
        "-o", str(test_exe)
    ]
    res_compile = subprocess.run(clang_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res_compile.returncode != 0:
        print(f"[FAIL] Compilation failed:\n{res_compile.stderr}")
        return False

    res_run = subprocess.run([str(test_exe)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res_run.returncode == 0 and "ALL_NAN_TESTS_PASSED" in res_run.stdout:
        print("[PASS] IEEE-754 NaN and Infinity propagation verified successfully.")
        return True
    else:
        print(f"[FAIL] Execution failed:\n{res_run.stderr}\n{res_run.stdout}")
        return False

if __name__ == "__main__":
    success = test_nan_propagation()
    sys.exit(0 if success else 1)
