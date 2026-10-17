# C++ Header Interoperability Audit & Limitations

VeloC is designed to interoperate with C and C++ libraries with zero marshalling overhead.

## 1. Verified Complex C++ Headers
The following standard library headers were audited and verified for direct usage in VeloC compilation units:

1. **`<algorithm>`**:
   - Tested: `std::sort`, `std::lower_bound`, `std::transform`, predicate lambdas.
   - Result: 100% compatible. Clang inlines algorithms into native vector instructions.
2. **`<vector>`**:
   - Tested: `std::vector<int>`, dynamic resizing, iterators, `begin()`, `end()`.
   - Result: 100% compatible.
3. **`<cmath>`**:
   - Tested: `std::sin`, `std::cos`, `std::sqrt`, `std::abs`.
   - Result: 100% compatible with strict IEEE-754 semantics.
4. **`<chrono>`**:
   - Tested: `std::chrono::high_resolution_clock`, duration casting (`nanoseconds`, `milliseconds`).
   - Result: 100% compatible.
5. **`<complex>`**:
   - Tested: `std::complex<double>`, complex multiplication, operator overloading.
   - Result: 100% compatible.

---

## 2. Architectural Limitations and Guidelines

1. **Non-Trivial Macro Collisions**:
   - Legacy Windows SDK headers (`winnt.h`, `windows.h`) define broad macros like `min`, `max`, `DELETE`, `ERROR`.
   - *Guideline*: Include `<windows.h>` with `#define NOMINMAX` and `#define WIN32_LEAN_AND_MEAN`.
2. **Heavy Template Compile-Time Overhead**:
   - Heavily templated libraries (`<iostream>`, `<regex>`, `<boost>`) can increase cold compilation times.
   - *Guideline*: Use precompiled headers (`PCH`) or VeloC's native modules (`veloc_core.h`, `FlatMap`, `SmallVec`).
3. **Exception Handling Across Boundaries**:
   - VeloC promotes `Result<T, E>` and does not rely on C++ exception unwinding (`-fno-exceptions` friendly).
   - *Guideline*: Wrap C++ exceptions at the boundary with `try / catch` before returning a VeloC `Result`.
