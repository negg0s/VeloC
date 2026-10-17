# Day 4: Branching and Expressions

## Goal
Use if/else conditional expressions to determine maximum values.

## Theory
In VeloC, `if`/`else` blocks are expressions that can return values.

## Starter Code
```veloc
fn max_val(a: i32, b: i32) -> i32 {
    if a > b {
        return a;
    } else {
        return b;
    }
}

fn main() -> i32 {
    printf("Max: %d\n", max_val(42, 17));
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 4
veloc learn check
```

## Hint
> [!TIP]
> Compare `a > b` and return the larger value.
