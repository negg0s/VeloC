# Day 22: SmallVec Stack Optimization

## Goal
Store small collections entirely on the stack to prevent heap allocations.

## Theory
SmallVec reserves an inline buffer. It only spills to the heap if capacity is exceeded.

## Starter Code
```veloc
fn main() -> i32 {
    int inline_arr[4] = {1, 2, 3, 4};
    printf("Inline count: 4, item[3]: %d\n", inline_arr[3]);
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 22
veloc learn check
```

## Hint
> [!TIP]
> Access element at index 3.
