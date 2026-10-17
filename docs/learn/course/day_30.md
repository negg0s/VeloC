# Day 30: Capstone: Real-Time Particle Physics Step

## Goal
Integrate SoA, SIMD, Arena allocation, and defer into a production kernel.

## Theory
You have mastered systems programming with VeloC!

## Starter Code
```veloc
soa struct Particle {
    f32 x;
    f32 y;
    f32 vx;
    f32 vy;
};

fn main() -> i32 {
    Particle_SoA p = Particle_SoA::create(100);
    defer p.destroy();
    p.push(0.0f, 0.0f, 10.0f, 5.0f);
    p.x[0] += p.vx[0] * 0.1f;
    printf("Updated Pos: %.1f\n", p.x[0]);
    return 0;
}
```

## How to Test
Run in your terminal:
```bash
veloc learn start 30
veloc learn check
```

## Hint
> [!TIP]
> 0.0 + 10.0 * 0.1 = 1.0.
