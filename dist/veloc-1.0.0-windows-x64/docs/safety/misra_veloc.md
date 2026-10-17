# MISRA-VeloC Safety Rules & Guidelines

> **Notice**: No formal regulatory certification is claimed. This catalog provides structural alignment and static safety rules inspired by MISRA C:2012, CERT C, and ISO 26262 for safety-critical systems in VeloC.

## 1. Memory and Allocations
- **RULE-SAFE-001 (Mandatory)**: Dynamic heap allocation (`malloc`, `free`, `Box`, unbounded resizing `Vec`) is prohibited in `--profile=safety`. Fixed-capacity buffers (`BitSet<N>`, `Array<T, N>`, static ring buffers) must be used.
- **RULE-SAFE-002 (Mandatory)**: Pointer arithmetic outside validated `Slice<T>` / `Span<T>` views is forbidden.
- **RULE-SAFE-003 (Mandatory)**: All memory regions must be zero-initialized or explicitly initialized at declaration.
- **RULE-SAFE-004 (Required)**: Memory freeing must occur only via RAII or arena reset; no raw manual pointer deletions.

## 2. Control Flow and Recursion
- **RULE-SAFE-005 (Mandatory)**: Unbounded loops (`while (true)`) are forbidden. Every loop must declare a verifiable static trip bound or iteration limit.
- **RULE-SAFE-006 (Mandatory)**: Direct and indirect recursion is prohibited. All call graphs must be acyclic.
- **RULE-SAFE-007 (Required)**: `goto` statements and non-local jumps (`setjmp`/`longjmp`) are prohibited. Single-exit or structured guard breaks only.
- **RULE-SAFE-008 (Required)**: All `match` statements over enums and types must be exhaustive; wildcard `_` is not permitted in safety-critical mode without explicit audit note.

## 3. Types and Arithmetic
- **RULE-SAFE-009 (Mandatory)**: Floating-point arithmetic must not use `-ffast-math`. Strict IEEE 754 rounding and associativity preservation is enforced.
- **RULE-SAFE-010 (Mandatory)**: Integer signed and unsigned wrapping must be well-defined (`-fwrapv`, `wrapping_add`). Implicit unchecked truncation between integer sizes is an error.
- **RULE-SAFE-011 (Required)**: Downcasting pointers or casting between incompatible struct representations is prohibited.

## 4. Traceability and Verification
- **RULE-SAFE-012 (Required)**: Every safety-critical function must be annotated with `#[req("REQ-XXX")]` mapping to an approved requirement in the system specification.
- **RULE-SAFE-013 (Required)**: Automated unit tests must verify every `#[req("REQ-XXX")]` with line, branch, and condition coverage.
- **RULE-SAFE-014 (Required)**: Static Worst-Case Execution Time (WCET) bounds must be calculated and verified for all real-time cyclic routines.
