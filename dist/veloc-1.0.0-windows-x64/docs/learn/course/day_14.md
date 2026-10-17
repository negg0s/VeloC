# Day 14: FixedPool Allocation Without Fragmentation

## Goal
Manage fixed-size nodes with deterministic $O(1)$ allocation.

## Theory
Fixed pools avoid OS heap lock contention and prevent fragmentation.

## Starter Code
```veloc
struct Node {
    i32 val;
};

fn main() -> i32 {
    VeloC_Arena pool = VeloC_Arena::create(4096);
    defer pool.destroy();
    Node* n = (Node*)pool.alloc(sizeof(Node));
    n->val = 999;
    printf("Pool Node: %d\n", n->val);
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 14
veloc learn check
```

## Hint
> [!TIP]
> Assign 999 to n->val.
