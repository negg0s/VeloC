# Migration Guide: Rust to VeloC

This guide is designed for Rust developers who appreciate memory safety and strong type systems, but desire faster compile times, simpler mental models for memory management, and transparent hardware control.

---

## 1. Philosophical Comparison

| Concept | Rust | VeloC | Advantage / Trade-off |
| :--- | :--- | :--- | :--- |
| **Safety Model** | Strict Compile-time Borrow Checker | First-class Allocators + Static Bounds Checker + Safety Profile | VeloC compiles 10x faster; explicit Arenas eliminate lifetime fighting |
| **Variables** | `let x = 5;`, `let mut x = 5;` | `let x = 5;`, `let mut x = 5;` | Familiar, ergonomic syntax |
| **Error Handling** | `Result<T, E>`, `Option<T>`, `?` | `Result<T, E>`, `Option<T>`, `?` | Identical idiomatic pattern |
| **Destructors** | `Drop` trait at scope end | `defer` statement + RAII structs | Explicit execution order without drop-check edge cases |
| **SIMD** | `std::simd` (nightly) or intrinsics | First-class `soa struct` + `f32x8` | Native compiler support for SoA alignment |
| **Build Times** | Often 30s – 5min for medium crates | Sub-second with PCH and LLD | Instant iterative development feedback |

---

## 2. Dealing with Memory Without Lifetime Fighting

In Rust, complex graphs, games, or compilers often struggle with borrow checker rules, requiring `Rc<RefCell<T>>`, `Arena`, or generational indices.

In VeloC:
- **Arenas are First-Class**: Allocate all temporary objects for a frame, request, or AST pass in a `VeloC_Arena`.
- **Zero Lifetimes on Types**: The data structures remain plain pointers (`T*` or `Span<T>`).
- **Instant Deallocation**: When the pass finishes, call `arena.reset()`. All memory is instantly reclaimed in $O(1)$ without walking object trees or running destructors one by one.

---

## 3. Code Translation Example: Option and Try Operator

### Rust:
```rust
fn parse_port(s: &str) -> Result<u16, &'static str> {
    let val: u32 = s.parse().map_err(|_| "invalid number")?;
    if val > 65535 {
        return Err("port out of range");
    }
    Ok(val as u16)
}
```

### VeloC:
```veloc
fn parse_port(s: const char*) -> Result<u16, const char*> {
    if (s == NULL || s[0] == '\0') {
        return Err("empty port string");
    }
    let val = atoi(s);
    if (val <= 0 || val > 65535) {
        return Err("port out of range");
    }
    return Ok((u16)val);
}
```
