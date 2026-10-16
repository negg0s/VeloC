#include "D:/VeloC/include/veloc.h"

// [VeloC module declaration]

// Auto-generated VeloC Struct-of-Arrays (SoA) for SIMD acceleration
struct Hero_SoA {
    usize capacity;
    usize count;
    f32* VELOC_RESTRICT hp;
    f32* VELOC_RESTRICT mana;
    f32* VELOC_RESTRICT armor;
    f32* VELOC_RESTRICT speed;

    static Hero_SoA create(usize cap) {
        Hero_SoA s;
        s.capacity = cap;
        s.count = 0;
        s.hp = (f32*)veloc_aligned_alloc(32, sizeof(f32) * cap);
        s.mana = (f32*)veloc_aligned_alloc(32, sizeof(f32) * cap);
        s.armor = (f32*)veloc_aligned_alloc(32, sizeof(f32) * cap);
        s.speed = (f32*)veloc_aligned_alloc(32, sizeof(f32) * cap);
        return s;
    }

    VELOC_INLINE void push(f32 val_hp, f32 val_mana, f32 val_armor, f32 val_speed) {
        if (count < capacity) {
            this->hp[count] = val_hp;
            this->mana[count] = val_mana;
            this->armor[count] = val_armor;
            this->speed[count] = val_speed;
            count++;
        }
    }

    void destroy() {
        if (hp) { veloc_aligned_free(hp); hp = NULL; }
        if (mana) { veloc_aligned_free(mana); mana = NULL; }
        if (armor) { veloc_aligned_free(armor); armor = NULL; }
        if (speed) { veloc_aligned_free(speed); speed = NULL; }
        capacity = 0;
        count = 0;
    }

    // Auto-generated Reflection: to_json()
    std::string to_json(usize i) const {
        if (i >= count) return "{}";
        std::ostringstream ss;
        ss << "{";
        ss << "\"hp\": " << this->hp[i] << ", ";
        ss << "\"mana\": " << this->mana[i] << ", ";
        ss << "\"armor\": " << this->armor[i] << ", ";
        ss << "\"speed\": " << this->speed[i] << "";
        ss << "}";
        return ss.str();
    }

    static const char* type_name() { return "Hero_SoA"; }
    static usize field_count() { return 4; }
};


auto main() -> i32 {
    printf("%s\n", (::veloc::to_str(VELOC_CYAN) + std::string("==================================================") + ::veloc::to_str(VELOC_RESET)).c_str());
    printf("%s\n", (::veloc::to_str(VELOC_BOLD) + std::string("   VeloC 4.0: Reflection, 3D SIMD & Memory Tracking") + ::veloc::to_str(VELOC_RESET)).c_str());
    printf("%s\n", (::veloc::to_str(VELOC_CYAN) + std::string("==================================================") + ::veloc::to_str(VELOC_RESET)).c_str());

    // 1. Built-in Compile-Time Reflection & JSON (Top Reddit (Request).unwrap())
    printf("%s\n", (::veloc::to_str(VELOC_YELLOW) + std::string("[1] Compile-Time Reflection & Auto-JSON") + ::veloc::to_str(VELOC_RESET)).c_str());
    auto heroes = Hero_SoA::create(10);
    auto _veloc_defer_1 = ::veloc::ScopeGuardHelper() + [&]() { heroes.destroy(); };

    heroes.push(100.0f, 50.0f, 15.0f, 7.5f);
    heroes.push(250.0f, 10.0f, 40.0f, 5.0f);

    printf("%s\n", (std::string("  Type Name:    ") + ::veloc::to_str(Hero_SoA::type_name())).c_str());
    printf("%s\n", (std::string("  Field Count:  ") + ::veloc::to_str(Hero_SoA::field_count()) + std::string(" fields")).c_str());
    printf("%s\n", (std::string("  Hero 0 JSON:  ") + ::veloc::to_str(heroes.to_json(0))).c_str());
    printf("%s\n", (std::string("  Hero 1 JSON:  ") + ::veloc::to_str(heroes.to_json(1))).c_str());

    // 2. Hardware 3D Vector Math (SIMD Vec3)
    printf("%s\n", (::veloc::to_str(VELOC_YELLOW) + std::string("[2] 128-bit SIMD 3D Vector Math (Vec3)") + ::veloc::to_str(VELOC_RESET)).c_str());
    const auto v1 = Vec3(1.0f, 2.0f, 3.0f);
    const auto v2 = Vec3(4.0f, 5.0f, 6.0f);

    const auto v_add = v1 + v2;
    const auto v_sub = v2 - v1;
    const auto v_dot = v1.dot(v2);
    const auto v_cross = v1.cross(v2);
    const auto v_norm = v1.normalized();

    printf("%s\n", (std::string("  v1 + v2:      (") + ::veloc::to_str(v_add.x) + std::string(", ") + ::veloc::to_str(v_add.y) + std::string(", ") + ::veloc::to_str(v_add.z) + std::string(")")).c_str());
    printf("%s\n", (std::string("  v2 - v1:      (") + ::veloc::to_str(v_sub.x) + std::string(", ") + ::veloc::to_str(v_sub.y) + std::string(", ") + ::veloc::to_str(v_sub.z) + std::string(")")).c_str());
    printf("%s\n", (std::string("  Dot product:  ") + ::veloc::to_str(v_dot)).c_str());
    printf("%s\n", (std::string("  Cross prod:   (") + ::veloc::to_str(v_cross.x) + std::string(", ") + ::veloc::to_str(v_cross.y) + std::string(", ") + ::veloc::to_str(v_cross.z) + std::string(")")).c_str());
    printf("%s\n", (std::string("  v1 Normalized:(") + ::veloc::to_str(v_norm.x) + std::string(", ") + ::veloc::to_str(v_norm.y) + std::string(", ") + ::veloc::to_str(v_norm.z) + std::string(") [length = ") + ::veloc::to_str(v_norm.length()) + std::string("]")).c_str());

    // 3. Memory Profiler & Tracking
    printf("%s\n", (::veloc::to_str(VELOC_YELLOW) + std::string("[3] Built-in Memory Telemetry Tracker") + ::veloc::to_str(VELOC_RESET)).c_str());
    veloc::MemoryTracker::record_alloc(1024 * 64); // 64 KB
    veloc::MemoryTracker::record_alloc(1024 * 128); // 128 KB
    veloc::MemoryTracker::print_report();
    veloc::MemoryTracker::record_free(1024 * 64);
    veloc::MemoryTracker::print_report();

    printf("%s\n", (::veloc::to_str(VELOC_GREEN) + std::string("[SUCCESS] All VeloC 4.0 features operational!") + ::veloc::to_str(VELOC_RESET)).c_str());
    printf("%s\n", (::veloc::to_str(VELOC_CYAN) + std::string("==================================================") + ::veloc::to_str(VELOC_RESET)).c_str());

    return 0;
}