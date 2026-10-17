# Day 16: Structure-of-Arrays (SoA) for SIMD Alignment

## Goal
Create and populate an SoA collection for entity data.

## Theory
`soa struct` automatically decomposes fields into separate contiguous arrays.

## Starter Code
```veloc
soa struct Unit {
    f32 x;
    f32 y;
};

fn main() -> i32 {
    Unit_SoA units = Unit_SoA::create(10);
    defer units.destroy();
    units.push(10.0f, 20.0f);
    printf("Unit 0: %.1f %.1f\n", units.x[0], units.y[0]);
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 16
veloc learn check
```

## Hint
> [!TIP]
> Create Unit_SoA, push coordinates, and read x[0] and y[0].
