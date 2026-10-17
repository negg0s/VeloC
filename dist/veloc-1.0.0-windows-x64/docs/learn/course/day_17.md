# Day 17: SIMD Intrinsics Basics: 256-bit Vector Lanes

## Goal
Load and broadcast a float into an 8-lane AVX2 vector.

## Theory
The `f32x8` type wraps an AVX2 256-bit register containing eight 32-bit floats.

## Starter Code
```veloc
fn main() -> i32 {
    f32x8 vec = f32x8_set1(5.0f);
    f32 out[8];
    f32x8_store(out, vec);
    printf("Lanes: %.1f %.1f\n", out[0], out[7]);
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 17
veloc learn check
```

## Hint
> [!TIP]
> Broadcast 5.0f across all lanes with f32x8_set1.
