# Day 29: Benchmarking and Roofline Analysis

## Goal
Measure CPU cycles and elapsed milliseconds with VeloC_Timer.

## Theory
Precise timing requires warmup, hardware cycle measurement, and statistical medians.

## Starter Code
```veloc
fn main() -> i32 {
    VeloC_Timer timer;
    timer.start();
    f64 ms = timer.elapsed_ms();
    printf("Timer ok: %d\n", ms >= 0.0 ? 1 : 0);
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 29
veloc learn check
```

## Hint
> [!TIP]
> Verify elapsed_ms() returns >= 0.0.
