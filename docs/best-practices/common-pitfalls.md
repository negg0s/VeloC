# Best Practices: Common Beginner Pitfalls

Based on real errors observed in VeloC-Eval benchmark tasks and test cases, here are the top mistakes beginners make and how to avoid them.

---

## Pitfall 1: Mutating an Immutable `let` Binding
```veloc
// WRONG:
let counter = 0;
counter += 1; // Compiler Error E0005: Variable is immutable!

// CORRECT:
let mut counter = 0;
counter += 1;
```

## Pitfall 2: Direct Floating-Point Equality Comparison
```veloc
// WRONG: Triggers Linter Rule FP-001
if (current_time == 1.0f) { ... }

// CORRECT:
if (fabsf(current_time - 1.0f) < 1e-6f) { ... }
```

## Pitfall 3: Returning Pointers to Local Stack Memory
```veloc
// WRONG: Compiler Error E0011 (Dangling pointer)
fn get_buffer() -> i32* {
    i32 local_data[10];
    return local_data; // Memory will be corrupted once function returns!
}

// CORRECT:
fn get_buffer(arena: VeloC_Arena*) -> i32* {
    return arena->alloc_array<i32>(10);
}
```

## Pitfall 4: Forgetting the Scalar Tail in SIMD Loops
```veloc
// WRONG: Crashes or misses elements if array length is not multiple of 8
for (usize i = 0; i < count; i += 8) {
    f32x8 v = f32x8_load(&arr[i]); // Buffer overrun on last iteration!
}

// CORRECT: Always split into 8-element chunks + scalar tail loop
usize i = 0;
for (; i + 8 <= count; i += 8) {
    f32x8 v = f32x8_load(&arr[i]);
    // SIMD work
}
for (; i < count; i++) {
    // Scalar remainder
}
```

## Pitfall 5: Unchecked Division by Zero
```veloc
// WRONG: Triggers Linter Warning FP-003
let ratio = a / b;

// CORRECT:
let ratio = (b != 0) ? (a / b) : 0;
```
