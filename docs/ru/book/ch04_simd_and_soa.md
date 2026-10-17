# Глава 4: Векторизация SIMD и SoA структуры

Размещение Structure of Arrays (SoA) позволяет векторизовать обработку компонентов сущностей без штрафов scatter/gather.

## Объявление SoA
```veloc
soa struct Particle {
    f32 x;
    f32 y;
    f32 z;
};

int main() {
    Particle_SoA parts = Particle_SoA::create(100);
    parts.push(1.0f, 2.0f, 3.0f);
    printf("Количество частиц: %d\n", (int)parts.count);
    parts.destroy();
    return 0;
}
```
