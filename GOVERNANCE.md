# VeloC Project Governance

## 1. Governance Principles
The VeloC project is an open, consensus-driven systems programming language project dedicated to zero-cost abstractions, deterministic performance, and memory safety.

The project is governed by:
- **Core Team**: Technical stewards responsible for language specification, compiler architecture, release signing, and breaking-change veto.
- **Working Groups**: Specialized teams focusing on:
  - *Compiler & Code Generation* (Clang/LLVM interop, SIMD intrinsics, SSA IR)
  - *Standard Library & Tooling* (LSP, package manager, formatter, linter)
  - *Documentation & Community* (Tutorials, API guidelines, issue triage)

## 2. Decision Making & The RFC Process
All non-trivial changes (syntax changes, new stdlib modules, breaking changes) must go through the Request for Comments (RFC) process:
1. **Proposal**: Author writes an RFC following `rfcs/0000-template.md`.
2. **Review Period**: A minimum 14-day public review window.
3. **Consensus**: Working group and Core Team deliberate on design trade-offs.
4. **Final Comment Period (FCP)**: 7-day disposition period with intent to merge or close.
5. **Acceptance**: RFC is assigned an official number and merged into `rfcs/`.

## 3. Releases & Stability
- The Core Team maintains strict semantic versioning (`MAJOR.MINOR.PATCH`).
- Breaking changes are permitted only across MAJOR edition boundaries and must provide automated migration tools (`veloc fix`).
