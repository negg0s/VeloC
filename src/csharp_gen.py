# VeloC C# / .NET / Unity P/Invoke Binding Generator
# Generates high-performance C# interop bindings from VeloC header exports.

import re
from pathlib import Path
from typing import List, Dict

TYPE_MAP_CS = {
    "void": "void",
    "bool": "bool",
    "i8": "sbyte",
    "u8": "byte",
    "i16": "short",
    "u16": "ushort",
    "i32": "int",
    "u32": "uint",
    "i64": "long",
    "u64": "ulong",
    "f32": "float",
    "f64": "double",
    "usize": "nuint",
    "int": "int",
    "float": "float",
    "double": "double",
    "const char*": "string",
    "char*": "string"
}

class CSharpGen:
    def __init__(self, dll_name: str = "veloc_native"):
        self.dll_name = dll_name

    def generate_cs_class(self, class_name: str, exports: List[Dict]) -> str:
        lines = [
            "// Auto-generated VeloC C# / Unity P/Invoke Interop Layer",
            "using System;",
            "using System.Runtime.InteropServices;",
            "",
            "namespace VeloC.Interop",
            "{",
            f"    public static class {class_name}",
            "    {",
            f'        private const string LibraryName = "{self.dll_name}";',
            ""
        ]

        for exp in exports:
            ret_type = TYPE_MAP_CS.get(exp["ret_type"], exp["ret_type"])
            raw_args = exp["args"].split(",") if exp["args"] != "void" else []
            cs_args = []
            for a in raw_args:
                parts = a.strip().split()
                if len(parts) >= 2:
                    t = parts[0]
                    n = parts[1].replace("*", "")
                    cs_t = TYPE_MAP_CS.get(t, t)
                    if "*" in parts[0] or "*" in parts[1]:
                        cs_t = "IntPtr"
                    cs_args.append(f"{cs_t} {n}")
                elif parts:
                    cs_args.append(f"IntPtr arg{len(cs_args)}")

            arg_str = ", ".join(cs_args)
            lines.extend([
                f'        [DllImport(LibraryName, EntryPoint = "{exp["name"]}", CallingConvention = CallingConvention.Cdecl)]',
                f'        public static extern {ret_type} {exp["name"]}({arg_str});',
                ""
            ])

        lines.extend([
            "    }",
            "}"
        ])
        return "\n".join(lines)

if __name__ == "__main__":
    gen = CSharpGen("veloc_physics")
    dummy_exports = [
        {"ret_type": "void", "name": "veloc_physics_init", "args": "void"},
        {"ret_type": "int", "name": "veloc_simulate_step", "args": "float dt, int entity_count"},
        {"ret_type": "float", "name": "veloc_get_energy", "args": "void"}
    ]
    cs_code = gen.generate_cs_class("NativePhysics", dummy_exports)
    out_f = Path("examples/unity_plugin/NativePhysics.cs")
    out_f.parent.mkdir(parents=True, exist_ok=True)
    out_f.write_text(cs_code, encoding="utf-8")
    print(f"Generated C# bindings: {out_f}")
