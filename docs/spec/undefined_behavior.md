# VeloC Undefined Behavior (UB) & Safety Specification

VeloC is designed to minimize Undefined Behavior (UB). In `safe` mode, all operations that could trigger UB in standard C/C++ are dynamically trapped, bounds-checked, or verified at runtime.

| UB Category | C/C++ Behavior | VeloC `fast` Mode | VeloC `safe` Mode | Specification Rule |
| :--- | :--- | :--- | :--- | :--- |
| **Out-of-Bounds Access** | Silent memory corruption | Unchecked pointer arithmetic | Runtime bounds check abort with diagnostic | `RULE-UB-001` |
| **Null Pointer Dereference** | Crash or compiler assumption | Hardware segfault | Dynamic null assertion trap via `unwrap()` | `RULE-UB-002` |
| **Unaligned SIMD Load** | Hardware fault (GPF) | Assumes 32-byte alignment | Asserts address % 32 == 0 before AVX load | `RULE-UB-003` |
| **Signed Integer Overflow** | Undefined Behavior | Two's complement wrap | Checked arithmetic / overflow trap | `RULE-UB-004` |
| **Use-After-Free / Double Free** | Heap corruption | Unchecked free | `TrackingAllocator` detects invalid/double free | `RULE-UB-005` |
| **Data Race on Memory** | Undefined Behavior | Data race | Atomic acquire-release fences in SPSC | `RULE-UB-006` |

---

### RULE-UB-001: Array and Slice Bounds
- Safe access through `Slice<T>` verifies `index < length`.
- Attempted access beyond bounds emits `[VeloC Bounds Check Error]` and terminates with exit code 1.

### RULE-UB-002: Null Pointer Dereferencing
- The unwrap operator `!` asserts `ptr != NULL` or `opt.is_some()`.
- Unwrapping a null reference emits `[VeloC Panic: Attempted to unwrap null or None value]`.

### RULE-UB-003: Aligned SIMD Loads
- SIMD loads via `f32x8_load` require `reinterpret_cast<uintptr_t>(ptr) % 32 == 0`.
- Safe SIMD loaders verify alignment before emitting `_mm256_load_ps`.

### RULE-UB-004: Signed Integer Overflow
- In `safe` mode, integer arithmetic is defined as two's complement wrapping without undefined compiler assumptions.

### RULE-UB-005: Heap Allocation Traps
- `TrackingAllocator` maintains a ledger of all active heap blocks. Double free triggers an immediate fatal diagnostic.

### RULE-UB-006: Data Races
- Multi-threaded shared memory access requires synchronized types (`LockFreeRingBuffer` or atomic variables).
