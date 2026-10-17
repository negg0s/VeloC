# VeloC Library & C-Header Export Engine
# Implements `veloc build --lib --emit-header` to produce static libraries (.a/.lib)
# and clean C-compatible headers (.h) for CMake, Meson, MSBuild, and Foreign FFI.

import os
import sys
import re
import subprocess
from pathlib import Path
from typing import List, Dict

ROOT_DIR = Path("D:/VeloC")
CLANG_PATH = Path("C:/Program Files/Windhawk/Compiler/bin/clang++.exe")
LLVM_AR_PATH = Path("C:/Program Files/Windhawk/Compiler/bin/llvm-ar.exe")

class LibEmitter:
    def __init__(self, root_dir: Path = ROOT_DIR):
        self.root_dir = root_dir
        self.include_dir = root_dir / "include"

    def extract_c_exports(self, source_code: str) -> List[Dict]:
        """Extracts functions marked with pub fn, extern \"C\", or standard fn."""
        exports = []
        # Pattern: extern "C" RetType name(args)
        ext_c_pattern = re.compile(r'extern\s+"C"\s+([A-Za-z0-9_]+)\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)')
        for m in ext_c_pattern.finditer(source_code):
            ret_type, name, args = m.groups()
            exports.append({
                "ret_type": ret_type,
                "name": name,
                "args": args.strip() or "void"
            })
        
        # Pattern: pub fn name(args) -> RetType
        pub_fn_pattern = re.compile(r'pub\s+fn\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)\s*(?:->\s*([A-Za-z0-9_]+))?')
        for m in pub_fn_pattern.finditer(source_code):
            name, args, ret_type = m.groups()
            exports.append({
                "ret_type": ret_type or "void",
                "name": name,
                "args": args.strip() or "void"
            })
        return exports

    def emit_header(self, exports: List[Dict], header_path: Path, guard_name: str = "VELOC_EXPORT_H"):
        lines = [
            f"#ifndef {guard_name}",
            f"#define {guard_name}",
            "",
            "/* Auto-generated VeloC Export Header */",
            "#include <stdint.h>",
            "#include <stddef.h>",
            "#include <stdbool.h>",
            "",
            "#ifdef __cplusplus",
            'extern "C" {',
            "#endif",
            ""
        ]
        for exp in exports:
            lines.append(f"{exp['ret_type']} {exp['name']}({exp['args']});")
        lines.extend([
            "",
            "#ifdef __cplusplus",
            "}",
            "#endif",
            "",
            f"#endif /* {guard_name} */",
            ""
        ])
        header_path.parent.mkdir(parents=True, exist_ok=True)
        header_path.write_text("\n".join(lines), encoding="utf-8")

    def build_static_lib(self, source_file: Path, output_lib: Path, emit_header_path: Path = None) -> bool:
        src_text = source_file.read_text(encoding="utf-8")
        exports = self.extract_c_exports(src_text)

        output_lib.parent.mkdir(parents=True, exist_ok=True)
        obj_file = output_lib.with_suffix(".o")

        # Compile to object file
        cmd_obj = [
            str(CLANG_PATH), "-std=c++20", "-O3", "-march=native", "-fwrapv",
            "-I" + str(self.include_dir), "-c", str(source_file), "-o", str(obj_file)
        ]
        res = subprocess.run(cmd_obj, cwd=str(self.root_dir), capture_output=True, text=True)
        if res.returncode != 0:
            print(f"[Lib Build Failed]:\n{res.stderr or res.stdout}")
            return False

        # Archive into static library .a / .lib
        ar_tool = str(LLVM_AR_PATH) if LLVM_AR_PATH.exists() else "ar"
        cmd_ar = [ar_tool, "rcs", str(output_lib), str(obj_file)]
        res_ar = subprocess.run(cmd_ar, cwd=str(self.root_dir), capture_output=True, text=True)
        if res_ar.returncode != 0:
            print(f"[Archive Failed]:\n{res_ar.stderr or res_ar.stdout}")
            return False

        if emit_header_path:
            guard = f"VELOC_{output_lib.stem.upper()}_H"
            self.emit_header(exports, emit_header_path, guard)
            print(f"[VeloC Lib] Export header generated: {emit_header_path}")

        print(f"[VeloC Lib] Static library generated: {output_lib}")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python src/lib_emitter.py <input.vc> <output.lib/.a> [--emit-header <output.h>]")
        sys.exit(1)

    in_f = Path(sys.argv[1])
    out_lib = Path(sys.argv[2])
    hdr_path = None
    if len(sys.argv) > 4 and sys.argv[3] == "--emit-header":
        hdr_path = Path(sys.argv[4])

    emitter = LibEmitter()
    ok = emitter.build_static_lib(in_f, out_lib, hdr_path)
    sys.exit(0 if ok else 1)
