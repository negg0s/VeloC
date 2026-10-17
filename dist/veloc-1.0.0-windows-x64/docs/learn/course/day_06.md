# Day 6: Pure Functions and Tail Expressions

## Goal
Implement a recursive factorial function with base cases.

## Theory
Functions are declared with `fn name(param: Type) -> RetType`. Early returns prevent deep nesting.

## Starter Code
```veloc
fn factorial(n: i32) -> i32 {
    if n <= 1 {
        return 1;
    }
    return n * factorial(n - 1);
}

fn main() -> i32 {
    printf("Fact: %d\n", factorial(5));
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 6
veloc learn check
```

## Hint
> [!TIP]
> When n <= 1, return 1. Otherwise return n * factorial(n - 1).
