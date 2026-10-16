# RFC-0002: Dual Execution Profiles: Safe Mode & Fast Mode

- **Feature Name**: `safe_fast_modes`
- **Start Date**: 2026-10-15
- **Status**: Accepted & Implemented

---

## 1. Summary
Defines two first-class compilation profiles in VeloC:
- **Safe Mode** (`--profile=safe` / `safe = true`): Mandatory bounds checking, integer overflow detection, pointer non-null validation, and contract assertions.
- **Fast Mode** (`--profile=fast` / `safe = false`): Strict `-O3`, `-ffast-math`, auto-vectorization, contract assumption hints (`__builtin_assume`), and zero-overhead release execution.

## 2. Motivation
Developers need debuggability and bulletproof memory verification during local testing and CI fuzzing, but demand raw hardware performance in production releases. Rather than ad-hoc flags, VeloC standardizes these into language-level contracts.
