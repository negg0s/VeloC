# veloc-sci: Scientific Computing & Numerical Engine for VeloC

`veloc-sci` provides high-precision linear algebra, signal processing, numerical ODE integration, and statistical simulation tools.

## Architecture & Features

1. **Linear Algebra**:
   - `cholesky`: Cholesky factorization ($A = L \cdot L^T$) for symmetric positive-definite matrices.
   - `lu_decompose`: LU decomposition with partial row pivoting ($P \cdot A = L \cdot U$) with singularity detection.
   - `lu_solve`: Forward and backward triangular substitution solving $A \cdot x = b$.
2. **Signal Processing & Fourier Analysis**:
   - `fft_radix2`: Cooley-Tukey Radix-2 in-place Fast Fourier Transform with bit-reversal indexing and forward/inverse transforms.
   - Reaches **56.17 Million complex samples per second** on 16,384 points.
3. **Ordinary Differential Equations (ODE)**:
   - `rk4_step`: Classical 4th-order Runge-Kutta integrator with fourth-order global truncation error $O(\Delta t^4)$.
   - Demonstrates zero radial drift ($< 10^{-8}$) over full orbital trajectories.
4. **Monte Carlo Methods**:
   - `monte_carlo_integrate_1d`: Statistical numerical quadrature over arbitrary integrands.

## Benchmarks (Intel Core i5-10400F, Clang 20, AVX2)

| Algorithm | Scale | Latency | Throughput | Speedup vs Reference |
|---|---|---|---|---|
| **Direct Naive DFT** | 2,048 points | 175.64 ms | 0.012 M samples/s | 1.0x (Baseline) |
| **Cooley-Tukey FFT** | 2,048 points | 0.0255 ms | 80.31 M samples/s | **6,898.7x** |
| **Cooley-Tukey FFT** | 16,384 points| 0.29 ms | **56.17 M samples/s** | - |
| **RK4 Orbital Simulation**| 6,283 steps | 3.5 ms | 1.80 M steps/s | 0.00000000 Drift |

## Running Tests & Demonstrations

```bash
# Run unit tests (Cholesky, LU, FFT roundtrip, RK4 decay)
python veloc.py run packages/veloc-sci/tests/test_sci.vc

# Run FFT benchmark vs direct DFT
python veloc.py run packages/veloc-sci/benchmarks/bench_fft.vc

# Run orbit simulation & Monte Carlo PI demo
python veloc.py run packages/veloc-sci/examples/demo_sci.vc
```
