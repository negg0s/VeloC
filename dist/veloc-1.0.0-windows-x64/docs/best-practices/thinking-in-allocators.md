# Best Practices: Thinking in Allocators

Systems programming in VeloC is defined by **allocator awareness**. Instead of delegating memory to a generic OS heap allocator (`malloc` / `free`), choose the right memory arena for the lifetime of your data.

---

## The Four Primary Lifetime Categories

```
+------------------------------------------------------------------------+
| 1. Frame / Temporary Lifetime (Ticks, Requests, Transient Passes)      |
|    -> Tool: VeloC_Arena (Bump Allocator)                               |
|    -> Cost: O(1) alloc, O(1) batch deallocation                       |
+------------------------------------------------------------------------+
| 2. Uniform Objects (Entities, Bullets, Nodes, Grid Cells)              |
|    -> Tool: FixedPool<T, N> (Free-list Chunk Allocator)                |
|    -> Cost: O(1) alloc, O(1) free, 0 fragmentation                     |
+------------------------------------------------------------------------+
| 3. Small Local Collections (Argument lists, temporary string buffers)  |
|    -> Tool: SmallVec<T, N> / Span<T>                                   |
|    -> Cost: Zero allocations (resides on CPU stack)                    |
+------------------------------------------------------------------------+
| 4. Long-Lived Engine State (Textures, World Map, Loaded Databases)     |
|    -> Tool: TrackingAllocator (OS Heap + Leak Telemetry)               |
|    -> Cost: Monitored real-time against memory budgets                 |
+------------------------------------------------------------------------+
```

---

## Practical Rules of Thumb

1. **Never allocate inside inner loops**:
   - If a function is called thousands of times per second, pass an arena pointer `arena: VeloC_Arena*` into the function instead of having it allocate memory itself.
2. **Batch resets over piecemeal destruction**:
   - Calling `free()` 50,000 times invalidates CPU caches and spends milliseconds in lock synchronization.
   - Calling `arena.reset()` rewinds an integer offset to `0` in a single CPU instruction (< 1 nanosecond).
3. **Use Markers for Sub-Tasks**:
   - `usize marker = arena.get_marker();`
   - Run sub-task, then `arena.reset_to_marker(marker);`.
   - Reclaims only the memory allocated by the sub-task.
