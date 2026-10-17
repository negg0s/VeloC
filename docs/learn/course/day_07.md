# Day 7: Slices and Contiguous Buffers

## Goal
Traverse and compute the mean of an array buffer.

## Theory
VeloC arrays and pointers represent contiguous memory without garbage collection overhead.

## Starter Code
```veloc
fn main() -> i32 {
    i32 arr[4] = {10, 20, 30, 40};
    let mut sum: i32 = 0;
    for (int i = 0; i < 4; i++) {
        sum += arr[i];
    }
    printf("Mean: %d\n", sum / 4);
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 7
veloc learn check
```

## Hint
> [!TIP]
> Sum elements and divide by 4.
