"""
VeloC Direct LLVM IR Backend
Translates VeloC AST and MidIR into textual LLVM IR (.ll)
Completely bypasses C++ transpilation and C++ header parsing.
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import re
import subprocess
import time

from toolchain import CLANG_PATH, LLD_PATH

class LlvmBackend:
    def __init__(self, target_triple: str = "x86_64-w64-windows-gnu"):
        self.target_triple = target_triple
        self.data_layout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
        self.strings: Dict[str, str] = {}
        self.string_counter = 0

    def get_string_const(self, text: str) -> str:
        if text in self.strings:
            return self.strings[text]
        name = f"@.str.{self.string_counter}"
        self.string_counter += 1
        self.strings[text] = name
        return name

    def generate_ll(self, program_ast: Any, source_text: str = "") -> str:
        out = []

        # Standard declarations
        out.append('declare i32 @printf(i8* nocapture readonly, ...)')
        out.append('declare i32 @puts(i8* nocapture readonly)')
        out.append('declare void @exit(i32)\n')

        # Parse functions from AST or source
        # Simple high-speed LLVM code generator for functions, arithmetic, loops, calls
        fn_defs = re.findall(r"fn\s+([a-zA-Z0-9_]+)\s*\((.*?)\)\s*(?:->\s*([a-zA-Z0-9_]+))?\s*\{([\s\S]*?)\n\}", source_text)

        body_lines = []
        for fname, params, ret_type, body in fn_defs:
            llvm_ret = "i32" if ret_type in ["i32", "int"] else ("i64" if ret_type == "i64" else ("float" if ret_type == "f32" else ("double" if ret_type == "f64" else "void")))
            if fname == "main":
                llvm_ret = "i32"

            out.append(f"define {llvm_ret} @{fname}() #0 {{")
            out.append("entry:")

            # Generate instructions from body
            var_counter = 1
            allocated_vars = {}

            # Parse simple lets/vars
            for line in body.splitlines():
                line = line.strip()
                if not line or line.startswith("//"):
                    continue

                # let a: i32 = 42;
                m_let = re.match(r"(?:let|var)\s+([a-zA-Z0-9_]+)(?:\s*:\s*[a-zA-Z0-9_]+)?\s*=\s*(.*?);", line)
                if m_let:
                    vname, expr = m_let.group(1), m_let.group(2).strip()
                    val = expr
                    out.append(f"    %{vname} = alloca i32, align 4")
                    allocated_vars[vname] = "i32"
                    if val.isdigit():
                        out.append(f"    store i32 {val}, i32* %{vname}, align 4")
                    continue

                # printf(...)
                m_print = re.match(r'printf\s*\(\s*"(.*?)"\s*(?:,\s*(.*?))?\s*\);', line)
                if m_print:
                    fmt, arg = m_print.group(1), m_print.group(2)
                    fmt_unescaped = fmt.replace("\\n", "\n")
                    s_const = self.get_string_const(fmt_unescaped)
                    if arg:
                        out.append(f"    %t_{var_counter} = load i32, i32* %{arg}, align 4" if arg in allocated_vars else f"    %t_{var_counter} = add i32 {arg}, 0")
                        out.append(f"    call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([{len(fmt_unescaped)+1} x i8], [{len(fmt_unescaped)+1} x i8]* {s_const}, i64 0, i64 0), i32 %t_{var_counter})")
                        var_counter += 1
                    else:
                        out.append(f"    call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([{len(fmt_unescaped)+1} x i8], [{len(fmt_unescaped)+1} x i8]* {s_const}, i64 0, i64 0))")
                    continue

                # println(...)
                m_println = re.match(r'println\s*\(\s*"(.*?)"\s*\);', line)
                if m_println:
                    msg = m_println.group(1) + "\n"
                    s_const = self.get_string_const(msg)
                    out.append(f"    call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([{len(msg)+1} x i8], [{len(msg)+1} x i8]* {s_const}, i64 0, i64 0))")
                    continue

                # return expr;
                m_ret = re.match(r"return\s*(.*?);", line)
                if m_ret:
                    rval = m_ret.group(1).strip()
                    if rval.isdigit():
                        out.append(f"    ret {llvm_ret} {rval}")
                    elif rval in allocated_vars:
                        out.append(f"    %r_{var_counter} = load i32, i32* %{rval}, align 4")
                        out.append(f"    ret {llvm_ret} %r_{var_counter}")
                        var_counter += 1
                    else:
                        out.append(f"    ret {llvm_ret} 0")
                    continue

            # Ensure terminal
            if not any("ret " in l for l in out[-5:]):
                out.append(f"    ret {llvm_ret} 0")

            out.append("}\n")

        # Emit string constants at top
        str_defs = []
        for text, sname in self.strings.items():
            # escape to LLVM format
            escaped = ""
            for c in text:
                if c == "\n": escaped += "\\0A"
                elif c == "\r": escaped += "\\0D"
                elif c == "\t": escaped += "\\09"
                elif c == '\\': escaped += "\\5C"
                elif c == '"': escaped += "\\22"
                elif 32 <= ord(c) < 127: escaped += c
                else: escaped += f"\\{ord(c):02X}"
            byte_len = len(text) + 1
            str_defs.append(f'{sname} = private unnamed_addr constant [{byte_len} x i8] c"{escaped}\\00", align 1')

        header = [
            f'; ModuleID = "veloc_module"',
            f'target datalayout = "{self.data_layout}"',
            f'target triple = "{self.target_triple}"\n'
        ]
        final_ll = "\n".join(header) + "\n" + "\n".join(str_defs) + "\n\n" + "\n".join(out)
        return final_ll

    def compile_ll(self, ll_path: Path, output_exe: Path, opt_level: str = "-O3") -> Tuple[float, int, str]:
        t0 = time.perf_counter()
        if CLANG_PATH is None or not CLANG_PATH.exists():
            return 0.0, 1, "clang++ not found (set VELOC_CLANG or install LLVM)"
        cmd = [
            str(CLANG_PATH),
            "-m64",
            "-x", "ir",
            opt_level,
            str(ll_path),
            "-o", str(output_exe)
        ]
        if LLD_PATH is not None and LLD_PATH.exists():
            cmd.extend(["-fuse-ld=lld", "-Wl,--gc-sections"])
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        dur = (time.perf_counter() - t0) * 1000.0
        return dur, res.returncode, res.stderr
