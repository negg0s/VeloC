# Day 26: Lock-Free SPSC Ring Buffer

## Goal
Pass data between a producer and consumer without mutex locks.

## Theory
Atomic acquire/release semantics ensure zero-wait thread coordination.

## Starter Code
```veloc
fn main() -> i32 {
    int cap = 1024;
    int mask = cap - 1;
    int index = 1025;
    printf("Slot: %d\n", index & mask);
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 26
veloc learn check
```

## Hint
> [!TIP]
> 1025 & 1023 is 1.
