# Day 21: High-Performance SwissTable Map

## Goal
Insert and query keys in an open-addressing hash table.

## Theory
SwissTable uses 1-byte metadata SIMD matching to achieve single-digit nanosecond lookups.

## Starter Code
```veloc
fn main() -> i32 {
    int key = 42;
    int val = 1337;
    printf("KV: %d -> %d\n", key, val);
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 21
veloc learn check
```

## Hint
> [!TIP]
> Print key and value.
