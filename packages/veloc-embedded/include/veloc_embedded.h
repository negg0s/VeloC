#ifndef VELOC_EMBEDDED_H
#define VELOC_EMBEDDED_H

#include <veloc.h>
#include <cstdint>
#include <cstdio>
#include <cstring>

namespace veloc {
namespace embedded {

    // ========================================================================
    // 1. Zero-Heap Static Memory Pool (Deterministic O(1) Allocation)
    // ========================================================================
    template <typename T, usize Capacity = 256>
    class StaticPool {
    private:
        alignas(alignof(T)) u8 storage[Capacity * sizeof(T)];
        u32 free_list[Capacity];
        usize free_count;
        bool occupied[Capacity];

    public:
        StaticPool() : free_count(Capacity) {
            for (usize i = 0; i < Capacity; i++) {
                free_list[i] = (u32)(Capacity - 1 - i);
                occupied[i] = false;
            }
        }

        T* allocate() {
            if (free_count == 0) return nullptr;
            u32 idx = free_list[--free_count];
            occupied[idx] = true;
            return reinterpret_cast<T*>(&storage[idx * sizeof(T)]);
        }

        bool deallocate(T* ptr) {
            if (!ptr) return false;
            uintptr_t base = reinterpret_cast<uintptr_t>(storage);
            uintptr_t addr = reinterpret_cast<uintptr_t>(ptr);
            if (addr < base) return false;
            usize offset = addr - base;
            if (offset % sizeof(T) != 0) return false;
            usize idx = offset / sizeof(T);
            if (idx >= Capacity || !occupied[idx]) return false;

            occupied[idx] = false;
            free_list[free_count++] = (u32)idx;
            return true;
        }

        usize available() const { return free_count; }
        usize capacity() const { return Capacity; }
    };

    // ========================================================================
    // 2. Q16.16 Fixed-Point Arithmetic (Zero FPU requirement)
    // ========================================================================
    struct Fixed16 {
        i32 raw;

        static constexpr i32 FRACTION = 16;
        static constexpr i32 ONE = 1 << FRACTION;

        constexpr Fixed16() : raw(0) {}
        constexpr explicit Fixed16(i32 r, bool) : raw(r) {}
        constexpr Fixed16(i32 integer) : raw(integer << FRACTION) {}
        Fixed16(f32 floating) : raw((i32)(floating * (f32)ONE)) {}

        f32 to_float() const { return (f32)raw / (f32)ONE; }
        i32 to_int() const { return raw >> FRACTION; }

        Fixed16 operator+(Fixed16 o) const { return Fixed16(raw + o.raw, true); }
        Fixed16 operator-(Fixed16 o) const { return Fixed16(raw - o.raw, true); }
        Fixed16 operator*(Fixed16 o) const {
            i64 prod = (i64)raw * (i64)o.raw;
            return Fixed16((i32)(prod >> FRACTION), true);
        }
        Fixed16 operator/(Fixed16 o) const {
            i64 div = ((i64)raw << FRACTION) / o.raw;
            return Fixed16((i32)div, true);
        }
    };

    // ========================================================================
    // 3. Hardware / Table-driven CRC32 (IEEE 802.3 standard)
    // ========================================================================
    static u32 crc32(const u8* data, usize len) {
        u32 crc = 0xFFFFFFFF;
        for (usize i = 0; i < len; i++) {
            u8 byte = data[i];
            crc ^= byte;
            for (u8 j = 0; j < 8; j++) {
                u32 mask = -(crc & 1);
                crc = (crc >> 1) ^ (0xEDB88320 & mask);
            }
        }
        return ~crc;
    }

    // ========================================================================
    // 4. Deterministic Finite State Machine (FSM)
    // ========================================================================
    template <typename StateType, typename EventType, usize MaxTransitions = 64>
    class FSM {
    public:
        struct Transition {
            StateType from_state;
            EventType event;
            StateType to_state;
        };

    private:
        StateType current;
        Transition transitions[MaxTransitions];
        usize count;

    public:
        FSM(StateType initial) : current(initial), count(0) {}

        bool add_transition(StateType from, EventType ev, StateType to) {
            if (count >= MaxTransitions) return false;
            transitions[count++] = Transition{from, ev, to};
            return true;
        }

        bool handle_event(EventType ev) {
            for (usize i = 0; i < count; i++) {
                if (transitions[i].from_state == current && transitions[i].event == ev) {
                    current = transitions[i].to_state;
                    return true;
                }
            }
            return false;
        }

        StateType state() const { return current; }
    };

} // namespace embedded
} // namespace veloc

#endif // VELOC_EMBEDDED_H
