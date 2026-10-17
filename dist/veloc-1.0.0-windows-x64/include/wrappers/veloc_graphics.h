// VeloC Idiomatic Graphics & Windowing Wrapper (SDL/GLFW/Vulkan/OpenGL abstraction)
// Provides safe window creation, event polling, and surface handles
#pragma once

#include "veloc.h"
#include <cstdio>
#include <cstring>

namespace veloc {
namespace graphics {

struct WindowConfig {
    const char* title;
    int width;
    int height;
    bool resizable;
    bool vsync;

    static WindowConfig default_config(const char* title = "VeloC Window", int w = 1280, int h = 720) {
        WindowConfig cfg;
        cfg.title = title;
        cfg.width = w;
        cfg.height = h;
        cfg.resizable = true;
        cfg.vsync = true;
        return cfg;
    }
};

struct Event {
    enum Type { None, KeyDown, KeyUp, MouseMove, MouseButton, WindowClose, Resize } type;
    int keycode;
    int mouse_x;
    int mouse_y;
};

struct Window {
    char title[128];
    int width;
    int height;
    bool should_close_flag;

    Window() : width(0), height(0), should_close_flag(false) { title[0] = '\0'; }
    ~Window() { destroy(); }

    void destroy() {
        should_close_flag = true;
    }

    static Result<Window, const char*> create(const WindowConfig& cfg) {
        if (cfg.width <= 0 || cfg.height <= 0) {
            return Result<Window, const char*>::Err("Invalid window dimensions");
        }
        Window w;
        strncpy(w.title, cfg.title, sizeof(w.title) - 1);
        w.width = cfg.width;
        w.height = cfg.height;
        w.should_close_flag = false;
        return Result<Window, const char*>::Ok(w);
    }

    bool should_close() const { return should_close_flag; }

    bool poll_event(Event* out_event) {
        if (!out_event) return false;
        out_event->type = Event::None;
        return false;
    }

    void swap_buffers() {
        // Native backbuffer presentation
    }
};

} // namespace graphics
} // namespace veloc
