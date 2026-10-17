# VeloC Memory Model Specification

## 1. Memory Organization

### RULE-MEM-001: Stack Frame & Alignment
- All stack frames conform to target ABI requirements.
- On x86/x86-64, SIMD vectors (`f32x8`) and aligned allocations must maintain a 32-byte alignment boundary.
- Dynamic stack allocations maintain 16-byte alignment minimum for SSE, realigned to 32-byte for AVX2.

### RULE-MEM-002: Allocators
Heap allocation is managed through explicit, first-class allocator concepts:
1. `TrackingAllocator`: Wraps global malloc/free, records active allocations, tracks high-water mark, and reports leak diagnostics upon termination.
2. `TempAllocator`: Thread-local monotonic ring buffer for zero-fragmentation ephemeral memory with fast scoped reclamation.
3. `VeloC_Arena`: Contiguous chunk allocator with O(1) allocation and instant marker rewind (`arena.rewind(marker)`).
4. `FixedPool`: Fixed-size chunk free-list allocator eliminating external fragmentation for uniform object lifespans.

### RULE-MEM-003: Aligned Allocation
- `veloc_aligned_alloc(alignment, size)` guarantees that the returned memory address is a multiple of `alignment` (typically 32 bytes for AVX2).
- Freeing memory allocated via `veloc_aligned_alloc` must use `veloc_aligned_free`.

### RULE-MEM-004: Lifetimes and Scope Guards
- `defer <stmt>` creates a lexical scope guard.
- Defer statements execute in Last-In-First-Out (LIFO) order upon exiting their containing scope block.
- Execution is guaranteed upon all normal exits (return, break, end of block).

### RULE-MEM-005: Concurrency and Race Freedom
- Shared mutable access across OS threads without atomic operations or synchronization primitives is undefined behavior in fast mode, and checked via atomic wrappers in safe mode.
- `LockFreeRingBuffer` provides sequentially consistent lockless Single-Producer Single-Consumer (SPSC) FIFO queues with acquire-release memory fences.
