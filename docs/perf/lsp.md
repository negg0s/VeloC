# VeloC Language Server Performance Benchmark

Empirical evaluation of the VeloC Language Server on a **1,000-file project topology** (50,000 lines of code, cross-file imports).

Hardware Environment:
- CPU: Intel Core i5-10400F (6 cores, 12 threads @ 2.90 GHz)
- OS: Windows 10 x86_64
- Topology: 1,000 `.vc` files with cross-module structs, functions, and global constants

---

## Benchmark Results

| Metric | Measured Result | SLA Target | Status |
|---|---|---|---|
| **Cold Start Indexing (1,000 files)** | **0.413 s** | < 2.0 s | **PASSED** |
| **Completion Latency (p50)** | **1.201 ms** | < 15.0 ms | **PASSED** |
| **Completion Latency (p95)** | **3.653 ms** | < 40.0 ms | **PASSED** |
| **Diagnostics Latency (p50)** | **0.002 ms** | < 50.0 ms | **PASSED** |
| **Diagnostics Latency (p95)** | **0.013 ms** | < 120.0 ms | **PASSED** |
| **Project-Wide Rename (1,000 files)** | **25.83 ms** | < 500.0 ms | **PASSED** |

---

## Editor Features Verified

- **Auto-Completions**: Keywords, primitive types, sizes/alignments, standard library types (`Arena`, `Buffer`, `Pool`, `Result`), and user-defined functions.
- **Hover Tooltips**: Docstrings, exact byte size and memory alignment of types, function signatures.
- **Diagnostics & QuickFix**: Debounced syntax and type checks with automatic correction code actions.
- **Inlay Hints**: Variable type inferences (`let x: i32 = 42;`).
- **Semantic Tokens**: Rich syntax coloring distinguishing types, variables, functions, and keywords.
- **Global Rename**: Atomic multi-file text replacement with full index awareness.
