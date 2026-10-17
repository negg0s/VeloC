# Day 5: Iteration: For and While Loops

## Goal
Calculate the sum of integers from 1 to N using a loop.

## Theory
`for` loops and `while` loops allow deterministic iteration. Semicolons separate loop parts.

## Starter Code
```veloc
fn sum_to_n(n: i32) -> i32 {
    let mut total: i32 = 0;
    for (int i = 1; i <= n; i++) {
        total += i;
    }
    return total;
}

fn main() -> i32 {
    printf("Sum: %d\n", sum_to_n(10));
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 5
veloc learn check
```

## Hint
> [!TIP]
> Iterate `i` from 1 to `n` and accumulate into `total`.
