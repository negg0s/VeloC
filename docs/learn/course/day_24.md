# Day 24: Floating-Point Safety & Accuracy Contracts

## Goal
Inspect NaN/Inf propagation and test math accuracy contracts.

## Theory
Strict IEEE-754 mode guarantees that NaNs and infinities are never elided by fast-math.

## Starter Code
```veloc
fn main() -> i32 {
    f32 inf_val = 1.0f / 0.0f;
    printf("Is Inf: %d\n", isinf(inf_val) ? 1 : 0);
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 24
veloc learn check
```

## Hint
> [!TIP]
> 1.0f / 0.0f results in infinity.
