# Formally Verified Guarantees & Safety Theorems

This document catalogs mathematical invariants, safety theorems, and formal verification proofs established for the VeloC language runtime and compiler pipeline.

## 1. Verified Runtime Data Structures

### Guarantee G-001: BoundedQueue Inductive Invariant Preservation
* **Component**: `veloc::BoundedQueue<T, Capacity>` / Ring Buffer.
* **Theorem**: For all execution sequences of valid operations, the queue invariants $0 \le count \le Capacity$ and $tail = (head + count) \pmod{Capacity}$ hold inductively.
* **Proof Technique**: State-space model enumeration & induction via `src/formal_core.py`.
* **Assumptions**: Single-threaded access or protected by enclosing lock/mutex.

### Guarantee G-002: HardenedAllocator Canary Non-Bypass
* **Component**: `veloc::security::HardenedAllocator`.
* **Theorem**: Any linear out-of-bounds write of $\ge 8$ bytes past the allocation boundary corrupts the 64-bit footer canary (`0xFEEDFACEDEADBEEF`), triggering immediate deterministic abort on `deallocate()`.
* **Proof Technique**: Memory layout verification in `tests/test_block_a_security.vc`.

### Guarantee G-003: Constant-Time Secret Equality
* **Component**: `veloc::security::Secret<T>`, `veloc::security::SecretBytes<N>`.
* **Theorem**: `constant_time_eq()` executes in a fixed number of CPU cycles proportional only to buffer length $N$, with zero conditional jumps or cache-dependent early exits.
* **Proof Technique**: Instruction inspection (`_mm_xor_si128` / bitwise OR accumulation), verified by `src/security.py::SecretBranchLinter`.

## 2. Compiler Optimization Guarantees

### Guarantee G-004: Bit-for-Bit Build Reproducibility
* **Component**: `veloc.py build` with `-Wl,--no-insert-timestamp`.
* **Theorem**: Compiling the same VeloC source in independent directory roots yields bit-for-bit identical binary SHA-256 digests.
* **Proof Technique**: Dual-environment isolation test in `src/sbom.py::ReproducibilityVerifier`.

### Guarantee G-005: Translation Validation Soundness
* **Component**: `src/translation_validation.py`.
* **Theorem**: MidIR constant folding and dead code elimination passes preserve input-output semantics across all integer test domains.
