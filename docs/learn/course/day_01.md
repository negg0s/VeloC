# Day 1: Hello World and Console Output

## Goal
Write your first VeloC program that outputs formatted text to stdout.

## Theory
In VeloC, execution starts in `int main()` or `fn main() -> i32`. Output is performed via `printf(...)` or `println(...)`.

## Starter Code
```veloc
fn main() -> i32 {
    printf("Hello, VeloC!
");
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 1
veloc learn check
```

## Hint
> [!TIP]
> Use printf("Hello, VeloC!\n"); and make sure to return 0.
