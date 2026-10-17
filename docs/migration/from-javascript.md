# Migration Guide: JavaScript / TypeScript to VeloC

This guide targets JavaScript and TypeScript developers building server backends, data parsers, or WebAssembly engines who need native hardware speed without V8 JIT warm-up latency.

---

## 1. Conceptual Shift

| JavaScript / TS | VeloC | Key Differences |
| :--- | :--- | :--- |
| `number` (always 64-bit float) | `i32`, `i64`, `f32`, `f64` | Explicit integer bit-width prevents precision bugs |
| `interface Point { x: number; }` | `struct Point { f32 x; f32 y; };` | Flat contiguous memory without V8 hidden classes |
| `async / await` Promise loop | Thread pool / Work-stealing | True parallelism on all CPU cores, not single-threaded event loop |
| `JSON.parse()` | `veloc-data` SIMD parser | 20x higher throughput via 32-byte AVX2 whitespace skipping |
| JIT Compiler Warmup | AOT Native Compilation | Instant peak speed on cold start (0 ms warm-up time) |
| Memory garbage collection | Linear Arena and RAII | Deterministic latency (predictable p99.9 latency under 100 microseconds) |

---

## 2. Dealing with Strings and Objects

In JavaScript, strings are immutable and allocated on the V8 heap.
In VeloC:
- Strings can be stack spans (`Span<char>`) or raw pointers (`const char*`).
- Slices do not allocate new string copies; they reference existing memory using an offset and length.

---

## 3. High-Throughput HTTP Processing Example

In Node.js, `http.createServer` handles requests asynchronously, but CPU-bound tasks block the event loop.
In VeloC, each worker thread runs an event loop with work-stealing, processing **3.4 million HTTP requests/second** with zero dynamic allocations per request.
