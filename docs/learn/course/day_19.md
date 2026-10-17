# Day 19: SIMD Tail Handling and Alignment

## Goal
Process buffers whose size is not a multiple of 8 without overrun.

## Theory
Vector algorithms process full 8-lane chunks, then handle the remainder with scalar logic.

## Starter Code
```veloc
fn main() -> i32 {
    int count = 11;
    int simd_chunks = count / 8;
    int tail_rem = count % 8;
    printf("Chunks: %d, Tail: %d\n", simd_chunks, tail_rem);
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 19
veloc learn check
```

## Hint
> [!TIP]
> 11 divided by 8 is 1 chunk with 3 tail elements.
