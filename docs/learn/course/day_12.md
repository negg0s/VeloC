# Day 12: Structs and Layout Control

## Goal
Define a 2D Vector struct with an in-place add method.

## Theory
Structs in VeloC have predictable byte layout without hidden compiler padding or RTTI.

## Starter Code
```veloc
struct Vec2 {
    f32 x;
    f32 y;

    void add(Vec2 other) {
        x += other.x;
        y += other.y;
    }
};

fn main() -> i32 {
    let mut v = Vec2 { 1.0f, 2.0f };
    v.add(Vec2 { 3.0f, 4.0f });
    printf("Vec: %.1f %.1f\n", v.x, v.y);
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 12
veloc learn check
```

## Hint
> [!TIP]
> Accumulate other.x into x and other.y into y.
