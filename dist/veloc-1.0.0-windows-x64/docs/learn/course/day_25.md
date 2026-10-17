# Day 25: Work-Stealing and Parallel Scheduling

## Goal
Distribute work items evenly across worker threads.

## Theory
Work-stealing dequeues idle workers steal tasks from the tails of busy workers.

## Starter Code
```veloc
fn main() -> i32 {
    int tasks = 64;
    int threads = 4;
    printf("Tasks per thread: %d\n", tasks / threads);
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 25
veloc learn check
```

## Hint
> [!TIP]
> 64 / 4 = 16 tasks per worker.
