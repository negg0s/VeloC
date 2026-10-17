# VeloC Python Extension Generator (pyext)
# Generates zero-copy CPython C-extensions (.pyd) with NumPy buffer protocol support.

import os
import sys
import sysconfig
import subprocess
from pathlib import Path
from typing import Dict, List

ROOT_DIR = Path("D:/VeloC")
CLANG_PATH = Path("C:/Program Files/Windhawk/Compiler/bin/clang++.exe")

class PyExtGenerator:
    def __init__(self, root_dir: Path = ROOT_DIR):
        self.root_dir = root_dir
        self.include_dir = root_dir / "include"
        self.py_include = Path(sysconfig.get_path("include"))
        self.py_lib_dir = Path(sys.base_prefix) / "libs"
        self.py_ver_tag = f"python{sys.version_info.major}{sys.version_info.minor}"

    def generate_wrapper_c(self, module_name: str, kernel_body: str) -> str:
        return f"""// Auto-generated VeloC Python C-Extension: {module_name}
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "veloc.h"

// Vectorized VeloC kernel executing directly on raw buffer
static void veloc_kernel(f32* data, usize count, f32 multiplier) {{
    f32x8 m_vec = _mm256_set1_ps(multiplier);
    usize i = 0;
    for (; i + 8 <= count; i += 8) {{
        f32x8 v = _mm256_loadu_ps(&data[i]);
        _mm256_storeu_ps(&data[i], _mm256_mul_ps(v, m_vec));
    }}
    for (; i < count; i++) {{
        data[i] *= multiplier;
    }}
}}

// Python wrapper supporting NumPy 1D/2D continuous buffer (zero-copy)
static PyObject* py_fast_scale(PyObject* self, PyObject* args) {{
    Py_buffer view;
    float multiplier = 1.0f;

    // "y*f" or "w*f" format accepts any buffer-compatible object (NumPy array, bytearray, etc.)
    if (!PyArg_ParseTuple(args, "w*f", &view, &multiplier)) {{
        return NULL;
    }}

    usize elem_count = view.len / sizeof(float);
    float* raw_ptr = (float*)view.buf;

    // Release Python GIL during native AVX2 SIMD computation!
    Py_BEGIN_ALLOW_THREADS
    veloc_kernel(raw_ptr, elem_count, multiplier);
    Py_END_ALLOW_THREADS

    PyBuffer_Release(&view);
    Py_RETURN_NONE;
}}

static PyMethodDef {module_name}_methods[] = {{
    {{"fast_scale", py_fast_scale, METH_VARARGS, "Zero-copy in-place array scaling via VeloC AVX2 kernel."}},
    {{NULL, NULL, 0, NULL}}
}};

static struct PyModuleDef {module_name}_module = {{
    PyModuleDef_HEAD_INIT,
    "{module_name}",
    "High-performance native VeloC acceleration extension.",
    -1,
    {module_name}_methods
}};

PyMODINIT_FUNC PyInit_{module_name}(void) {{
    return PyModule_Create(&{module_name}_module);
}}
"""

    def build_extension(self, module_name: str, output_pyd: Path) -> bool:
        src_c = output_pyd.parent / f"{module_name}_pyext.cpp"
        wrapper_code = self.generate_wrapper_c(module_name, "")
        src_c.write_text(wrapper_code, encoding="utf-8")

        cmd = [
            str(CLANG_PATH), "-shared", "-target", "x86_64-w64-windows-gnu",
            "-std=c++20", "-O3", "-march=native", "-fwrapv",
            f"-I{self.include_dir}",
            f"-I{self.py_include}",
            f"-L{self.py_lib_dir}",
            f"-l{self.py_ver_tag}",
            str(src_c),
            "-o", str(output_pyd)
        ]
        res = subprocess.run(cmd, cwd=str(self.root_dir), capture_output=True, text=True)
        if res.returncode != 0:
            print(f"[PyExt Build Error]:\n{res.stderr or res.stdout}")
            return False

        print(f"[VeloC PyExt Success] Extension built: {output_pyd}")
        return True

if __name__ == "__main__":
    mod_name = sys.argv[1] if len(sys.argv) > 1 else "veloc_speedup"
    out_path = Path(f"{mod_name}.pyd")
    gen = PyExtGenerator()
    ok = gen.build_extension(mod_name, out_path)
    sys.exit(0 if ok else 1)
