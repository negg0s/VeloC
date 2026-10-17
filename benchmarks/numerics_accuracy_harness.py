"""
VeloC Comprehensive Numerics & Mathematical Accuracy Harness
Evaluates precision contracts (Max ULP, Mean ULP, Error Distribution, Latency ns/elem)
across standard functions against high-precision (double/quad) references.
Outputs results to benchmarks/results/numerics_accuracy.json and docs/perf/accuracy_contracts.md.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

ROOT_DIR = Path("D:/VeloC")
CACHE_DIR = ROOT_DIR / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR = ROOT_DIR / "benchmarks" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

HARNESS_CPP = CACHE_DIR / "harness_math.cpp"
HARNESS_EXE = CACHE_DIR / "harness_math.exe"

CPP_SOURCE = """
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <string.h>
#include <chrono>
#include <vector>
#include <random>
#include "D:/VeloC/include/veloc_numerics.h"

struct AccuracyMetric {
    const char* name;
    const char* variant;
    double max_ulp;
    double mean_ulp;
    double ns_per_elem;
    uint32_t samples;
    uint32_t ulp_0_count;
    uint32_t ulp_1_count;
    uint32_t ulp_2_count;
    uint32_t ulp_gt2_count;
};

// Generates uniform and tricky edge-case floats
std::vector<float> generate_test_inputs(float min_val, float max_val, size_t count) {
    std::vector<float> vals;
    vals.reserve(count + 100);

    // 1. Uniform random
    std::mt19937 rng(42);
    std::uniform_real_distribution<float> dist(min_val, max_val);
    for (size_t i = 0; i < count; ++i) {
        vals.push_back(dist(rng));
    }

    // 2. Tricky edge cases: +-0.0, subnormals, small epsilons, boundaries
    vals.push_back(0.0f);
    vals.push_back(-0.0f);
    vals.push_back(1.0f);
    vals.push_back(-1.0f);
    vals.push_back(1e-7f);
    vals.push_back(-1e-7f);
    vals.push_back(1e-37f); // Subnormal threshold
    vals.push_back(min_val);
    vals.push_back(max_val);
    vals.push_back(min_val * 0.99f);
    vals.push_back(max_val * 0.99f);

    return vals;
}

template <typename Func, typename RefFunc>
AccuracyMetric benchmark_kernel(const char* name, const char* variant, Func fn, RefFunc ref_fn, const std::vector<float>& inputs) {
    AccuracyMetric m;
    m.name = name;
    m.variant = variant;
    m.max_ulp = 0.0;
    m.mean_ulp = 0.0;
    m.samples = inputs.size();
    m.ulp_0_count = 0;
    m.ulp_1_count = 0;
    m.ulp_2_count = 0;
    m.ulp_gt2_count = 0;

    double total_ulp = 0.0;

    // Accuracy pass
    for (float x : inputs) {
        float actual = fn(x);
        double expected_d = ref_fn((double)x);
        float expected = (float)expected_d;

        if (isnan(actual) && isnan(expected)) continue;
        if (isinf(actual) && isinf(expected) && ((actual > 0) == (expected > 0))) continue;

        uint32_t ulp = veloc_ulp_distance_f32(actual, expected);
        if (ulp > m.max_ulp) m.max_ulp = (double)ulp;
        total_ulp += ulp;

        if (ulp == 0) m.ulp_0_count++;
        else if (ulp == 1) m.ulp_1_count++;
        else if (ulp == 2) m.ulp_2_count++;
        else m.ulp_gt2_count++;
    }
    m.mean_ulp = total_ulp / inputs.size();

    // Latency benchmark pass (run 10 iterations)
    volatile float dummy = 0.0f;
    auto t0 = std::chrono::high_resolution_clock::now();
    for (int rep = 0; rep < 10; ++rep) {
        for (float x : inputs) {
            dummy += fn(x);
        }
    }
    auto t1 = std::chrono::high_resolution_clock::now();
    double total_ns = std::chrono::duration<double, std::nano>(t1 - t0).count();
    m.ns_per_elem = total_ns / (10.0 * inputs.size());

    return m;
}

int main() {
    printf("{\\n  \\"metrics\\": [\\n");

    std::vector<AccuracyMetric> all_metrics;

    // exp
    auto exp_inputs = generate_test_inputs(-80.0f, 85.0f, 50000);
    all_metrics.push_back(benchmark_kernel("exp", "strict", veloc_exp_strict, [](double x){ return exp(x); }, exp_inputs));
    all_metrics.push_back(benchmark_kernel("exp", "fast", veloc_exp_fast, [](double x){ return exp(x); }, exp_inputs));

    // log
    auto log_inputs = generate_test_inputs(1e-6f, 1e20f, 50000);
    all_metrics.push_back(benchmark_kernel("log", "strict", veloc_log_strict, [](double x){ return log(x); }, log_inputs));
    all_metrics.push_back(benchmark_kernel("log", "fast", veloc_log_fast, [](double x){ return log(x); }, log_inputs));

    // tanh
    auto tanh_inputs = generate_test_inputs(-8.0f, 8.0f, 50000);
    all_metrics.push_back(benchmark_kernel("tanh", "strict", veloc_tanh_strict, [](double x){ return tanh(x); }, tanh_inputs));
    all_metrics.push_back(benchmark_kernel("tanh", "fast", veloc_tanh_fast, [](double x){ return tanh(x); }, tanh_inputs));

    // erf
    auto erf_inputs = generate_test_inputs(-3.5f, 3.5f, 50000);
    all_metrics.push_back(benchmark_kernel("erf", "strict", veloc_erf_strict, [](double x){ return erf(x); }, erf_inputs));

    // sqrt
    auto sqrt_inputs = generate_test_inputs(1e-6f, 1e20f, 50000);
    all_metrics.push_back(benchmark_kernel("sqrt", "strict", veloc_sqrt_strict, [](double x){ return sqrt(x); }, sqrt_inputs));
    all_metrics.push_back(benchmark_kernel("sqrt", "fast", veloc_sqrt_fast, [](double x){ return sqrt(x); }, sqrt_inputs));

    // GeLU
    auto gelu_inputs = generate_test_inputs(-6.0f, 6.0f, 50000);
    auto ref_gelu = [](double x) { return 0.5 * x * (1.0 + erf(x / 1.4142135623730951)); };
    all_metrics.push_back(benchmark_kernel("GeLU", "strict", veloc_gelu_strict, ref_gelu, gelu_inputs));
    all_metrics.push_back(benchmark_kernel("GeLU", "fast", veloc_gelu_fast, ref_gelu, gelu_inputs));

    // Sigmoid
    auto sig_inputs = generate_test_inputs(-12.0f, 12.0f, 50000);
    auto ref_sig = [](double x) { return 1.0 / (1.0 + exp(-x)); };
    all_metrics.push_back(benchmark_kernel("Sigmoid", "strict", veloc_sigmoid_strict, ref_sig, sig_inputs));
    all_metrics.push_back(benchmark_kernel("Sigmoid", "fast", veloc_sigmoid_fast, ref_sig, sig_inputs));

    for (size_t i = 0; i < all_metrics.size(); ++i) {
        const auto& m = all_metrics[i];
        printf("    {\\n");
        printf("      \\"name\\": \\"%s\\",\\n", m.name);
        printf("      \\"variant\\": \\"%s\\",\\n", m.variant);
        printf("      \\"max_ulp\\": %.2f,\\n", m.max_ulp);
        printf("      \\"mean_ulp\\": %.4f,\\n", m.mean_ulp);
        printf("      \\"ns_per_elem\\": %.3f,\\n", m.ns_per_elem);
        printf("      \\"samples\\": %u,\\n", m.samples);
        printf("      \\"ulp_0_pct\\": %.1f,\\n", 100.0 * m.ulp_0_count / m.samples);
        printf("      \\"ulp_1_pct\\": %.1f,\\n", 100.0 * m.ulp_1_count / m.samples);
        printf("      \\"ulp_2_pct\\": %.1f,\\n", 100.0 * m.ulp_2_count / m.samples);
        printf("      \\"ulp_gt2_pct\\": %.1f\\n", 100.0 * m.ulp_gt2_count / m.samples);
        printf("    }%s\\n", (i == all_metrics.size() - 1) ? "" : ",");
    }

    printf("  ]\\n}\\n");
    return 0;
}
"""

def run_harness():
    print("=" * 80)
    print("      VeloC Precision Contracts & Mathematical ULP Accuracy Harness     ")
    print("=" * 80)

    HARNESS_CPP.write_text(CPP_SOURCE, encoding="utf-8")
    cmd = [
        "C:/Program Files/Windhawk/Compiler/bin/clang++.exe",
        "-std=c++20",
        "-O3",
        "-static",
        "-fno-fast-math",
        "-frounding-math",
        str(HARNESS_CPP),
        "-o", str(HARNESS_EXE)
    ]

    print("[1/3] Compiling accuracy harness with strict IEEE-754 semantics...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"[FAIL] Compilation failed:\n{res.stderr}")
        return False

    print("[2/3] Evaluating 50,000+ random and edge-case samples per kernel...")
    res_run = subprocess.run([str(HARNESS_EXE)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res_run.returncode != 0:
        print(f"[FAIL] Execution failed:\n{res_run.stderr}")
        return False

    output_json = json.loads(res_run.stdout)
    out_file = RESULTS_DIR / "numerics_accuracy.json"
    out_file.write_text(json.dumps(output_json, indent=2), encoding="utf-8")
    print(f"[3/3] Results saved to {out_file.relative_to(ROOT_DIR)}")

    # Print summary table
    print("\n" + "=" * 80)
    print(f"{'FUNCTION':<10} | {'VARIANT':<8} | {'MAX ULP':<10} | {'MEAN ULP':<10} | {'LATENCY (ns)':<14} | {'0 ULP %':<8} | {'<=1 ULP %':<10}")
    print("-" * 80)
    for m in output_json["metrics"]:
        le1 = m['ulp_0_pct'] + m['ulp_1_pct']
        print(f"{m['name']:<10} | {m['variant']:<8} | {m['max_ulp']:<10.1f} | {m['mean_ulp']:<10.3f} | {m['ns_per_elem']:<14.2f} | {m['ulp_0_pct']:<7.1f}% | {le1:<9.1f}%")
    print("=" * 80)

    # Generate Markdown documentation
    md_lines = [
        "# VeloC Mathematical Kernel Accuracy Contracts & Verification",
        "",
        "**Host Target:** Intel Core i5-10400F (AVX2, Clang 20 MinGW)  ",
        f"**Test Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}  ",
        "**Sample Size:** 50,011 samples per function (including boundary, subnormal, near-zero edge cases)  ",
        "",
        "## Accuracy & Latency Verification Table",
        "",
        "| Function | Variant | Precision Contract | Measured Max ULP | Mean ULP | Latency (ns/elem) | Exactly Correct (0 ULP) | <= 1 ULP |",
        "|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|"
    ]

    for m in output_json["metrics"]:
        contract = "<= 1.0 ULP" if m['variant'] == "strict" else "<= 4.0 ULP"
        le1 = m['ulp_0_pct'] + m['ulp_1_pct']
        md_lines.append(f"| **`{m['name']}`** | `{m['variant']}` | {contract} | **{m['max_ulp']:.1f} ULP** | {m['mean_ulp']:.3f} | {m['ns_per_elem']:.2f} ns | {m['ulp_0_pct']:.1f}% | **{le1:.1f}%** |")

    md_file = ROOT_DIR / "docs" / "perf" / "accuracy_contracts.md"
    md_file.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"Documentation generated: {md_file.relative_to(ROOT_DIR)}")
    return True

if __name__ == "__main__":
    success = run_harness()
    sys.exit(0 if success else 1)
