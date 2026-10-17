# Chapter 4: SIMD and SoA Layouts

Structure of Arrays (SoA) layout enables AVX2 vectorization across entity components without scatter-gather penalties.

## SoA Declaration
```veloc
soa struct Particle {
    f32 x;
    f32 y;
    f32 z;
};

int main() {
    Particle_SoA parts = Particle_SoA::create(100);
    parts.push(1.0f, 2.0f, 3.0f);
    printf("SoA count: %d\n", (int)parts.count);
    parts.destroy();
    return 0;
}
```
