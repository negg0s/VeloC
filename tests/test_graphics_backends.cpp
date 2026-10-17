// Test VeloC Multi-Backend Graphics Abstraction
#include "wrappers/veloc_graphics.h"
#include <cassert>
#include <cstdio>

int main() {
    using namespace veloc::graphics;

    printf("[*] Testing VeloC Multi-Backend Graphics System...\n");

    // 1. Test DirectX 12
    auto dx12_cfg = WindowConfig::default_config("DirectX12 App", 1920, 1080);
    dx12_cfg.preferred_backend = GfxBackend::DirectX12;
    auto w_dx12 = Window::create(dx12_cfg);
    assert(w_dx12.is_ok());
    assert(w_dx12.unwrap().device.backend == GfxBackend::DirectX12);
    printf("  [PASS] DirectX 12 Device: %s\n", w_dx12.unwrap().device.adapter_name);

    // 2. Test Vulkan
    auto vk_cfg = WindowConfig::default_config("Vulkan App", 1280, 720);
    vk_cfg.preferred_backend = GfxBackend::Vulkan;
    auto w_vk = Window::create(vk_cfg);
    assert(w_vk.is_ok());
    assert(w_vk.unwrap().device.backend == GfxBackend::Vulkan);
    printf("  [PASS] Vulkan 1.3 Device: %s\n", w_vk.unwrap().device.adapter_name);

    // 3. Test Software Rasterizer fallback
    auto sw_cfg = WindowConfig::default_config("Headless App", 640, 480);
    sw_cfg.preferred_backend = GfxBackend::Software;
    auto w_sw = Window::create(sw_cfg);
    assert(w_sw.is_ok());
    assert(w_sw.unwrap().device.backend == GfxBackend::Software);
    printf("  [PASS] Software Fallback: %s\n", w_sw.unwrap().device.adapter_name);

    printf("[SUCCESS] All graphics backends validated successfully!\n");
    return 0;
}
