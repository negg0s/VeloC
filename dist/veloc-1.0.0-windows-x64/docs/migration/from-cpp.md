# Migration Guide: C++ to VeloC

This guide covers transitioning from modern C++ (C++17/C++20) to VeloC for systems, game engines, and low-latency financial systems.

---

## 1. Syntax and Language Mapping

| C++ Concept | VeloC Equivalent | Why VeloC is More Productive |
| :--- | :--- | :--- |
| `int x = 10;` | `let x = 10;` | Immutable by default; prevents accidental mutation bugs |
| `int x = 10; x = 20;` | `let mut x = 10; x = 20;` | Explicit mutation intent |
| `std::optional<T>` | `Option<T>` | Pattern matching and zero-cost `?` unwrap operator |
| `std::expected<T, E>` | `Result<T, E>` | First-class language syntax without template bloat |
| `AOS struct { float x, y, z; }` | `soa struct Particle { f32 x; f32 y; f32 z; }` | Automatic AVX2 32-byte aligned SoA layout generation |
| Header files (`.h` / `.hpp`) | Modules (`module M; import M;`) | 5x faster compilation with Precompiled Headers and LLD |
| Template errors (pages of text) | Rust-grade diagnostic errors | Exact source line underlining and suggestions |
| `new` / `malloc` | `VeloC_Arena`, `FixedPool`, `TrackingAllocator` | Deterministic memory without memory fragmentation |
| Signed overflow is UB | Two's complement wrap (`-fwrapv`) | Deterministic arithmetic without compiler trapdoors |
| Global `-ffast-math` bugs | Strict IEEE-754 default + explicit ULP contracts | Reliable scientific computing and NaN preservation |

---

## 2. Using Existing C++ Libraries in VeloC

Because VeloC transpiles directly to clean C++ and compiles via Clang, **all existing C/C++ libraries can be called directly without FFI wrappers**:

```veloc
#include <cmath>
#include <vector>

int main() {
    std::vector<int> numbers = {1, 2, 3, 4, 5};
    double root = std::sqrt(16.0);
    printf("Root: %.1f, Count: %d\n", root, (int)numbers.size());
    return 0;
}
```

---

## 3. Automated Migration Tool: `veloc from-cpp`

VeloC provides an automated transpiler to convert legacy C++ files to idiomatic VeloC:
```bash
python veloc.py from-cpp legacy_file.cpp -o migrated.vc
```
It handles:
- Variable declarations (`int x = 5;` -> `let mut x = 5;`)
- Stream output (`std::cout << val << std::endl;` -> `printf("%d\n", val);`)
- Function signatures and control flow.
