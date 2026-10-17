# Day 10: Error Handling with Result and Option

## Goal
Safely propagate errors with Option/Result patterns.

## Theory
Instead of throwing exceptions, VeloC returns structured `Result` or `Option`.

## Starter Code
```veloc
fn safe_divide(a: i32, b: i32) -> i32 {
    if b == 0 {
        return -1; // Sentinel error
    }
    return a / b;
}

fn main() -> i32 {
    let res = safe_divide(100, 5);
    printf("Div: %d\n", res);
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 10
veloc learn check
```

## Hint
> [!TIP]
> Check if divisor is 0, otherwise compute division.
