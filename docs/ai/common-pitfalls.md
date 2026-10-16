# Catalog of Common AI Model Pitfalls in VeloC

This document catalogs the top 10 hallucination patterns and syntax confusion commonly exhibited by Large Language Models (LLMs) when writing VeloC code, along with corrective rules.

---

### 1. Function Declaration Syntax (`fn` vs `def`)
* **Hallucination**: LLMs frequently mix Python `def foo():` and Rust `fn foo() -> i32:`.
* **Correct VeloC**: Both `fn foo() -> i32 { ... }` and `def foo() -> i32 { ... }` are supported, but curly braces `{ ... }` are required for multi-line block bodies.
* **Compiler Diagnostic**: *"Notice: VeloC uses curly braces `{ ... }` for function bodies; did you forget opening `{`?"*

### 2. Match Expression Syntax (No Rust Fat Arrows `=>`)
* **Hallucination**: LLMs often write Rust-style pattern match arms: `match val { 1 => { ... } }`.
* **Correct VeloC**: Match expressions use colon `:` or block syntax: `match (val) { case 1: ... }` or `case SlicePattern(...) { ... }`.
* **Compiler Diagnostic**: *"Syntax Error: unexpected `=>` in match expression; did you mean `case pattern:`?"*

### 3. C++ Standard Library Leakage (`std::vector::push_back` vs `vec.push()`)
* **Hallucination**: Calling `vec.push_back(item)` instead of `vec.push(item)`.
* **Correct VeloC**: VeloC vectors use `.push(item)`, `.pop()`, `.len()`, `.clear()`.
* **Compiler Diagnostic**: *"No member named 'push_back' in Vector; did you mean '.push(item)'?"*

### 4. Raw Unbounded Loops in Safety Mode
* **Hallucination**: Writing `while (true) { ... }` without a trip count.
* **Correct VeloC**: In `--profile=safety`, unbounded loops trigger `RULE-SAFE-005`. Use bounded loops `for (i in 0..MAX_STEPS)`.

### 5. Secret Variable Timing Leaks
* **Hallucination**: Writing `if (secret_key == candidate) { ... }`.
* **Correct VeloC**: Conditional branches on `Secret<T>` are flagged by `SEC-001`. Use `secret_key.constant_time_compare(candidate)` or `ct_select()`.

### 6. Dynamic Allocations in Real-Time / Safety Code
* **Hallucination**: Using `new Buffer()` or `malloc` in performance-critical kernels.
* **Correct VeloC**: Use stack-allocated fixed buffers `BitSet<N>`, `Array<T, N>`, or `Arena` allocation.

### 7. Incorrect Slice Indexing
* **Hallucination**: Passing raw pointer and length separately as two arguments everywhere.
* **Correct VeloC**: Use `Slice<T>` (e.g. `Span<f32>`) which bundles pointer and length with bounds checking.

### 8. Macro Invocation Syntax
* **Hallucination**: Writing macro definitions without `macro_rules! name { ($arg:expr) => { ... } }`.
* **Correct VeloC**: Use `macro_rules!` with hygienic variables `_tmp_var`.

### 9. Fast-Math Assumptions in Crypto
* **Hallucination**: Assuming floating-point arithmetic is associative in crypto or safety code.
* **Correct VeloC**: Use `--deterministic-math` to guarantee exact IEEE 754 precision and fixed reduction order.

### 10. Capability Manifest Disregard
* **Hallucination**: Calling network or filesystem APIs from untrusted packages without checking `veloc.toml`.
* **Correct VeloC**: Declare required permissions in `[capabilities] allow = ["fs.read", "net.http"]`.
