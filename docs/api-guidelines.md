# VeloC API Design Guidelines & Best Practices

This document outlines the official API conventions, memory management patterns, and naming guidelines for the VeloC language ecosystem.

---

## 1. Naming Conventions

| Language Construct | Style | Example | Notes |
| :--- | :--- | :--- | :--- |
| **Types, Structs, Classes** | `PascalCase` | `PieceTable`, `TransformerModel` | Nouns or noun phrases |
| **Traits / Interfaces** | `PascalCase` | `Serialize`, `Drawable`, `Iterator` | Adjectives or capability nouns |
| **Functions / Methods** | `snake_case` | `compute_lighting`, `append_log` | Verbs or verb phrases |
| **Variables / Fields** | `snake_case` | `total_visible`, `chunk_size` | Descriptive names, avoid single letters except loop index |
| **Constants / Enums** | `SCREAMING_SNAKE_CASE` | `MAX_CAPACITY`, `OP_CONST` | Constants and enum variants |
| **Modules / Namespaces** | `PascalCase` | `VelocDb`, `VelocSync` | Explicit namespace encapsulation |

### 1.1 Platform Header Collision Avoidance
When designing enums that may interoperate with C libraries or the Windows SDK (e.g. `windows.h`, `winnt.h`), avoid generic names like `TokenType`, `Handle`, `Status`, `Process`, or `Thread`. Always prefix enum types with the domain name:
```veloc
// Recommended:
enum EditTokenType {
    TOKEN_KEYWORD,
    TOKEN_IDENTIFIER,
    TOKEN_NUMBER
};

// Avoid:
enum TokenType { ... }; // Collides with winnt.h TokenType
```

---

## 2. Memory & Performance Patterns

### 2.1 Structure of Arrays (SoA) vs Array of Structures (AoS)
For batch operations over large sets of entities ($\ge 1,000$ items) processed in loops:
- **Prefer SoA**: Store components in parallel contiguous vectors (`std::vector<f32> pos_x`, `pos_y`, `pos_z`). This maximizes CPU L1/L2 cache line utilization and allows the compiler to auto-vectorize loops with AVX2/AVX-512.
- **Avoid AoS**: Large structs (`struct Entity { Vec3 pos; Vec3 vel; Mat4 transform; ... }`) cause cache thrashing when only a subset of fields is accessed during a pass.

### 2.2 Allocation Discipline in Inner Loops
- Never allocate or free heap memory (`malloc`, `new`, dynamic vector resizing) inside inner computation loops.
- Pre-allocate buffers upfront using `.reserve()` or reuse scratch buffers across iterations.
- For temporary scratch allocations, use `ArenaAllocator` or stack-based ring buffers.

---

## 3. Error Handling

### 3.1 Prefer `Result<T, E>` and `Option<T>`
- Functions that can fail must return a `Result<T, E>` rather than sentinel error codes (`-1`, `null`).
- Use `Option<T>` for values that may be absent.
- Avoid uncaught panics in library code; reserve `panic()` only for unrecoverable invariant violations.

---

## 4. RAII & Resource Management
- Always use `defer` for cleanup of external resources (file descriptors, sockets, GPU handles).
- Destructors must never throw exceptions or trigger secondary failures.
