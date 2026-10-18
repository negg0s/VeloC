# VeloC Agent & AI Assistant Instructions

This repository is the VeloC systems language compiler, standard library, and runtime toolchain.

## 1. Quick CLI Reference
- **Check code**: `python veloc.py check <file.vc>`
- **Compile**: `python veloc.py build <file.vc> -o bin/<output.exe>`
- **Run**: `python veloc.py run <file.vc>`
- **Inspect Security Hardening**: `python veloc.py harden-check bin/<output.exe>`
- **Trace Requirements**: `python veloc.py trace-reqs`
- **Supply Chain Audit**: `python veloc.py audit`
- **License Check**: `python veloc.py licenses`
- **AI Code Check**: `python veloc.py ai-check <file.vc>`
- **Project Context for LLMs**: `python veloc.py context`
- **Model Context Protocol Server**: `python veloc.py mcp`

## 2. Coding Patterns to Enforce
1. **Memory Safety**: Use `Slice<T>` / `Span<T>` instead of raw pointer/length pairs.
2. **Secrets**: Use `Secret<T>` and `constant_time_compare()` to prevent timing side channels.
3. **Safety Profile**: When compiling with `--profile=safety`, no heap allocations (`malloc`, `new`) or unbounded `while (true)` loops are permitted.
4. **SIMD**: Use intrinsics via `veloc_stage6.h` (`gemm_microkernel_6x16_f32`, `bitonic_sort_16_f32`).
