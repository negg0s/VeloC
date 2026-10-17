# VeloC Compilation Speed & Toolchain Engineering Architecture

**Document Version:** 1.0 (Stage 9 Architecture Specification)  
**Host Hardware Target:** Intel Core i5-10400F @ 2.90 GHz (6 Cores, 12 Threads, AVX2)  
**Baseline Toolchain:** Clang 20 (Windhawk / MinGW-w64), LLD (`ld.lld.exe`), Python 3.12  

---

## 1. Executive Summary & Problem Statement

Prior to Stage 9, every VeloC application compiled from a cold state in approximately **3.4 to 3.8 seconds**, regardless of whether the program was a 2-line "Hello World" or a 25,000-line database engine. While incremental rebuilds appeared to finish in **0.3 ms**, detailed instrumentation proved this was an instant cryptographic hash-cache hit (`.cache/*.hash`), rather than actual sub-millisecond compilation.

### Root Cause Analysis via `-ftime-trace`

Detailed LLVM `-ftime-trace` execution graphs revealed that:
1. **VeloC Frontend (Python):** Lexing, parsing, and transpiling 1,000 to 10,000 lines of code accounted for only **15 to 35 ms** (< 1% of total time).
2. **Fixed Clang C++ Overhead (97%):** Every compilation unit unconditionally prepended the monolithic `include/veloc.h` (3,716 lines) which pulled in heavy C++ standard library headers: `<iostream>`, `<chrono>`, `<thread>`, `<vector>`, `<unordered_map>`, `<sstream>`, `<fstream>`, and `<functional>`.
3. **Linker Overhead (GNU ld):** Default MinGW `ld.exe` performed single-threaded section resolution, relocation, and debug info generation, consuming 350-550 ms per invocation.

---

## 2. Architectural Solutions & Results

Stage 9 introduced a 5-pillar architectural solution to eliminate the cold compilation tax while maintaining zero-overhead C++ interoperability:

| Architecture Layer | Description | Cold Compile Speedup |
|:---|:---|:---:|
| **Lean Runtime Header (`veloc_core.h`)** | Decoupled lightweight runtime without heavy STL template blooms | **3.5x to 4.5x** |
| **Bit-for-Bit Precompiled Headers (`.pch`)** | Synchronized Clang AST caching for `veloc_core.h` and `veloc.h` | **5.0x to 8.8x** |
| **Fast Linker (`ld.lld.exe`)** | Parallelized PE/COFF linking with `--gc-sections` and `--dynamicbase` | **1.8x link speed** |
| **Direct LLVM IR Backend (`--backend=llvm`)** | Complete bypass of C++ transpilation emitting pure textual LLVM IR | **Bypasses C++ STL** |
| **Fine-Grained Query Object Cache** | Function-level content-addressed binary cache (`src/object_cache.py`) | **80% Hit Rate** |

### Benchmark Results Comparison

Measured on host hardware (Intel Core i5-10400F, 6C/12T):

| Compilation Configuration | Compilation Mode | Measured Time | Speedup vs Baseline |
|:---|:---|:---:|:---:|
| **Monolithic `veloc.h` (No PCH)** | Clang 20 `-O3` | 3,518.9 ms | 1.0x (Baseline) |
| **Lean `veloc_core.h` (No PCH)** | Clang 20 `-O3` | 867.2 ms | **4.06x faster** |
| **Monolithic `veloc.h` (+ Warm PCH)** | Clang 20 `-O3` | 713.6 ms | **4.93x faster** |
| **Lean `veloc_core.h` (+ Warm PCH)** | Clang 20 `-O3` | 398.1 ms | **8.84x faster** |
| **Direct LLVM IR Backend** | `clang -x ir -O3` | 420.1 ms | **8.38x faster** |
| **Cached Incremental Build** | CAS Hash Hit | 0.3 ms | Instant |

---

## 3. Detailed Component Deep-Dives

### 3.1. Lean Header Architecture (`include/veloc_core.h`)
`include/veloc_core.h` is designed specifically for performance-critical services, kernels, and micro-benchmarks that do not require C++ template-heavy containers. It directly includes:
- `<stddef.h>`, `<stdint.h>`, `<stdio.h>`, `<stdlib.h>`, `<string.h>`, `<stdbool.h>`, `<immintrin.h>`.
- Fast AVX2 SIMD vector types: `f32x8`, `f32x8_load`, `f32x8_store`, `f32x8_fmadd`.
- High-efficiency `Vec3` 16-byte aligned structs.
- Minimalistic formatted `println()` based directly on `printf`, avoiding all `<iostream>` template instantiation overhead.

### 3.2. Automated PCH Manager (`src/pch_manager.py`)
Clang strictly requires that compilation flags used during PCH generation match the compilation flags of the consumer down to preprocessor definitions (`-static`, `-fwrapv`, `-std=c++20`, `-fno-exceptions`).
`PchManager` computes a composite fingerprint:
```python
key = f"{CLANG_PATH}:{clang_mtime}:{flags_str}:{header_content_hash}"
fingerprint = sha256(key)[:12]
```
If compiler flags, clang binary, or header contents change, the PCH is automatically invalidated and regenerated on-demand.

### 3.3. Direct LLVM IR Backend (`src/llvm_backend.py`)
For maximum compilation speed and direct control over compiler optimizations, VeloC includes `--backend=llvm`:
- Emits textual LLVM IR (`.ll`) adhering to the `x86_64-w64-windows-gnu` target triple and data layout.
- Directly invokes `clang++ -m64 -mconsole -x ir -fuse-ld=lld`.
- Completely eliminates C++ transpilation, AST conversion, and header inclusion.

### 3.4. Background Compilation Daemon (`src/daemon.py`)
Running as a persistent background daemon on `127.0.0.1:45731`:
- Retains warm Python bytecode and compiler modules in memory.
- Keeps warm in-memory parsed AST nodes across repetitive builds.
- Serves CLI requests in sub-5ms latency for warm query hits.

### 3.5. Sub-Second Hot Reloading (`src/hot_reload.py`)
When invoked with `veloc watch <file.vc> --hot`:
- Compiles mutating functions into a dynamic companion shared library (`.dll`).
- Dynamically swaps function pointers in the host process using Win32 `LoadLibraryA` / `GetProcAddress`.
- Measured round-trip iteration latency: **786.3 ms** without killing or restarting the user application.

---

## 4. Developer CLI Reference

```bash
# Compile with full phase timing breakdown
veloc build app.vc --timings

# Output timings and build metrics in JSON format
veloc build app.vc --json

# Force lean runtime header (no heavy STL)
veloc build app.vc --lean

# Compile using direct LLVM IR backend (no C++ transpilation)
veloc build app.vc --backend=llvm

# Inspect binary PE sections, raw sizes, and virtual footprint
veloc size build/app.exe

# Compare executable binary size against a baseline
veloc size build/app.exe --diff build/baseline.exe

# Verify build time conforms to performance budgets (regression detector)
veloc build-bisect

# Run full compilation speed benchmark suite
veloc bench --build

# Run hot code reloading watch loop
veloc watch app.vc --hot
```

---

## 5. Performance Budget & Regression Invariants

Build speed budgets are codified in `perf-budget.toml`:
- `cold_build_hello_max_ms = 2000.0` (Hard ceiling on Windows toolchain subprocess invocation).
- `hot_build_hello_max_ms = 5.0` (Instant cache hit budget).
- `cold_build_10k_loc_max_ms = 2500.0` (Synthetic 10k LOC ceiling).
- `compiler_peak_rss_100k_max_mb = 50.0` (Audited at 10.89 MB peak).

Any commit causing a build regression > 10% is flagged and blocked by `veloc build-bisect`.
