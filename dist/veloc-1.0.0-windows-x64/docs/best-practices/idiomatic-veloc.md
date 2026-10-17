# Best Practices: Idiomatic VeloC

Follow these foundational rules to write maintainable, blisteringly fast VeloC code.

---

## 1. Value Semantics First, Pointers Second
- Pass small structs (`Vec2`, `Vec3`, `Rect`, `Span`) by value: they fit cleanly in CPU registers (`XMM` / general purpose).
- Use pointers (`T*` or `&T`) only when mutating in-place or passing large datasets.

## 2. Think in Data Layouts: Structure-of-Arrays (SoA)
- When managing collections of objects that update simultaneously (particles, game entities, physics rigidbodies, audio samples, dataframe columns), **always prefer SoA over Array-of-Structures (AoS)**.
- Declare them with `soa struct`:
  ```veloc
  soa struct Boid {
      f32 x;
      f32 y;
      f32 vx;
      f32 vy;
  };
  ```
- This guarantees sequential streaming through cache lines without scatter/gather overhead.

## 3. Scope-Bound Memory Lifetimes
- Avoid heap allocations in loops.
- Use a **Frame Arena** for all temporary data created during a single game frame, web request, or CLI command execution:
  ```veloc
  VeloC_Arena frame_arena = VeloC_Arena::create(4 * 1024 * 1024);
  defer frame_arena.destroy();

  while (game_running) {
      frame_arena.reset();
      // Allocate temporary buffers freely from frame_arena
  }
  ```

## 4. Explicit Errors, No Silent Failures
- Return `Result<T, const char*>` instead of error sentinel values like `-1` or `NULL`.
- Use the `?` try operator to bubble up errors to the callsite cleanly.
