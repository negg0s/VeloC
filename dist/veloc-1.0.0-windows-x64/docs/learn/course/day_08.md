# Day 8: References and Pointers

## Goal
Pass variables by pointer/reference to mutate in-place.

## Theory
Use `&val` to pass an address, or reference syntax to modify values without copying.

## Starter Code
```veloc
fn swap_vals(a: i32*, b: i32*) {
    let temp = *a;
    *a = *b;
    *b = temp;
}

fn main() -> i32 {
    let mut x: i32 = 1;
    let mut y: i32 = 2;
    swap_vals(&x, &y);
    printf("Swapped: %d %d\n", x, y);
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 8
veloc learn check
```

## Hint
> [!TIP]
> Use a temporary variable to hold `*a`, then assign `*a = *b` and `*b = temp`.
