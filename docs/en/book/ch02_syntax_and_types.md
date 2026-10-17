# Chapter 2: Syntax and Type System

VeloC combines concise expression-based syntax with strong static typing.

## Primitive Types
- Integers: `i8`, `i16`, `i32`, `i64`, `u8`, `u16`, `u32`, `u64`, `usize`
- Floats: `f32`, `f64`
- Booleans: `bool` (`true`, `false`)
- Slices: `Span<T>` and `Slice<T>`

## Functions & Control Flow
```veloc
fn fib(n: i32) -> i32 {
    if n <= 1 {
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}

fn main() -> i32 {
    let res = fib(10);
    printf("Fib(10) = %d\n", res);
    return 0;
}
```
