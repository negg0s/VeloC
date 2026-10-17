# Day 9: Enums and Pattern Matching

## Goal
Define an enum and evaluate cases with `match`.

## Theory
Enums in VeloC group discrete variants. `match` ensures clear dispatch.

## Starter Code
```veloc
enum Status {
    Ok = 0,
    Warn = 1,
    Fail = 2,
};

fn evaluate(s: Status) -> i32 {
    switch (s) {
        case Ok: return 200;
        case Warn: return 300;
        case Fail: return 500;
    }
    return 0;
}

fn main() -> i32 {
    printf("Code: %d\n", evaluate(Ok));
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 9
veloc learn check
```

## Hint
> [!TIP]
> Return 200 for Ok, 300 for Warn, 500 for Fail.
