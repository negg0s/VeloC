# Day 23: Deterministic Signed Integer Arithmetic

## Goal
Verify two's complement wrapping with `-fwrapv`.

## Theory
VeloC compiles with `-fwrapv`, guaranteeing that signed overflow wraps predictably without UB.

## Starter Code
```veloc
fn main() -> i32 {
    int max_i32 = 2147483647;
    int wrapped = max_i32 + 1;
    printf("Wrapped: %d\n", wrapped);
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 23
veloc learn check
```

## Hint
> [!TIP]
> Max positive signed 32-bit int wraps to -2147483648.
