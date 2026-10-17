# Day 18: Fused Multiply-Add (FMA) in SIMD

## Goal
Perform $a 	imes b + c$ across 8 lanes simultaneously.

## Theory
FMA executes multiplication and addition in a single hardware cycle with zero intermediate rounding.

## Starter Code
```veloc
fn main() -> i32 {
    f32 a[8] = {1, 2, 3, 4, 5, 6, 7, 8};
    f32 b[8] = {2, 2, 2, 2, 2, 2, 2, 2};
    f32 c[8] = {10, 10, 10, 10, 10, 10, 10, 10};
    f32 out[8];
    for (int i = 0; i < 8; i++) {
        out[i] = a[i] * b[i] + c[i];
    }
    printf("FMA[0]: %.1f, FMA[7]: %.1f\n", out[0], out[7]);
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 18
veloc learn check
```

## Hint
> [!TIP]
> 1*2 + 10 = 12, 8*2 + 10 = 26.
