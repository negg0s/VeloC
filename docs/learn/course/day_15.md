# Day 15: TrackingAllocator and Leak Telemetry

## Goal
Verify memory allocation counts and peak usage tracking.

## Theory
Tracking allocators record allocated bytes and detect unreleased resources before exit.

## Starter Code
```veloc
fn main() -> i32 {
    usize total_bytes = 1024;
    printf("Tracking Alloc: %llu bytes\n", (unsigned long long)total_bytes);
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 15
veloc learn check
```

## Hint
> [!TIP]
> Format total_bytes with %llu.
