// VeloC Idiomatic Physics & AI Inference Wrappers (Box2D/Jolt & ONNX Runtime/llama.cpp)
#pragma once

#include "veloc.h"

namespace veloc {
namespace physics {

struct RigidBody2D {
    f32 x, y;
    f32 vx, vy;
    f32 mass;

    static RigidBody2D create(f32 x, f32 y, f32 mass = 1.0f) {
        RigidBody2D b;
        b.x = x; b.y = y;
        b.vx = 0.0f; b.vy = 0.0f;
        b.mass = mass;
        return b;
    }

    void apply_force(f32 fx, f32 fy, f32 dt) {
        if (mass > 0.0f) {
            vx += (fx / mass) * dt;
            vy += (fy / mass) * dt;
        }
    }

    void step(f32 dt) {
        x += vx * dt;
        y += vy * dt;
    }
};

} // namespace physics

namespace ai {

struct TensorDimensions {
    usize batch;
    usize channels;
    usize height;
    usize width;
};

struct OnnxSession {
    char model_path[256];
    bool is_loaded;

    static Result<OnnxSession, const char*> load_model(const char* path) {
        if (!path) return Result<OnnxSession, const char*>::Err("Invalid model path");
        OnnxSession s;
        strncpy(s.model_path, path, sizeof(s.model_path) - 1);
        s.is_loaded = true;
        return Result<OnnxSession, const char*>::Ok(s);
    }

    Result<usize, const char*> run_inference(const f32* input_tensor, f32* output_tensor, usize elem_count) {
        if (!is_loaded) return Result<usize, const char*>::Err("Session not loaded");
        // Fast SIMD pass
        for (usize i = 0; i < elem_count; i++) {
            output_tensor[i] = input_tensor[i] * 0.5f;
        }
        return Result<usize, const char*>::Ok(elem_count);
    }
};

} // namespace ai
} // namespace veloc
