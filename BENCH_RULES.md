# Rules of the VeloC Benchmark Suite (BENCH_RULES.md)

This specification defines the rigorous scientific methodology governing all benchmarks published in the VeloC ecosystem.

---

## 1. Principles of Honest Benchmarking
1. **Identical Algorithms & Workloads**:
   - Competing implementations (C++, Rust, Zig, VeloC) must execute the exact same algorithmic work (e.g. identical number of matrix multiplications, FFT points, particles, or network requests).
2. **Fair Compiler Flags**:
   - C++ Baseline must be compiled with industry-standard peak flags: `-O3 -march=native -ffast-math -static` on the same Clang 20 compiler.
   - MSVC baseline must use `/O2 /arch:AVX2 /fp:fast`.
3. **Hardware Ground Truth & Physical Bounds**:
   - Every throughput number must be validated against theoretical hardware limits:
     - Peak Dual-Channel DDR4 RAM bandwidth on test machine: **~45.0 GB/s**. Any report claiming >45 GB/s must prove it fits in L1/L2/L3 cache.
     - Single-core 256-bit FMA peak: $2 \text{ ops/cycle} \times 8 \text{ floats} \times 4.3 \text{ GHz} \approx \mathbf{68.8 \text{ GFLOPS}}$.
4. **Statistical Rigor**:
   - Minimum **30 runs** per benchmark after a dedicated warm-up run.
   - Reports must record **Median**, **P95**, **Minimum**, and **Standard Deviation**.
5. **No Optimization Dead Code Elimination**:
   - Use `volatile` sinks or checksum assertions to ensure the compiler does not optimize away pure loops.
6. **Transparent Environment Telemetry**:
   - Every report must record CPU model, core/thread count, L1/L2/L3 cache sizes, RAM speed, OS version, and exact compiler versions.
