# VeloC-Compiler Application Report

## Architecture
- **Language**: VeloC 1.0 (Transpiled to C++20 via Clang)
- **Lines of Code**: 238 LOC (`apps/veloc-compiler/src/main.vc`)
- **Compilation Time**: 3.24 seconds
- **Transpile Time**: 7.0 ms

## Components
1. `MicroOp` & `Instruction`: Stack machine bytecode definitions including integer math, relational comparisons, and branching.
2. `MicroVm`: Dynamic bytecode interpreter with variable environments and value stack.
3. `optimize_constant_folding`: Optimization pass simplifying constant operations ($a \text{ op } b$) at compile time into folded constants.
4. `Sum(1..1M)` test program: Full verification of loop condition evaluation, accumulator arithmetic, and variable loads/stores.

## Benchmark Results (i5-10400F Single Thread)
- **Constant Folding**: Reduced 6 AST bytecode instructions to 4 instructions, evaluated expression `(10 + 20) * 3` directly to `90`.
- **Accumulator Loop**: Executed $13,000,010$ bytecode instructions in $114.38\text{ ms}$.
- **Throughput**: $113.66\text{ MIPS}$ (Million Instructions Per Second).
- **Correctness**: Output matched expected $500,000,500,000$.

## Language Pains & Lessons Learned
- **`else if` Token Splitting**: In VeloC, chaining `else if` on the same line caused `#line` pragma insertion between `else` and `if`. Nesting `else { if (...) { ... } }` avoided the split. Added to compiler bug list and test suite.
