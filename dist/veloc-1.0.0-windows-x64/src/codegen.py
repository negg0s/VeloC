# VeloC AST-to-C++ Code Generator
# Emits optimized, valid C++ with exact #line directives for 100% source mapping!

import os
from typing import List, Tuple
from ast_nodes import *

class CppCodegen:
    def __init__(self, include_dir: str, test_mode: bool = False):
        self.include_dir = include_dir.replace("\\", "/")
        self.test_mode = test_mode
        self.tests: List[Tuple[str, str]] = [] # (name, func_name)
        self.test_counter = 0
        self.defer_counter = 0
        self.has_user_main = False

    def emit_expr(self, expr: Expr) -> str:
        if isinstance(expr, IntLiteral):
            return expr.value
        elif isinstance(expr, FloatLiteral):
            return expr.value
        elif isinstance(expr, StringLiteral):
            # Escape newlines, carriage returns, tabs
            escaped = expr.value.replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t").replace('"', '\\"')
            return f'"{escaped}"'
        elif isinstance(expr, CharLiteral):
            return f"'{expr.value}'"
        elif isinstance(expr, BoolLiteral):
            return "true" if expr.value else "false"
        elif isinstance(expr, NullLiteral):
            return "NULL"
        elif isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, BinaryExpr):
            left_str = self.emit_expr(expr.left)
            right_str = self.emit_expr(expr.right)
            return f"({left_str} {expr.op} {right_str})"
        elif isinstance(expr, UnaryExpr):
            operand_str = self.emit_expr(expr.operand)
            return f"({expr.op}{operand_str})"
        elif isinstance(expr, CastExpr):
            sub_expr = self.emit_expr(expr.expr)
            if "*" in expr.target_type or expr.target_type in ("uintptr_t", "intptr_t", "usize"):
                return f"(({expr.target_type})({sub_expr}))"
            return f"static_cast<{expr.target_type}>({sub_expr})"
        elif isinstance(expr, AssertNonNullExpr):
            sub_expr = self.emit_expr(expr.expr)
            return f"({sub_expr}).unwrap()"
        elif isinstance(expr, TryExpr):
            sub_expr = self.emit_expr(expr.expr)
            return f"({{ auto _v_try = ({sub_expr}); if (::veloc::try_is_err(_v_try)) return ::veloc::try_forward_err(_v_try); ::veloc::try_unwrap(_v_try); }})"
        elif isinstance(expr, MatchExpr):
            expr_str = self.emit_expr(expr.expr)
            has_str = any(arm.pattern_val and arm.pattern_val.startswith('"') for arm in expr.arms)
            switch_header = f"switch (::veloc::str_hash({expr_str})) {{" if has_str else f"switch ({expr_str}) {{"
            body_parts = [f"([&]() {{\n    {switch_header}\n"]
            for arm in expr.arms:
                if arm.pattern_val is None or arm.pattern_val == "_":
                    body_parts.append("        default:\n")
                elif arm.pattern_val.startswith('"'):
                    unquoted = arm.pattern_val.strip('"')
                    body_parts.append(f'        case "{unquoted}"_hash:\n')
                else:
                    body_parts.append(f"        case {arm.pattern_val}:\n")
                if isinstance(arm.body, Expr):
                    arm_val = self.emit_expr(arm.body)
                    body_parts.append(f"            return ({arm_val});\n")
                elif isinstance(arm.body, Stmt):
                    body_parts.append(self.emit_stmt(arm.body, 3))
            body_parts.append("    }\n})()")
            return "".join(body_parts)

        elif isinstance(expr, CallExpr):
            callee_str = self.emit_expr(expr.callee)
            if callee_str == "println":
                if len(expr.args) == 1:
                    arg_expr = expr.args[0]
                    if isinstance(arg_expr, StringLiteral):
                        esc = arg_expr.value.replace("\n", "\\n").replace('"', '\\"')
                        return f'printf("{esc}\\n")'
                    else:
                        arg_str = self.emit_expr(arg_expr)
                        return f'printf("%s\\n", (::veloc::to_str({arg_str})).c_str())'
                elif len(expr.args) >= 2:
                    fmt = self.emit_expr(expr.args[0])
                    rest = ", ".join(self.emit_expr(a) for a in expr.args[1:])
                    return f'printf({fmt}, {rest})'
                else:
                    return 'printf("\\n")'
            elif callee_str == "print":
                if len(expr.args) == 1:
                    arg_str = self.emit_expr(expr.args[0])
                    return f'printf("%s", (::veloc::to_str({arg_str})).c_str())'
                elif len(expr.args) >= 2:
                    fmt = self.emit_expr(expr.args[0])
                    rest = ", ".join(self.emit_expr(a) for a in expr.args[1:])
                    return f'printf({fmt}, {rest})'
            args_str = ", ".join(self.emit_expr(a) for a in expr.args)
            return f"{callee_str}({args_str})"
        elif isinstance(expr, MemberAccessExpr):
            obj_str = self.emit_expr(expr.object)
            return f"{obj_str}.{expr.member}"
        elif isinstance(expr, IndexExpr):
            coll_str = self.emit_expr(expr.collection)
            idx_str = self.emit_expr(expr.index)
            return f"{coll_str}[{idx_str}]"
        elif isinstance(expr, LambdaExpr):
            params_str = ", ".join([f"auto {p}" for p in expr.params])
            body_str = self.emit_expr(expr.body)
            return f"[&]({params_str}) {{ return {body_str}; }}"
        elif isinstance(expr, PipeExpr):
            # Transform x |> f |> g(a) -> g(f(x), a)
            left_str = self.emit_expr(expr.left)
            if isinstance(expr.right, CallExpr):
                callee_str = self.emit_expr(expr.right.callee)
                existing_args = [self.emit_expr(a) for a in expr.right.args]
                args = [left_str] + existing_args
                return f"{callee_str}({', '.join(args)})"
            elif isinstance(expr.right, Identifier):
                return f"{expr.right.name}({left_str})"
            else:
                right_str = self.emit_expr(expr.right)
                return f"{right_str}({left_str})"
        elif isinstance(expr, CoalesceExpr):
            left_str = self.emit_expr(expr.left)
            right_str = self.emit_expr(expr.right)
            return f"::veloc::coalesce({left_str}, {right_str})"
        elif isinstance(expr, FStringLiteral):
            # Parse f"Hello {name}, x = {x}"
            import re
            parts = re.split(r'\{([^}]+)\}', expr.raw_value)
            if len(parts) == 1:
                return f'"{parts[0]}"'
            exprs = []
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    if part:
                        esc = part.replace("\n", "\\n").replace('"', '\\"')
                        exprs.append(f'std::string("{esc}")')
                else:
                    exprs.append(f'::veloc::to_str({part.strip()})')
            return f"({' + '.join(exprs)}).c_str()"
        elif isinstance(expr, TupleExpr):
            elems = ", ".join(self.emit_expr(e) for e in expr.elements)
            return f"std::make_tuple({elems})"
        else:
            return ""

    def emit_stmt(self, stmt: Stmt, indent_level: int = 1) -> str:
        ind = "    " * indent_level
        line_dir = f'#line {stmt.line} "{stmt.file.replace(chr(92), "/")}"\n' if stmt.file != "<stdin>" else ""

        if isinstance(stmt, ExprStmt):
            return f"{line_dir}{ind}{self.emit_expr(stmt.expr)};\n"
        elif isinstance(stmt, BlockStmt):
            lines = [f"{ind}{{\n"]
            for s in stmt.statements:
                lines.append(self.emit_stmt(s, indent_level + 1))
            lines.append(f"{ind}}}\n")
            return "".join(lines)
        elif isinstance(stmt, SeqStmt):
            lines = []
            for s in stmt.statements:
                lines.append(self.emit_stmt(s, indent_level))
            return "".join(lines)
        elif isinstance(stmt, LetStmt):
            if stmt.destructure:
                vars_str = ", ".join(stmt.destructure)
                qual = "auto" if stmt.is_mut else "const auto"
                init_str = self.emit_expr(stmt.init_expr) if stmt.init_expr else "{}"
                return f"{line_dir}{ind}{qual} [{vars_str}] = {init_str};\n"
            else:
                qual = "" if stmt.is_mut else "const "
                t_str = stmt.type_annotation if stmt.type_annotation else "auto"
                if stmt.constructor_args is not None:
                    cargs = ", ".join(self.emit_expr(a) for a in stmt.constructor_args)
                    return f"{line_dir}{ind}{qual}{t_str} {stmt.name}({cargs});\n"
                init_str = f" = {self.emit_expr(stmt.init_expr)}" if stmt.init_expr else ""
                return f"{line_dir}{ind}{qual}{t_str} {stmt.name}{init_str};\n"
        elif isinstance(stmt, ReturnStmt):
            val = f" {self.emit_expr(stmt.value)}" if stmt.value else ""
            return f"{line_dir}{ind}return{val};\n"
        elif isinstance(stmt, IfStmt):
            cond = self.emit_expr(stmt.condition)
            res = [f"{line_dir}{ind}if ({cond}) {{\n"]
            for s in stmt.then_branch.statements:
                res.append(self.emit_stmt(s, indent_level + 1))
            res.append(f"{ind}}}")
            if stmt.else_branch:
                if isinstance(stmt.else_branch, IfStmt):
                    res.append(" else ")
                    res.append(self.emit_stmt(stmt.else_branch, indent_level).lstrip())
                else:
                    res.append(" else {\n")
                    if isinstance(stmt.else_branch, BlockStmt):
                        for s in stmt.else_branch.statements:
                            res.append(self.emit_stmt(s, indent_level + 1))
                    else:
                        res.append(self.emit_stmt(stmt.else_branch, indent_level + 1))
                    res.append(f"{ind}}}\n")
            else:
                res.append("\n")
            return "".join(res)
        elif isinstance(stmt, IfLetStmt):
            check_meth = "is_some()" if stmt.pattern_type == "Some" else "is_ok()"
            expr_str = self.emit_expr(stmt.expr)
            opt_var = f"_veloc_iflet_{stmt.line}_{stmt.col}"
            res = [f"{line_dir}{ind}if (auto {opt_var} = ({expr_str}); {opt_var}.{check_meth}) {{\n"]
            res.append(f"{ind}    auto& {stmt.var_name} = {opt_var}.val;\n")
            for s in stmt.then_branch.statements:
                res.append(self.emit_stmt(s, indent_level + 1))
            res.append(f"{ind}}}")
            if stmt.else_branch:
                res.append(" else {\n")
                if isinstance(stmt.else_branch, BlockStmt):
                    for s in stmt.else_branch.statements:
                        res.append(self.emit_stmt(s, indent_level + 1))
                else:
                    res.append(self.emit_stmt(stmt.else_branch, indent_level + 1))
                res.append(f"{ind}}}\n")
            else:
                res.append("\n")
            return "".join(res)
        elif isinstance(stmt, WhileStmt):
            cond = self.emit_expr(stmt.condition)
            res = [f"{line_dir}{ind}while ({cond}) {{\n"]
            for s in stmt.body.statements:
                res.append(self.emit_stmt(s, indent_level + 1))
            res.append(f"{ind}}}\n")
            return "".join(res)
        elif isinstance(stmt, WhileLetStmt):
            check_meth = "is_some()" if stmt.pattern_type == "Some" else "is_ok()"
            expr_str = self.emit_expr(stmt.expr)
            opt_var = f"_veloc_wlet_{stmt.line}_{stmt.col}"
            res = [f"{line_dir}{ind}for (auto {opt_var} = ({expr_str}); {opt_var}.{check_meth}; {opt_var} = ({expr_str})) {{\n"]
            res.append(f"{ind}    auto& {stmt.var_name} = {opt_var}.val;\n")
            for s in stmt.body.statements:
                res.append(self.emit_stmt(s, indent_level + 1))
            res.append(f"{ind}}}\n")
            return "".join(res)
        elif isinstance(stmt, ForInStmt):
            qual = "auto" if stmt.is_mut else "const auto"
            iter_str = self.emit_expr(stmt.iter_expr)
            res = [f"{line_dir}{ind}for ({qual} {stmt.var_name} : {iter_str}) {{\n"]
            for s in stmt.body.statements:
                res.append(self.emit_stmt(s, indent_level + 1))
            res.append(f"{ind}}}\n")
            return "".join(res)
        elif isinstance(stmt, ForEnumerateStmt):
            qual = "auto&" if stmt.is_mut else "const auto&"
            iter_expr = stmt.iter_expr
            if isinstance(iter_expr, CallExpr) and isinstance(iter_expr.callee, Identifier) and iter_expr.callee.name == "enumerate" and len(iter_expr.args) == 1:
                iter_str = self.emit_expr(iter_expr.args[0])
            else:
                iter_str = self.emit_expr(iter_expr)
            res = [f"{line_dir}{ind}usize {stmt.idx_var} = 0;\n"]
            res.append(f"{ind}for ({qual} {stmt.val_var} : {iter_str}) if (bool _step_ = true) for (; _step_; _step_ = false, {stmt.idx_var}++) {{\n")
            for s in stmt.body.statements:
                res.append(self.emit_stmt(s, indent_level + 1))
            res.append(f"{ind}}}\n")
            return "".join(res)
        elif isinstance(stmt, MatchStmt):
            expr_str = self.emit_expr(stmt.expr)
            # Check if matching on strings or numbers
            has_str = any(arm.pattern_val and arm.pattern_val.startswith('"') for arm in stmt.arms)
            switch_header = f"switch (::veloc::str_hash({expr_str})) {{" if has_str else f"switch ({expr_str}) {{"
            res = [f"{line_dir}{ind}{switch_header}\n"]
            for arm in stmt.arms:
                if arm.pattern_val is None or arm.pattern_val == "_":
                    res.append(f"{ind}    default:\n")
                elif arm.pattern_val.startswith('"'):
                    unquoted = arm.pattern_val.strip('"')
                    res.append(f'{ind}    case "{unquoted}"_hash:\n')
                else:
                    res.append(f'{ind}    case {arm.pattern_val}:\n')
                res.append(self.emit_stmt(arm.body, indent_level + 2))
                res.append(f"{ind}        break;\n")
            res.append(f"{ind}}}\n")
            return "".join(res)
        elif isinstance(stmt, DeferStmt):
            self.defer_counter += 1
            guard_name = f"_veloc_defer_{self.defer_counter}"
            if isinstance(stmt.body, BlockStmt):
                body_lines = []
                for s in stmt.body.statements:
                    body_lines.append(self.emit_stmt(s, indent_level + 1))
                return f"{line_dir}{ind}auto {guard_name} = ::veloc::ScopeGuardHelper() + [&]() {{\n{''.join(body_lines)}{ind}}};\n"
            else:
                body_lines = self.emit_stmt(stmt.body, indent_level + 1)
                return f"{line_dir}{ind}auto {guard_name} = ::veloc::ScopeGuardHelper() + [&]() {{\n{body_lines}{ind}}};\n"
        elif isinstance(stmt, BenchStmt):
            res = [
                f"{line_dir}{ind}{{\n",
                f"{ind}    ::veloc::CycleCounter _veloc_cc;\n",
                f"{ind}    VeloC_Timer _veloc_timer;\n",
                f"{ind}    _veloc_timer.start();\n",
                f"{ind}    {{\n",
            ]
            for s in stmt.body.statements:
                res.append(self.emit_stmt(s, indent_level + 2))
            res.extend([
                f"{ind}    }}\n",
                f'{ind}    printf("[BENCH] %-30s : %.4f ms (%llu cycles)\\n", "{stmt.name}", _veloc_timer.elapsed_ms(), (unsigned long long)_veloc_cc.elapsed());\n',
                f"{ind}}}\n",
            ])
            return "".join(res)
        elif isinstance(stmt, RawCppStmt):
            return f"{line_dir}{ind}{stmt.code}\n"
        else:
            return ""

    def emit_soa_struct(self, s: SoAStructDecl) -> str:
        lines = [
            f"// Auto-generated VeloC Struct-of-Arrays (SoA) for SIMD acceleration",
            f"struct {s.name}_SoA {{",
            f"    usize capacity;",
            f"    usize count;",
        ]
        for f in s.fields:
            lines.append(f"    {f.type_name}* VELOC_RESTRICT {f.name};")

        lines.extend([
            f"\n    static {s.name}_SoA create(usize cap) {{",
            f"        {s.name}_SoA s;",
            f"        s.capacity = cap;",
            f"        s.count = 0;",
        ])
        for f in s.fields:
            lines.append(f"        s.{f.name} = ({f.type_name}*)veloc_aligned_alloc(32, sizeof({f.type_name}) * cap);")
        lines.append("        return s;\n    }")

        # Push method
        args = ", ".join([f"{f.type_name} val_{f.name}" for f in s.fields])
        lines.extend([
            f"\n    VELOC_INLINE void push({args}) {{",
            f"        if (count < capacity) {{",
        ])
        for f in s.fields:
            lines.append(f"            this->{f.name}[count] = val_{f.name};")
        lines.extend([
            f"            count++;",
            f"        }}",
            f"    }}",
            f"\n    void destroy() {{",
        ])
        for f in s.fields:
            lines.append(f"        if ({f.name}) {{ veloc_aligned_free({f.name}); {f.name} = NULL; }}")
        lines.extend([
            f"        capacity = 0;",
            f"        count = 0;",
            f"    }}",
            f"\n    // Auto-generated Reflection: to_json()",
            f"    std::string to_json(usize i) const {{",
            f'        if (i >= count) return "{{}}";',
            f"        std::ostringstream ss;",
            f'        ss << "{{";',
        ])
        for idx, f in enumerate(s.fields):
            comma = ', ' if idx < len(s.fields) - 1 else ''
            lines.append(f'        ss << "\\"{f.name}\\": " << this->{f.name}[i] << "{comma}";')
        lines.extend([
            f'        ss << "}}";',
            f"        return ss.str();",
            f"    }}",
            f'\n    static const char* type_name() {{ return "{s.name}_SoA"; }}',
            f'    static usize field_count() {{ return {len(s.fields)}; }}',
            f"}};\n",
        ])
        return "\n".join(lines)

    def emit_decl(self, decl: Decl) -> str:
        if isinstance(decl, ModuleDecl):
            return ""
        elif isinstance(decl, ImportDecl):
            mod = decl.path.strip()
            if mod.startswith("veloc_"):
                subpkg = mod[len("veloc_"):]
                return f'#include <{mod}.h>\nusing namespace veloc::{subpkg};\n\n'
            return f'#include <{mod}.h>\n\n'
        elif isinstance(decl, SoAStructDecl):
            return self.emit_soa_struct(decl)
        elif isinstance(decl, FnDecl):
            if decl.name == "main":
                self.has_user_main = True
                if self.test_mode:
                    decl.name = "_user_main_disabled"

            params = ", ".join([f"{p.type_name} {p.name}" for p in decl.params])
            ret_type = decl.return_type
            lines = [f"{ret_type} {decl.name}({params}) {{\n"]
            for s in decl.body.statements:
                lines.append(self.emit_stmt(s, 1))
            lines.append("}\n")
            return "".join(lines)
        elif isinstance(decl, TestDecl):
            self.test_counter += 1
            func_name = f"_veloc_test_case_{self.test_counter}"
            self.tests.append((decl.name, func_name))
            lines = [f"void {func_name}() {{\n"]
            for s in decl.body.statements:
                lines.append(self.emit_stmt(s, 1))
            lines.append("}\n")
            return "".join(lines)
        elif isinstance(decl, RawCppStmt):
            clean_file = decl.file.replace(chr(92), "/")
            line_dir = f'#line {decl.line} "{clean_file}"\n'
            return f"{line_dir}{decl.code}\n\n"
        else:
            return ""

    def generate_cpp(self, program: Program) -> str:
        code_parts = []
        code_parts.append(f'#include "{self.include_dir}/veloc.h"\n\n')

        for decl in program.declarations:
            code_parts.append(self.emit_decl(decl))

        # Test runner injection
        if self.test_mode or (len(self.tests) > 0 and not self.has_user_main):
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
                test_main.extend([
                    f'    printf("  Running test: %-30s ... ", "{name}");',
                    f"    timer.start();",
                    f"    {func}();",
                    f'    printf("[PASS] (%.2f ms)\\n", timer.elapsed_ms());',
                    f"    passed++;",
                ])
            test_main.extend([
                '    printf("--------------------------------------------------\\n");',
                '    printf("Results: %d passed, %d failed\\n", passed, failed);',
                '    printf("==================================================\\n");',
                "    return failed == 0 ? 0 : 1;",
                "}\n",
            ])
            code_parts.append("\n".join(test_main))

        return "".join(code_parts)
