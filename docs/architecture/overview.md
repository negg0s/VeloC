# VeloC Compiler Architecture & Contributor Overview

Welcome to the internal architecture guide for VeloC!

---

## 1. High-Level Pipeline

```
[ .vc Source Code ]
        │
        ▼ (src/lexer.py)
[ Token Stream ]
        │
        ▼ (src/parser.py)
[ Semantic Typed AST ]
        │
        ├────────────────────────────────┐
        ▼ (src/ir.py)                    ▼ (src/transpiler.py)
[ SSA Intermediate Representation ]   [ C++20 Clean Transpiled Code ]
  - HighIR (Typed constructs)           - Aligned SIMD types (include/veloc.h)
  - MidIR (Basic blocks, %v registers)  - Monomorphized templates
  - LowIR (Linear virtual machine)      - Zero-overhead RAII wrappers
        │                                │
        ▼ (Optimization Passes)          ▼ (Clang 20 MinGW)
  - Inlining                           [ Native Executable Binary ]
  - Constant Folding                     - Stack Protector
  - Auto-Vectorization (AVX2)            - ASLR & DEP
  - Bounds Check Elimination             - Static Runtime
```

---

## 2. Source Tree Organization

- `src/`: Compiler core subsystems
  - `lexer.py`: Lexical analysis, source line tracking, tokenization
  - `parser.py`: Recursive descent parser, type inference, AST construction
  - `transpiler.py`: C++20 code generation with `#line` source map pragmas
  - `ir.py`: Multi-level intermediate representation and optimization passes
  - `diagnostics.py`: Rust-style compiler diagnostics with error codes and suggestions
  - `security.py`: PE hardening checker (ASLR, DEP, Stack Protection)
  - `crater.py`: Ecosystem-wide regression testing gate
  - `health_dashboard.py`: Codebase health metrics generator
- `include/`: Core headers
  - `veloc.h`: Zero-overhead standard library, SIMD vectors, Piece Table, Allocators
- `apps/`: Production flagship applications
  - `veloc-edit`, `veloc-db`, `veloc-render`, `veloc-pathtracer`, `veloc-llm`, `veloc-compiler`, `veloc-sync`
- `tests/`: Test runners and suites
  - Unit tests, differential testing, metamorphic testing, golden tests, DoS tests
- `benchmarks/`: Rigorous physical benchmarks

---

## 3. Developing & Testing
Run developer setup:
```bash
python veloc.py dev-setup
```
Run ecosystem crater check:
```bash
python veloc.py crater
```
Run CI test suite:
```bash
python veloc.py ci
```
