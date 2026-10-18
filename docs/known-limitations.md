# VeloC: Known Limitations & Transparent Trade-offs (1.0.0)

This document provides a candid, unvarnished evaluation of VeloC's current architectural limitations, design trade-offs, and areas targeted for future releases.

---

## 1. Backend & Compilation Pipeline
- **Transpilation to C++20**:
  - *Current Reality*: VeloC compiles to clean C++20 and invokes Clang/LLVM (`clang++.exe`) for code generation, linking, and optimization.
  - *Limitation*: While this enables instant access to LLVM's world-class optimizer and zero-overhead C++ interop, cold compilation of large translation units takes 2-3 seconds per file (mitigated by our 0.3 ms incremental compilation cache). Note: a direct textual LLVM IR backend already exists (eloc.py build --backend=llvm), but the default cpp backend is primary in practice.
- **Source Map Line Pragma Splitting**:
  - *Current Reality*: Chaining `else if` without braces can occasionally cause the source map generator to insert an intermediate `#line` pragma between `else` and `if`.
  - *Workaround*: Write nested `else { if (...) {} }` blocks. No coalescence is implemented yet (nothing is scheduled: the roadmap lives in docs/dev/ROADMAP.md).

---

## 2. Grammar & Syntax Nuances
- **Bitwise Compound Assignment**:
  - *Current Reality*: The lexer currently splits `^=` into `^` and `=`.
  - *Workaround*: Use explicit expansion `x = x ^ mask;`.
- **Global / Standard Symbols**:
  - *Current Reality*: Types declared in `include/veloc.h` (such as `Vec3`, `Vec4`, `Mat4`) are globally accessible. Defining identical type names in user code requires namespacing or qualified names to prevent C++ redefinition errors.
- **Platform Header Identifiers**:
  - *Current Reality*: Standard Windows SDK headers (`winnt.h`) define generic tokens like `TokenType`. User enum types should always include a domain prefix (`EditTokenType`).

---

## 3. Type System & Memory Model
- **Affine / Linear Semantics**:
  - *Current Reality*: `Linear<T>` is enforced via move-only constructors, double-use assertions, and unconsumed destructor validation.
  - *Limitation*: Static compile-time substructural lifetime tracking without runtime assertions requires a full borrow-checker, Borrow-checker work is not scheduled (see docs/dev/ROADMAP.md).
- **Dynamic Dispatch Overhead**:
  - *Current Reality*: Dynamic virtual table dispatch (`dyn Trait`) carries a measured ~64,000x latency penalty compared to inlined AVX2 SIMD operations.
  - *Guidance*: VeloC is designed for high-performance computing; developers are strongly advised to use static generics, templates, and closed tagged enums for performance-critical inner loops.

---

## 4. Platform & Ecosystem Support
- **Host OS**:
  - *Current Reality*: VeloC is verified on Windows x86_64 only (this repo's checks: Windows 11, Clang 20.1.3, eloc.py test 3/3 golden + eloc.py ci 26/26). Linux/macOS are by design simple Clang builds, but they are NOT verified: the linker flags (-static/-lws2_32/PE mitigations) are gated to Windows since the 1.0.0 cleanup; run on your own risk. ARM64: no verification exists.
