# Day 11: Zero-Cost Defer and Scope Guards

## Goal
Guarantee resource cleanup at scope exit using `defer`.

## Theory
`defer stmt;` executes `stmt` when exiting the enclosing lexical block in reverse declaration order.

## Starter Code
```veloc
fn main() -> i32 {
    printf("Start\n");
    defer printf("Cleanup\n");
    printf("Work\n");
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 11
veloc learn check
```

## Hint
> [!TIP]
> defer runs upon scope exit, after 'Work'.
