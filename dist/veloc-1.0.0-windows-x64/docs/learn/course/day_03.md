# Day 3: Arithmetic Operations and Type Casting

## Goal
Perform scalar arithmetic and explicit type casting using `as`.

## Theory
VeloC avoids implicit narrowing or lossy promotions. Use `x as f32` to cast explicitly.

## Starter Code
```veloc
fn main() -> i32 {
    let int_val: i32 = 7;
    let float_val: f32 = 2.0;
    let ratio: f32 = (int_val as f32) / float_val;
    printf("Ratio: %.2f\n", ratio);
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 3
veloc learn check
```

## Hint
> [!TIP]
> Cast `int_val as f32` before dividing by `float_val`.
