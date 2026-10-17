# Day 2: Variables, Primitive Types, and Mutability

## Goal
Declare immutable and mutable variables with explicit primitive types.

## Theory
Variables are declared with `let` (immutable) or `let mut` (mutable). Integer types include `i32`, `i64`, `u32`, `u64`. Floats include `f32` and `f64`.

## Starter Code
```veloc
fn main() -> i32 {
    let a: i32 = 10;
    let mut b: i32 = 20;
    b += a;
    printf("Result: %d\n", b);
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 2
veloc learn check
```

## Hint
> [!TIP]
> Ensure `b` is marked mutable using `let mut` so that `b += a` succeeds.
