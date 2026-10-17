# Day 20: Zero-Copy String Slices

## Goal
Inspect string length and substrings without heap allocations.

## Theory
`const char*` and string spans reference existing memory without `malloc`.

## Starter Code
```veloc
fn main() -> i32 {
    const char* str = "VeloC Systems";
    printf("Len: %d\n", (int)strlen(str));
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 20
veloc learn check
```

## Hint
> [!TIP]
> strlen("VeloC Systems") is 13.
