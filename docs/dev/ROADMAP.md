# VeloC 12-Month Technical Roadmap

This roadmap defines the release milestones, stability criteria, and forward-looking research directions for VeloC.

---

## Milestone 1.0: Foundation & Stability (Current - Q4 2026)
**Theme**: Language freeze, production readiness, and long-term support.
- **Language Stability Guarantee**: Zero syntax breaking changes for all stable features across the 1.x lifecycle.
- **Self-Hosting Toolchain**: Native lexer, parser, formatter, linter, and package manager.
- **Hardening & Security**: Clang CFI, Windows `/guard:cf`, ASLR, DEP, stack canaries, secret types, and supply-chain auditing.
- **Production Reference Apps**: 7 flagship applications (`veloc-edit`, `veloc-db`, `veloc-render`, `veloc-pathtracer`, `veloc-llm`, `veloc-compiler`, `veloc-sync`).
- **Standardized CI / Crater**: Automated verification across all registered packages and apps on every compiler commit.

---

## Milestone 1.1: Compiler Optimizations & Cross-Platform (Q1 2027)
**Theme**: Micro-architecture tuning and platform expansion.
- **Enhanced Polyhedral Loop Tiler**: Auto-generation of multi-level cache blocking and loop skewing for tensor convolutions.
- **Linux & macOS Native Backends**: First-class packaging for Ubuntu LTS, Arch, and Apple Silicon (NEON 128-bit vectorization).
- **WebAssembly (WASM + SIMD)**: Direct compilation to WASM with 128-bit SIMD for browser execution.
- **Line Pragma Coalescence**: Elimination of intermediate `#line` pragmas across `else if` tokens.

---

## Milestone 1.2: Ecosystem & Developer Experience (Q2 2027)
**Theme**: Tooling, IDE integration, and package ecosystem.
- **Full LSP 3.17 Capabilities**: Semantic tokens, rename refactoring, inlay hints, and code actions.
- **Official Package Registry**: Cryptographically verified, distributed package index with automated supply chain signatures.
- **Documentation Engine v2**: Interactive web documentation with executable playground snippets.

---

## Milestone 2.0: Generational Evolution (2028+)
**Theme**: Next-generation memory models and native backend.
- **Static Substructural Lifetimes**: Compile-time borrow checking option eliminating runtime move assertions.
- **Direct LLVM IR Backend**: Optional direct emission to LLVM bitcode bypassing C++ transpilation for 30% faster compilation.
- **Heterogeneous Compute**: Unified kernel offloading to GPU (Vulkan Compute / Metal / CUDA).
