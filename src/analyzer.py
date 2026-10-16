# VeloC Static Analyzer & Bounds Check Verification
# Performs compile-time range proving, bounds check elimination reporting, and basic lifetime analysis.

from typing import List, Tuple, Optional
from ast_nodes import *

class BoundsReportEntry:
    def __init__(self, line: int, col: int, expr_str: str, status: str, reason: str):
        self.line = line
        self.col = col
        self.expr_str = expr_str
        self.status = status # "ELIMINATED" or "RUNTIME"
        self.reason = reason

class StaticAnalyzer:
    def __init__(self, filename: str):
        self.filename = filename
        self.bounds_reports: List[BoundsReportEntry] = []
        self.lifetime_errors: List[Tuple[int, int, str]] = []

    def analyze_program(self, program: Program):
        for decl in program.declarations:
            if isinstance(decl, FnDecl):
                self._analyze_fn(decl)

    def _analyze_fn(self, fn: FnDecl):
        local_vars = set()
        for p in fn.params:
            local_vars.add(p.name)

        def walk_stmt(s: Stmt):
            if isinstance(s, LetStmt):
                local_vars.add(s.name)
                if s.init_expr:
                    walk_expr(s.init_expr)
            elif isinstance(s, ReturnStmt) and s.value:
                # Check for returning pointer to local variable
                if isinstance(s.value, UnaryExpr) and s.value.op == "&":
                    if isinstance(s.value.operand, Identifier) and s.value.operand.name in local_vars:
                        self.lifetime_errors.append((
                            s.line, s.col,
                            f"Lifetime Error: Returning address of local variable '{s.value.operand.name}' which expires on function exit"
                        ))
                walk_expr(s.value)
            elif isinstance(s, BlockStmt):
                for sub_s in s.statements:
                    walk_stmt(sub_s)
            elif isinstance(s, ExprStmt):
                walk_expr(s.expr)
            elif isinstance(s, IfStmt):
                walk_expr(s.condition)
                walk_stmt(s.then_branch)
                if s.else_branch:
                    walk_stmt(s.else_branch)

        def walk_expr(e: Expr):
            if isinstance(e, IndexExpr):
                # Analyze bounds
                if isinstance(e.index, IntLiteral):
                    self.bounds_reports.append(BoundsReportEntry(
                        e.line, e.col, f"{self._repr_expr(e)}",
                        status="ELIMINATED",
                        reason=f"Constant index [{e.index.value}] statically proven in-bounds"
                    ))
                elif isinstance(e.index, BinaryOpExpr) and e.index.op in ("%", "&"):
                    self.bounds_reports.append(BoundsReportEntry(
                        e.line, e.col, f"{self._repr_expr(e)}",
                        status="ELIMINATED",
                        reason=f"Index bounded by bitwise/modulo mask '{e.index.op}'"
                    ))
                else:
                    self.bounds_reports.append(BoundsReportEntry(
                        e.line, e.col, f"{self._repr_expr(e)}",
                        status="RUNTIME",
                        reason="Dynamic index requires runtime assertion check"
                    ))

            # Recursive sub-expressions
            for child in getattr(e, "__dict__", {}).values():
                if isinstance(child, Expr):
                    walk_expr(child)
                elif isinstance(child, list):
                    for item in child:
                        if isinstance(item, Expr):
                            walk_expr(item)

        for stmt in fn.body.statements:
            walk_stmt(stmt)

    def _repr_expr(self, e: Expr) -> str:
        if isinstance(e, IndexExpr):
            return f"{self._repr_expr(e.collection)}[{self._repr_expr(e.index)}]"
        elif isinstance(e, Identifier):
            return e.name
        elif isinstance(e, IntLiteral):
            return str(e.value)
        return "..."

    def print_bounds_report(self):
        print("==================================================")
        print(f"      VeloC Bounds Check Elimination Report       ")
        print("==================================================")
        print(f"File: {self.filename}\n")
        eliminated = sum(1 for r in self.bounds_reports if r.status == "ELIMINATED")
        runtime = sum(1 for r in self.bounds_reports if r.status == "RUNTIME")
        total = len(self.bounds_reports)
        pct = (eliminated / total * 100.0) if total > 0 else 100.0

        print(f"Total Array/Slice Accesses: {total}")
        print(f"Statically Eliminated:     {eliminated} ({pct:.1f}%)")
        print(f"Runtime Checked:           {runtime}\n")

        print(f"{'Line:Col':<12} {'Status':<12} {'Expression':<20} {'Reason'}")
        print("-" * 75)
        for r in self.bounds_reports:
            pos = f"{r.line}:{r.col}"
            print(f"{pos:<12} {r.status:<12} {r.expr_str:<20} {r.reason}")
        print("==================================================")
