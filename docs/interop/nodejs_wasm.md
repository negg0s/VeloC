# Interoperability: Node.js (N-API) and WebAssembly (WASM)

VeloC programs and libraries can be compiled into Node.js native addons (using N-API) or targeted to WebAssembly for browser and edge runtimes.

---

## 1. Node.js N-API Native Addon

Compile VeloC static libraries and wrap them with Node-API:

```c
#include <node_api.h>
#include "veloc.h"

napi_value FastCompute(napi_env env, napi_callback_info info) {
    size_t argc = 1;
    napi_value argv[1];
    napi_get_cb_info(env, info, &argc, argv, NULL, NULL);

    int32_t input_val;
    napi_get_value_int32(env, argv[0], &input_val);

    int32_t result = input_val * 2; // Native VeloC computation

    napi_value res_val;
    napi_create_int32(env, result, &res_val);
    return res_val;
}

napi_value Init(napi_env env, napi_value exports) {
    napi_value fn;
    napi_create_function(env, NULL, 0, FastCompute, NULL, &fn);
    napi_set_named_property(env, exports, "fastCompute", fn);
    return exports;
}

NAPI_MODULE(NODE_GYP_MODULE_NAME, Init)
```

---

## 2. WebAssembly (WASM) Compilation

To compile VeloC to WebAssembly using Emscripten or LLVM `wasm32-unknown-unknown`:
```bash
clang++ -target wasm32 -O3 -nostdlib -Wl,--no-entry -Wl,--export-all src/kernel.cpp -o kernel.wasm
```
*Note*: SIMD instructions on WebAssembly use the 128-bit `wasm_simd128` feature set.
