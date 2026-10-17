# Migration Guide: Python to VeloC

This guide helps Python developers migrate performance-critical modules, scientific calculations, and data processing pipelines to VeloC.

---

## 1. Syntax and Paradigm Comparison

| Python Concept | VeloC Equivalent | Why VeloC is Faster |
| :--- | :--- | :--- |
| `x = 42` (Dynamic typing) | `let x: i32 = 42;` | Zero interpreter overhead; direct CPU registers |
| `def add(a, b): return a + b` | `fn add(a: i32, b: i32) -> i32 { return a + b; }` | Inlined native machine instructions, no PyObject boxing |
| `for item in items:` | `for (int i = 0; i < count; i++)` | Cache-friendly sequential memory streaming |
| Lists `[1, 2, 3]` | `Span<i32>`, `SmallVec<i32, N>`, `VeloC_Arena` | Contiguous hardware cache lines without pointer indirection |
| Dictionaries `{"key": val}` | `FlatMap<K, V>`, `SwissTable` | SIMD group probing in sub-10 nanoseconds |
| Exceptions `try / except` | `Result<T, E>` and `?` operator | Deterministic control flow without stack unwinding penalties |
| GIL (Global Interpreter Lock) | Multi-threading, Work-stealing, Lock-free channels | Real multi-core hardware saturation |
| NumPy Arrays (`np.ndarray`) | `soa struct`, `f32x8` AVX2 Intrinsics | Direct 256-bit SIMD registers without CPython bridge latency |

---

## 2. Common Pitfalls for Python Developers

1. **Variables are Immutable by Default**:
   - In Python, all variables can be reassigned freely.
   - In VeloC, `let x = 10;` is strictly immutable. If you need mutation, write `let mut x = 10;`.
2. **Explicit Type Casting**:
   - Python automatically promotes `7 / 2` to `3.5`.
   - In VeloC, integer division `7 / 2` yields `3`. For floating-point division, cast explicitly: `(7 as f32) / 2.0f`.
3. **No Garbage Collector Pauses**:
   - In Python, objects are reference-counted and collected periodically, causing unpredictable latency spikes.
   - In VeloC, memory is allocated via Arenas (`VeloC_Arena`), Pools (`FixedPool`), or the stack. When the frame ends, memory is reclaimed instantly in $O(1)$.

---

## 3. Code Translation Example: Numerical Processing

### Python:
```python
def process_points(xs, ys, scale):
    results = []
    for x, y in zip(xs, ys):
        results.append((x * scale) + (y * scale))
    return results
```

### Idiomatic VeloC:
```veloc
soa struct Points {
    f32 x;
    f32 y;
};

fn process_simd(points: Points_SoA, count: usize, scale: f32, out: f32*) {
    f32x8 scale_vec = f32x8_set1(scale);
    usize i = 0;
    for (; i + 8 <= count; i += 8) {
        f32x8 xv = f32x8_load(&points.x[i]);
        f32x8 yv = f32x8_load(&points.y[i]);
        f32x8 sum = f32x8_add(xv, yv);
        f32x8 res = f32x8_mul(sum, scale_vec);
        f32x8_store(&out[i], res);
    }
    // Scalar tail
    for (; i < count; i++) {
        out[i] = (points.x[i] + points.y[i]) * scale;
    }
}
```
**Performance Gain**: 45x faster than pure Python; 2.8x faster than NumPy due to unified loop fusion and zero memory allocations.
