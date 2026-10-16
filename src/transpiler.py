import os
import re
import sys
from typing import List, Dict, Tuple

class SoAField:
    def __init__(self, field_type: str, name: str):
        self.field_type = field_type.strip()
        self.name = name.strip()

class SoAStruct:
    def __init__(self, name: str, fields: List[SoAField]):
        self.name = name
        self.fields = fields

    def generate_cpp(self) -> str:
        lines = []
        lines.append(f"// Auto-generated VeloC Struct-of-Arrays (SoA) for SIMD acceleration")
        lines.append(f"struct {self.name}_SoA {{")
        lines.append("    usize capacity;")
        lines.append("    usize count;")
        for f in self.fields:
            lines.append(f"    {f.field_type}* VELOC_RESTRICT {f.name};")
        
        # Factory method: create
        lines.append(f"\n    static {self.name}_SoA create(usize cap) {{")
        lines.append(f"        {self.name}_SoA s;")
        lines.append("        s.capacity = cap;")
        lines.append("        s.count = 0;")
        for f in self.fields:
            lines.append(f"        s.{f.name} = ({f.field_type}*)veloc_aligned_alloc(32, sizeof({f.field_type}) * cap);")
        lines.append("        return s;")
        lines.append("    }")

        # Push method
        args = ", ".join([f"{f.field_type} val_{f.name}" for f in self.fields])
        lines.append(f"\n    VELOC_INLINE void push({args}) {{")
        lines.append("        if (count < capacity) {")
        for f in self.fields:
            lines.append(f"            this->{f.name}[count] = val_{f.name};")
        lines.append("            count++;")
        lines.append("        }")
        lines.append("    }")

        # Destroy method
        lines.append("\n    void destroy() {")
        for f in self.fields:
            lines.append(f"        if ({f.name}) {{ veloc_aligned_free({f.name}); {f.name} = NULL; }}")
        lines.append("        capacity = 0;")
        lines.append("        count = 0;")
        lines.append("    }")

        # Built-in Compile-time Reflection & JSON Serialization (Reddit #1 Wishlist Feature)
        lines.append("\n    // Auto-generated Reflection: to_json()")
        lines.append("    std::string to_json(usize i) const {")
        lines.append('        if (i >= count) return "{}";')
        lines.append("        std::ostringstream ss;")
        lines.append('        ss << "{";')
        for idx, f in enumerate(self.fields):
            comma = ', ' if idx < len(self.fields) - 1 else ''
            lines.append(f'        ss << "\\"{f.name}\\": " << this->{f.name}[i] << "{comma}";')
        lines.append('        ss << "}";')
        lines.append("        return ss.str();")
        lines.append("    }")
        lines.append(f'\n    static const char* type_name() {{ return "{self.name}_SoA"; }}')
        lines.append(f'    static usize field_count() {{ return {len(self.fields)}; }}')
        lines.append("};\n")
        return "\n".join(lines)


class VeloCTranspiler:
    def __init__(self, include_dir: str, test_mode: bool = False):
        self.include_dir = include_dir
        self.test_mode = test_mode
        self.soa_structs: Dict[str, SoAStruct] = {}
        self.defer_counter = 0
        self.tests: List[Tuple[str, str]] = [] # (name, func_name)

    def transpile_source(self, code: str) -> str:
        def is_in_quotes(line_str: str, pos: int) -> bool:
            in_q = False
            for i in range(pos):
                if line_str[i] == '"' and (i == 0 or line_str[i-1] != '\\'):
                    in_q = not in_q
            return in_q

        # 1. Transform `soa struct Name { ... };`
        soa_pattern = re.compile(r'soa\s+struct\s+([A-Za-z0-9_]+)\s*\{([^}]+)\};', re.MULTILINE)
        
        def replace_soa(match):
            struct_name = match.group(1)
            body = match.group(2)
            fields = []
            for line in body.split(';'):
                line = line.strip()
                if not line:
                    continue
                parts = line.rsplit(None, 1)
                if len(parts) == 2:
                    fields.append(SoAField(parts[0], parts[1]))
            soa = SoAStruct(struct_name, fields)
            self.soa_structs[struct_name] = soa
            return soa.generate_cpp()

        code = soa_pattern.sub(replace_soa, code)

        # 2. Transform `test "name" { ... }` blocks (First-class Testing like Zig/Rust!)
        test_pattern = re.compile(r'test\s+"([^"]+)"\s*\{([\s\S]*?)\n\}', re.MULTILINE)
        test_idx = 0
        def replace_test(match):
            nonlocal test_idx
            test_idx += 1
            test_name = match.group(1)
            test_body = match.group(2)
            func_name = f"_veloc_test_case_{test_idx}"
            self.tests.append((test_name, func_name))
            return f"void {func_name}() {{\n{test_body}\n}}"

        code = test_pattern.sub(replace_test, code)

        # 3. Transform `defer { ... }` blocks and `defer <statement>;` line by line
        def replace_defer_blocks(code_str: str) -> str:
            pat = re.compile(r'\bdefer\s*\{')
            pos = 0
            res = []
            while True:
                m = pat.search(code_str, pos)
                if not m:
                    res.append(code_str[pos:])
                    break
                res.append(code_str[pos:m.start()])
                self.defer_counter += 1
                brace_count = 1
                idx = m.end()
                while idx < len(code_str) and brace_count > 0:
                    if code_str[idx] == '{': brace_count += 1
                    elif code_str[idx] == '}': brace_count -= 1
                    idx += 1
                body = code_str[m.end():idx-1].strip()
                replacement = f"auto _veloc_defer_{self.defer_counter} = ::veloc::ScopeGuardHelper() + [&]() {{ {body} }};"
                res.append(replacement)
                pos = idx
            return ''.join(res)

        code = replace_defer_blocks(code)

        def process_line(line: str) -> str:
            m = re.match(r'^(\s*)defer\s+([^;/{}]+);(.*)$', line)
            if m:
                indent = m.group(1)
                stmt = m.group(2).strip()
                trailing = m.group(3)
                self.defer_counter += 1
                return f"{indent}auto _veloc_defer_{self.defer_counter} = ::veloc::ScopeGuardHelper() + [&]() {{ {stmt}; }};{trailing}"
            return line

        code_lines = [process_line(l) for l in code.splitlines()]
        code = "\n".join(code_lines)
        # 3.5. Transform `if let Some(var) = expr` and `if let Ok(var) = expr` (Rust-style pattern matching)
        self.if_let_counter = 0
        def replace_if_let(code_str: str) -> str:
            pat = re.compile(r'\bif\s+let\s+Some\s*\(\s*([A-Za-z0-9_]+)\s*\)\s*=\s*([^;{]+)\{')
            pos = 0
            res = []
            while True:
                m = pat.search(code_str, pos)
                if not m:
                    res.append(code_str[pos:])
                    break
                res.append(code_str[pos:m.start()])
                self.if_let_counter += 1
                var_name = m.group(1).strip()
                expr = m.group(2).strip()
                tmp_name = f"_veloc_opt_{self.if_let_counter}"
                replacement = f"if (auto {tmp_name} = ({expr}); {tmp_name}.is_some()) {{\n        auto& {var_name} = {tmp_name}.val;\n"
                res.append(replacement)
                pos = m.end()
            return ''.join(res)

        def replace_if_let_ok(code_str: str) -> str:
            pat = re.compile(r'\bif\s+let\s+Ok\s*\(\s*([A-Za-z0-9_]+)\s*\)\s*=\s*([^;{]+)\{')
            pos = 0
            res = []
            while True:
                m = pat.search(code_str, pos)
                if not m:
                    res.append(code_str[pos:])
                    break
                res.append(code_str[pos:m.start()])
                self.if_let_counter += 1
                var_name = m.group(1).strip()
                expr = m.group(2).strip()
                tmp_name = f"_veloc_res_{self.if_let_counter}"
                replacement = f"if (auto {tmp_name} = ({expr}); {tmp_name}.is_ok()) {{\n        auto& {var_name} = {tmp_name}.val;\n"
                res.append(replacement)
                pos = m.end()
            return ''.join(res)

        code = replace_if_let(code)
        code = replace_if_let_ok(code)

        # 3.6. Transform `while let Some(var) = expr` and `while let Ok(var) = expr`
        def replace_while_let(code_str: str) -> str:
            pat = re.compile(r'\bwhile\s+let\s+Some\s*\(\s*([A-Za-z0-9_]+)\s*\)\s*=\s*([^;{]+)\{')
            pos = 0
            res = []
            while True:
                m = pat.search(code_str, pos)
                if not m:
                    res.append(code_str[pos:])
                    break
                res.append(code_str[pos:m.start()])
                self.if_let_counter += 1
                var_name = m.group(1).strip()
                expr = m.group(2).strip()
                tmp_name = f"_veloc_wopt_{self.if_let_counter}"
                replacement = f"for (auto {tmp_name} = ({expr}); {tmp_name}.is_some(); {tmp_name} = ({expr})) {{\n        auto& {var_name} = {tmp_name}.val;\n"
                res.append(replacement)
                pos = m.end()
            return ''.join(res)

        def replace_while_let_ok(code_str: str) -> str:
            pat = re.compile(r'\bwhile\s+let\s+Ok\s*\(\s*([A-Za-z0-9_]+)\s*\)\s*=\s*([^;{]+)\{')
            pos = 0
            res = []
            while True:
                m = pat.search(code_str, pos)
                if not m:
                    res.append(code_str[pos:])
                    break
                res.append(code_str[pos:m.start()])
                self.if_let_counter += 1
                var_name = m.group(1).strip()
                expr = m.group(2).strip()
                tmp_name = f"_veloc_wres_{self.if_let_counter}"
                replacement = f"for (auto {tmp_name} = ({expr}); {tmp_name}.is_ok(); {tmp_name} = ({expr})) {{\n        auto& {var_name} = {tmp_name}.val;\n"
                res.append(replacement)
                pos = m.end()
            return ''.join(res)

        code = replace_while_let(code)
        code = replace_while_let_ok(code)

        # 4. Transform `for (let i in expr)` and `for (let (i, val) in enumerate(expr))`
        code = re.sub(r'\bfor\s*\(\s*let\s+mut\s*\(\s*([A-Za-z0-9_]+)\s*,\s*([A-Za-z0-9_]+)\s*\)\s+in\s+enumerate\(([^)]+)\)\s*\)',
                      r'usize \1 = 0; for (auto& \2 : \3) if (bool _veloc_step_ = true) for (; _veloc_step_; _veloc_step_ = false, \1++)', code)
        code = re.sub(r'\bfor\s*\(\s*let\s*\(\s*([A-Za-z0-9_]+)\s*,\s*([A-Za-z0-9_]+)\s*\)\s+in\s+enumerate\(([^)]+)\)\s*\)',
                      r'usize \1 = 0; for (const auto& \2 : \3) if (bool _veloc_step_ = true) for (; _veloc_step_; _veloc_step_ = false, \1++)', code)

        code = re.sub(r'\bfor\s*\(\s*let\s+mut\s+([A-Za-z0-9_]+)\s+in\s+([^)]+)\)', r'for (auto \1 : \2)', code)
        code = re.sub(r'\bfor\s*\(\s*let\s+([A-Za-z0-9_]+)\s+in\s+([^)]+)\)', r'for (const auto \1 : \2)', code)
        code = re.sub(r'\bfor\s*\(\s*([A-Za-z0-9_]+)\s+in\s+([^)]+)\)', r'for (auto \1 : \2)', code)

        # 5. Transform tuple destructuring: `let (a, b) = expr;` -> `const auto [a, b] = expr;`
        code = re.sub(r'\blet\s+mut\s*\(([^)]+)\)\s*=', r'auto [\1] =', code)
        code = re.sub(r'\blet\s*\(([^)]+)\)\s*=', r'const auto [\1] =', code)

        # 6. Transform `let mut [type] x = ...;` and `let [type] x = ...;`
        code = re.sub(r'\blet\s+mut\s+([A-Za-z0-9_]+)\s*:\s*([A-Za-z0-9_]+)\s*=', r'\2 \1 =', code)
        code = re.sub(r'\blet\s+([A-Za-z0-9_]+)\s*:\s*([A-Za-z0-9_]+)\s*=', r'const \2 \1 =', code)
        code = re.sub(r'\blet\s+mut\s+([A-Za-z0-9_]+)\s+([A-Za-z0-9_]+)\s*=', r'\1 \2 =', code)
        code = re.sub(r'\blet\s+mut\s+([A-Za-z0-9_]+)\s*=', r'auto \1 =', code)
        code = re.sub(r'\blet\s+([A-Za-z0-9_]+)\s+([A-Za-z0-9_]+)\s*=', r'const \1 \2 =', code)
        code = re.sub(r'\blet\s+([A-Za-z0-9_]+)\s*=', r'const auto \1 =', code)

        # 7. Transform `expr as Type` (Rust-style safe cast)
        as_pattern = re.compile(r'(\((?:[^()]|\([^()]*\))*\)|[a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+|\([^()]*\))*)\s+as\s+([a-zA-Z0-9_]+)\b')
        as_lines = []
        for aline in code.splitlines():
            if ' as ' in aline:
                def repl_as(m):
                    if is_in_quotes(aline, m.start()):
                        return m.group(0)
                    return f"static_cast<{m.group(2)}>({m.group(1)})"
                aline = as_pattern.sub(repl_as, aline)
            as_lines.append(aline)
        code = '\n'.join(as_lines)

        # 8. Transform Rust-style Anonymous Lambdas `|params| => expr`
        lambda_pattern = re.compile(r'\|([A-Za-z0-9_,\s]+)\|\s*=>\s*([^;,\n\)]+)')
        lambda_lines = []
        for lline in code.splitlines():
            if '|' in lline and '=>' in lline:
                def repl_lambda(m):
                    if is_in_quotes(lline, m.start()):
                        return m.group(0)
                    params = [p.strip() for p in m.group(1).split(',')]
                    auto_params = ', '.join([f'auto {p}' for p in params])
                    body = m.group(2).strip()
                    return f'[&]({auto_params}) {{ return {body}; }}'
                lline = lambda_pattern.sub(repl_lambda, lline)
            lambda_lines.append(lline)
        code = '\n'.join(lambda_lines)

        # 9. Transform `fn name(...) -> type` to `auto name(...) -> type`
        code = re.sub(r'\bfn\s+([A-Za-z0-9_]+)\s*\(', r'auto \1(', code)

        # 6. Transform String Interpolation: f"Hello {name}, x = {x}"
        def replace_interp(match):
            raw_str = match.group(1)
            parts = re.split(r'\{([^}]+)\}', raw_str)
            if len(parts) == 1:
                return f'"{raw_str}"'
            
            exprs = []
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    if part:
                        exprs.append(f'std::string("{part}")')
                else:
                    exprs.append(f'::veloc::to_str({part.strip()})')
            return f"({' + '.join(exprs)}).c_str()"

        code = re.sub(r'f"([^"]*)"', replace_interp, code)

        # 7. Transform `noalias` keyword to `VELOC_RESTRICT`
        code = re.sub(r'\bnoalias\b', 'VELOC_RESTRICT', code)

        # 8. Transform `bench "name" { ... }` blocks (Sub-nanosecond hardware cycle & time benchmarking)
        def replace_bench_blocks(code_str: str) -> str:
            pattern = re.compile(r'\bbench\s+"([^"]+)"\s*\{')
            pos = 0
            result = []
            while True:
                m = pattern.search(code_str, pos)
                if not m:
                    result.append(code_str[pos:])
                    break
                result.append(code_str[pos:m.start()])
                name = m.group(1)
                brace_count = 1
                idx = m.end()
                while idx < len(code_str) and brace_count > 0:
                    if code_str[idx] == '{': brace_count += 1
                    elif code_str[idx] == '}': brace_count -= 1
                    idx += 1
                inner = code_str[m.end():idx-1]
                replacement = (
                    f"{{\n"
                    f"    ::veloc::CycleCounter _veloc_cc;\n"
                    f"    VeloC_Timer _veloc_timer;\n"
                    f"    _veloc_timer.start();\n"
                    f"    {{\n{inner}\n    }}\n"
                    f'    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\\n", "{name}", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());\n'
                    f"}}"
                )
                result.append(replacement)
                pos = idx
            return ''.join(result)

        code = replace_bench_blocks(code)

        # 9. Transform `match (expr) { "key" => ... _ => ... }` pattern matching
        def replace_match_blocks(code_str: str) -> str:
            pattern = re.compile(r'\bmatch\s*\(([^)]+)\)\s*\{')
            pos = 0
            result = []
            while True:
                m = pattern.search(code_str, pos)
                if not m:
                    result.append(code_str[pos:])
                    break
                result.append(code_str[pos:m.start()])
                target = m.group(1).strip()
                brace_count = 1
                idx = m.end()
                while idx < len(code_str) and brace_count > 0:
                    if code_str[idx] == '{': brace_count += 1
                    elif code_str[idx] == '}': brace_count -= 1
                    idx += 1
                inner = code_str[m.end():idx-1]
                
                lines = []
                arm_pattern = re.compile(r'("([^"]+)"|([0-9]+)|_)\s*=>\s*(\{[\s\S]*?\}|[^;]+;)')
                arms = list(arm_pattern.finditer(inner))
                # Check if any arm actually matches a string key (arm.group(2))
                has_string_key = any(bool(a.group(2)) for a in arms)

                if has_string_key:
                    lines.append(f"switch (::veloc::str_hash({target})) {{")
                else:
                    lines.append(f"switch ({target}) {{")

                for arm in arms:
                    key = arm.group(1)
                    body = arm.group(4).strip()
                    if key == '_':
                        lines.append(f"    default: {body} break;")
                    elif arm.group(2): # String value
                        str_val = arm.group(2)
                        lines.append(f'    case "{str_val}"_hash: {body} break;')
                    elif arm.group(3): # Int value
                        int_val = arm.group(3)
                        lines.append(f'    case {int_val}: {body} break;')
                lines.append("}")
                result.append("\n".join(lines))
                pos = idx
            return ''.join(result)

        code = replace_match_blocks(code)

        # 10. Transform `switch_str (expr)` and string cases: `case "str":` -> `case "str"_hash:`
        code = re.sub(r'\bswitch_str\s*\(([^)]+)\)', r'switch (::veloc::str_hash(\1))', code)
        code = re.sub(r'\bcase\s+"([^"]+)":', r'case "\1"_hash:', code)

        # 11. Transform Pipe Operator `|>` (Elixir / F# / C++ P2011 style functional chaining)
        def is_in_quotes(line_str: str, pos: int) -> bool:
            in_q = False
            for i in range(pos):
                if line_str[i] == '"' and (i == 0 or line_str[i-1] != '\\'):
                    in_q = not in_q
            return in_q

        def has_code_pipe(line_str: str) -> bool:
            pos = 0
            while True:
                idx = line_str.find('|>', pos)
                if idx == -1: return False
                if not is_in_quotes(line_str, idx): return True
                pos = idx + 2

        pipe_lines = []
        for pline in code.splitlines():
            if not has_code_pipe(pline):
                pipe_lines.append(pline)
                continue

            parts = pline.split('|>')
            first = parts[0].rstrip()
            idx = len(first) - 1
            paren_depth = 0
            while idx >= 0:
                ch = first[idx]
                if ch == ')': paren_depth += 1
                elif ch == '(':
                    if paren_depth > 0: paren_depth -= 1
                    else: break
                elif paren_depth == 0 and ch in "=;,{(+-*/":
                    break
                idx -= 1
            
            prefix = first[:idx+1]
            target = first[idx+1:].strip()

            for part in parts[1:-1]:
                stage = part.strip()
                if '(' in stage and stage.endswith(')'):
                    fn_name, args = stage.split('(', 1)
                    args = args[:-1].strip()
                    target = f"{fn_name.strip()}({target}, {args})" if args else f"{fn_name.strip()}({target})"
                else:
                    target = f"{stage}({target})"

            last = parts[-1].strip()
            suffix_idx = len(last)
            for i in range(len(last)-1, -1, -1):
                if last[i] in ";\n":
                    suffix_idx = i
                    break
            stage = last[:suffix_idx].strip()
            suffix = last[suffix_idx:]

            if '(' in stage and stage.endswith(')'):
                fn_name, args = stage.split('(', 1)
                args = args[:-1].strip()
                target = f"{fn_name.strip()}({target}, {args})" if args else f"{fn_name.strip()}({target})"
            else:
                target = f"{stage}({target})"

            pipe_lines.append(f"{prefix} {target}{suffix}")

        code = '\n'.join(pipe_lines)

        # 12. Transform Null-Coalescing Operator `??` (C# / Swift / Kotlin style)
        coalesce_pattern = re.compile(r'([a-zA-Z0-9_.\(\)]+)\s*\?\?\s*([a-zA-Z0-9_.\(\)\"]+)')
        coalesce_lines = []
        for cline in code.splitlines():
            if '??' in cline:
                def repl_coalesce(m):
                    if is_in_quotes(cline, m.start()):
                        return m.group(0)
                    return f"::veloc::coalesce({m.group(1)}, {m.group(2)})"
                cline = coalesce_pattern.sub(repl_coalesce, cline)
            coalesce_lines.append(cline)
        code = '\n'.join(coalesce_lines)

        # 13. Transform Non-Null Assertion Operator `opt!` (Rust/TypeScript unwrap syntax: opt! -> (opt).unwrap())
        assert_pattern = re.compile(r'([a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+|\([^)]*\))*)!(?![=])')
        assert_lines = []
        for aline in code.splitlines():
            if '!' in aline:
                def repl_assert(m):
                    if is_in_quotes(aline, m.start()):
                        return m.group(0)
                    target_expr = m.group(1).strip()
                    # avoid keywords like not, return, etc.
                    if target_expr in ('return', 'throw', 'delete', 'new', 'case'):
                        return m.group(0)
                    return f"({target_expr}).unwrap()"
                aline = assert_pattern.sub(repl_assert, aline)
            assert_lines.append(aline)
        code = '\n'.join(assert_lines)

        # 14. Transform `println(...)` and `print(...)`
        def replace_println(match):
            inner = match.group(1).strip()
            if inner.startswith('"') and inner.endswith('"'):
                inner_str = inner[:-1] + '\\n"'
                return f'printf({inner_str});'
            elif inner.startswith('"') and ',' in inner:
                first_part, rest = inner.split(',', 1)
                first_part = first_part.strip()
                if first_part.endswith('"'):
                    first_part = first_part[:-1] + '\\n"'
                    return f'printf({first_part}, {rest.strip()});'
            return f'printf("%s\\n", {inner});'

        code = re.sub(r'\bprintln\s*\((.*?)\);', replace_println, code)
        code = re.sub(r'\bprint\s*\((.*?)\);', r'printf("%s", \1);', code)

        # 12. Strip `module ...;` and `import ...;`
        code = re.sub(r'^\s*module\s+[^;]+;', '// [VeloC module declaration]', code, flags=re.MULTILINE)
        code = re.sub(r'^\s*import\s+[^;]+;', '// [VeloC import declaration]', code, flags=re.MULTILINE)

        has_user_main = bool(re.search(r'\b(int|auto)\s+main\s*\(', code))

        # If in test mode, rename user main if present and inject test main runner
        if self.test_mode or (len(self.tests) > 0 and not has_user_main):
            if self.test_mode and has_user_main:
                code = re.sub(r'\b(int|auto)\s+main\s*\(', r'\1 _user_main_disabled(', code)

            test_main = [
                "\n// Auto-generated VeloC Test Runner",
                "int main() {",
                '    printf("==================================================\\n");',
                '    printf("           VeloC Built-in Test Suite              \\n");',
                '    printf("==================================================\\n");',
                "    int passed = 0;",
                "    int failed = 0;",
                "    VeloC_Timer timer;",
            ]
            for name, func in self.tests:
                test_main.append(f'    printf("  Running test: %-30s ... ", "{name}");')
                test_main.append("    timer.start();")
                test_main.append(f"    {func}();")
                test_main.append(f'    printf("[PASS] (%.2f ms)\\n", timer.elapsed_ms());')
                test_main.append("    passed++;")
            test_main.append('    printf("--------------------------------------------------\\n");')
            test_main.append('    printf("Results: %d passed, %d failed\\n", passed, failed);')
            test_main.append('    printf("==================================================\\n");')
            test_main.append("    return failed == 0 ? 0 : 1;")
            test_main.append("}\n")
            code += "\n" + "\n".join(test_main)

        # Add preamble
        header_path = os.path.join(self.include_dir, 'veloc.h').replace('\\', '/')
        preamble = f'#include "{header_path}"\n\n'
        return preamble + code

    def transpile_file(self, input_file: str, output_file: str) -> str:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        transpiled = self.transpile_source(content)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(transpiled)
        return output_file
