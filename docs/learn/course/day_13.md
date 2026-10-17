# Day 13: Linear Bump Allocation with VeloC_Arena

## Goal
Allocate an array of 1,000 items from a bump arena and reset it.

## Theory
`VeloC_Arena` provides instantaneous $O(1)$ allocation by bumping an offset pointer.

## Starter Code
```veloc
fn main() -> i32 {
    VeloC_Arena arena = VeloC_Arena::create(1024 * 1024);
    defer arena.destroy();

    i32* arr = arena.alloc_array<i32>(10);
    for (int i = 0; i < 10; i++) {
        arr[i] = i * 2;
    }
    printf("Arena[5]: %d\n", arr[5]);
    arena.reset();
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 13
veloc learn check
```

## Hint
> [!TIP]
> arr[5] will store 5 * 2 = 10.
