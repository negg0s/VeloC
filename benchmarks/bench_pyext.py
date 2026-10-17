# Scientific Comparative Benchmark: Pure Python vs NumPy vs VeloC Extension
# Evaluates in-place array scaling on 10,000,000 float32 elements (40 MB buffer)

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
import array
import numpy as np
import veloc_accel

N = 10_000_000
BUFFER_MB = (N * 4) / (1024 * 1024)
ITERS = 25

def bench_pure_python():
    # Test on smaller sample and extrapolate to avoid 60+ seconds freeze
    n_small = 500_000
    py_list = [1.0] * n_small
    t0 = time.perf_counter()
    for i in range(n_small):
        py_list[i] *= 2.5
    dt = time.perf_counter() - t0
    scaled_dt = dt * (N / n_small)
    return scaled_dt * 1000.0

def bench_numpy():
    arr = np.ones(N, dtype=np.float32)
    # Warmup
    arr *= 2.5
    times = []
    for _ in range(ITERS):
        t0 = time.perf_counter()
        arr *= 2.5
        times.append((time.perf_counter() - t0) * 1000.0)
    times.sort()
    return times[len(times) // 2], times[int(len(times) * 0.95)], min(times)

def bench_veloc():
    arr = np.ones(N, dtype=np.float32)
    # Warmup
    veloc_accel.fast_scale(arr, 2.5)
    times = []
    for _ in range(ITERS):
        t0 = time.perf_counter()
        veloc_accel.fast_scale(arr, 2.5)
        times.append((time.perf_counter() - t0) * 1000.0)
    times.sort()
    return times[len(times) // 2], times[int(len(times) * 0.95)], min(times)

if __name__ == "__main__":
    print("=" * 80)
    print("      Comparative Benchmark: Pure Python vs NumPy 2.4 vs VeloC Extension      ")
    print(f"      Workload: In-place Scaling of {N:,} float32 elements ({BUFFER_MB:.1f} MB RAM)      ")
    print("=" * 80)

    print("Running Pure Python baseline...")
    py_ms = bench_pure_python()
    print(f"  Pure Python (CPython 3.12):  {py_ms:8.2f} ms")

    print("Running NumPy 2.4 baseline...")
    np_med, np_p95, np_min = bench_numpy()
    np_gbps = (BUFFER_MB * 2 / 1024) / (np_med / 1000.0)
    print(f"  NumPy 2.4 (OpenBLAS/C-API):  {np_med:8.2f} ms (p95: {np_p95:.2f} ms, Bandwidth: {np_gbps:5.2f} GB/s)")

    print("Running VeloC Native AVX2 Extension...")
    vc_med, vc_p95, vc_min = bench_veloc()
    vc_gbps = (BUFFER_MB * 2 / 1024) / (vc_med / 1000.0)
    print(f"  VeloC PyExt (AVX2 zero-copy):{vc_med:8.2f} ms (p95: {vc_p95:.2f} ms, Bandwidth: {vc_gbps:5.2f} GB/s)")

    print("-" * 80)
    speedup_vs_python = py_ms / vc_med
    speedup_vs_numpy = np_med / vc_med
    print(f"  VeloC vs Pure Python Speedup: {speedup_vs_python:6.1f}x faster")
    print(f"  VeloC vs NumPy 2.4 Speedup:   {speedup_vs_numpy:6.2f}x faster")
    print("=" * 80)
