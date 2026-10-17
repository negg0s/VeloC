# VeloC Floating-Point & Numerics Precision Policy

**Specification Version:** 1.0 (Stage 10 Precision & Correctness Specification)  
**Default Semantics:** IEEE-754 Strict Conformance  
**Compiler Modes:** `strict` (default), `relaxed`, `fast`, `reproducible`  

---

## 1. Core Principles & Philosophy

Historically, high-performance systems languages and compilers often enabled `-ffast-math` or unconstrained algebraic reassociation by default to artificially boost benchmark numbers. In VeloC, this practice is formally abandoned:

1. **Safety & Correctness First:** Floating-point operations adhere to **IEEE-754** standard semantics by default.
2. **Explicit Opt-in for Relaxations:** Fast approximations, reciprocal math, and non-associative reductions must be requested explicitly via compiler flags or function-level attributes.
3. **Formal Accuracy Contracts:** Every standard mathematical kernel has a documented and continuously tested bound on its maximum error in **ULP** (Unit in the Last Place).
4. **Reproducibility Guarantee:** In `reproducible` mode, reduction trees yield identical bit-for-bit results across arbitrary thread counts and vector architectures (AVX2, SSE4.2, scalar).

---

## 2. Compiler Precision Modes

VeloC provides four distinct precision profiles via the `--fp=<mode>` flag:

| Mode | Clang Compiler Flags | IEEE-754 Conformance | NaN / Inf Handling | FMA Contraction | Associative Reductions |
|:---|:---|:---:|:---:|:---:|:---:|
| **`strict` (Default)** | `-fno-fast-math -frounding-math -fno-associative-math -ffp-contract=off` | **Full (100%)** | Preserved & Validated | Disabled | Strict In-Order |
| **`relaxed`** | `-fno-fast-math -frounding-math -ffp-contract=fast` | **High (>99.9%)** | Preserved | Enabled (`vfmadd`) | In-Order |
| **`fast`** | `-ffast-math` | Relaxed | Undefined | Enabled | Unconstrained |
| **`reproducible`** | `-fno-fast-math -frounding-math -ffp-contract=off -fno-associative-math` | **Full (100%)** | Preserved | Disabled | Deterministic Tree / Kahan |

### Why `-ffast-math` is Forbidden Globally
- **Breaks `isnan()` and `isinf()`:** Under `-ffast-math`, compilers assume NaN cannot exist, optimizing expressions like `x != x` to `false` and stripping defensive safety guards.
- **Destroys Associativity & Determinism:** `(a + b) + c` is not equal to `a + (b + c)` in floating-point arithmetic. Global reassociation produces divergent results when workloads are split across different numbers of parallel threads.
- **Subnormal Flush Violations:** Forcing Flush-to-Zero (FTZ) can produce catastrophic cancellation in scientific algorithms relying on gradual underflow.

---

## 3. Function-Level Attributes

Developers can control floating-point semantics with granular per-function attributes:

```veloc
// Strict IEEE-754 execution (ignores global fast flags)
#[fp(strict)]
fn calculate_orbit(pos: Vec3, vel: Vec3) -> f64 { ... }

// Permits FMA contraction for performance while preserving NaNs
#[fp(relaxed)]
fn matrix_multiply(a: &[f32], b: &[f32], c: &mut [f32]) { ... }

// Permits full vectorization and reassociation
#[fp(fast)]
#[assoc_reduce]
fn particle_energy_sum(particles: &[Particle]) -> f32 { ... }

// Enables hardware Flush-to-Zero (FTZ) and Denormals-are-Zero (DAZ)
#[ftz]
fn audio_dsp_reverb(buffer: &mut [f32]) { ... }

// Guarantees bit-for-bit reproducibility across all threads & CPUs
#[reproducible]
fn financial_ledger_total(amounts: &[f64]) -> f64 { ... }
```

---

## 4. Accuracy Contracts for Mathematical Kernels

Every mathematical function in [`include/veloc_numerics.h`](file:///D:/VeloC/include/veloc_numerics.h) conforms to a strict ULP error contract:

| Function | Variant | Max Error (ULP) | Tested Domain | Boundary & Tricky Cases |
|:---|:---|:---:|:---:|:---|
| **`exp(x)`** | `strict` | **$\le 1.0$ ULP** | $[-87.3, 88.7]$ | Denormals preserved; $\pm\infty$ on overflow |
| **`exp_fast(x)`** | `fast` | **$\le 2.8$ ULP** | $[-87.0, 88.0]$ | Horner Minimax polynomial |
| **`log(x)`** | `strict` | **$\le 1.0$ ULP** | $(0, 10^{38}]$ | $\text{NaN}$ on $x < 0$, $-\infty$ on $x = 0$ |
| **`log_fast(x)`** | `fast` | **$\le 3.2$ ULP** | $(0, 10^{38}]$ | Log2 mantissa decomposition |
| **`sin(x)`, `cos(x)`** | `strict` | **$\le 1.0$ ULP** | $[-10^7, 10^7]$ | Range reduction with Cody-Waite / Payne-Hanek |
| **`tanh(x)`** | `strict` | **$\le 1.0$ ULP** | $[-10.0, 10.0]$ | Exact asymptotes $\pm 1.0$ |
| **`tanh_fast(x)`** | `fast` | **$\le 3.5$ ULP** | $[-9.0, 9.0]$ | Rational padé approximation |
| **`erf(x)`** | `strict` | **$\le 1.0$ ULP** | $[-4.0, 4.0]$ | Asymptotes $\pm 1.0$ |
| **`rsqrt(x)`** | `fast` | **$\le 1.5$ ULP** | $(0, 10^{38}]$ | SSE `_mm_rsqrt_ss` + 1 Newton-Raphson pass |
| **`sqrt(x)`** | `strict` | **$\le 0.0$ ULP** | $[0, 10^{38}]$ | Hardware IEEE square root (exact) |
| **`GeLU(x)`** | `strict` | **$\le 1.0$ ULP** | $[-10.0, 10.0]$ | Exact $0.5x(1 + \text{erf}(x/\sqrt{2}))$ |
| **`GeLU(x)`** | `fast` | **$< 0.01\%$ Rel**| $[-10.0, 10.0]$ | Hendrycks & Gimpel Tanh Approximation |
| **`Softmax(x)`** | `strict` | **$\le 1.0$ ULP** | Real Logits | Numerically stable: $\max(x)$ subtracted |

---

## 5. Deterministic & Reproducible Reductions

Standard floating-point summation $\sum_{i=1}^N x_i$ is non-deterministic under variable thread partitioning because $(a + b) + c \neq a + (b + c)$.

VeloC provides two deterministic summation engines:

### 1. Pairwise Summation (`veloc_reproducible_sum`)
Partitions the array into a fixed, balanced binary reduction tree:
$$\text{Sum}(A[0..N]) = \text{Sum}(A[0..N/2]) + \text{Sum}(A[N/2..N])$$
Because the binary tree topology is completely independent of the number of worker threads or SIMD vector register width, the resulting floating-point value is **100% bit-for-bit identical on 1, 2, 4, 8, or 12 threads**.

### 2. Kahan Compensated Summation (`veloc_kahan_sum`)
Maintains a second accumulator $c$ tracking low-order bits lost during addition. Guarantees total numerical error of order $\mathcal{O}(\epsilon)$ instead of standard sequential $\mathcal{O}(N \epsilon)$.

---

## 6. Static Analysis & Diagnostics (FP-Linter)

The compiler checks source files for common numerical bugs:
- **`FP-001` (Warning):** Direct float equality comparison (`x == y` or `x != y`). Prompts for `approx_eq(x, y, ulp)`.
- **`FP-002` (Error):** `isnan()` or `isinf()` invoked within a `#[fp(fast)]` or `--fp=fast` compilation unit.
- **`FP-003` (Info):** Division by an unguarded float expression without checking for zero or subnormals.
