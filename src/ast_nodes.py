# VeloC AST (Abstract Syntax Tree) Node Definitions
from dataclasses import dataclass, field
from typing import List, Optional, Any, Tuple

@dataclass
class ASTNode:
    line: int = 1
    col: int = 1
    file: str = "<stdin>"

# ==========================================
# Expressions
# ==========================================
@dataclass
class Expr(ASTNode):
    pass

@dataclass
class IntLiteral(Expr):
    value: str = "0"

@dataclass
class FloatLiteral(Expr):
    value: str = "0.0"

@dataclass
class StringLiteral(Expr):
    value: str = ""

@dataclass
class FStringLiteral(Expr):
    raw_value: str = ""

@dataclass
class CharLiteral(Expr):
    value: str = ""

@dataclass
class BoolLiteral(Expr):
    value: bool = False

@dataclass
class NullLiteral(Expr):
    pass

@dataclass
class Identifier(Expr):
    name: str = ""

@dataclass
class BinaryExpr(Expr):
    left: Expr = field(default_factory=Expr)
    op: str = ""
    right: Expr = field(default_factory=Expr)

@dataclass
class UnaryExpr(Expr):
    op: str = ""
    operand: Expr = field(default_factory=Expr)

@dataclass
class CastExpr(Expr): # expr as Type
    expr: Expr = field(default_factory=Expr)
    target_type: str = ""

@dataclass
class AssertNonNullExpr(Expr): # opt!
    expr: Expr = field(default_factory=Expr)

@dataclass
class TryExpr(Expr): # expr?
    expr: Expr = field(default_factory=Expr)

@dataclass
class CallExpr(Expr):
    callee: Expr = field(default_factory=Expr)
    args: List[Expr] = field(default_factory=list)

@dataclass
class MemberAccessExpr(Expr):
    object: Expr = field(default_factory=Expr)
    member: str = ""

@dataclass
class IndexExpr(Expr):
    collection: Expr = field(default_factory=Expr)
    index: Expr = field(default_factory=Expr)

@dataclass
class LambdaExpr(Expr): # |a, b| => expr
    params: List[str] = field(default_factory=list)
    body: Expr = field(default_factory=Expr)

@dataclass
class PipeExpr(Expr): # a |> b
    left: Expr = field(default_factory=Expr)
    right: Expr = field(default_factory=Expr)

@dataclass
class CoalesceExpr(Expr): # a ?? b
    left: Expr = field(default_factory=Expr)
    right: Expr = field(default_factory=Expr)

@dataclass
class TupleExpr(Expr):
    elements: List[Expr] = field(default_factory=list)

# ==========================================
# Statements
# ==========================================
@dataclass
class Stmt(ASTNode):
    pass

@dataclass
class ExprStmt(Stmt):
    expr: Expr = field(default_factory=Expr)

@dataclass
class BlockStmt(Stmt):
    statements: List[Stmt] = field(default_factory=list)

@dataclass
class LetStmt(Stmt):
    name: str = ""
    type_annotation: Optional[str] = None
    is_mut: bool = False
    init_expr: Optional[Expr] = None
    destructure: Optional[List[str]] = None

@dataclass
class ReturnStmt(Stmt):
    value: Optional[Expr] = None

@dataclass
class IfStmt(Stmt):
    condition: Expr = field(default_factory=Expr)
    then_branch: BlockStmt = field(default_factory=BlockStmt)
    else_branch: Optional[Stmt] = None

@dataclass
class IfLetStmt(Stmt):
    pattern_type: str = "Some" # "Some" or "Ok"
    var_name: str = ""
    expr: Expr = field(default_factory=Expr)
    then_branch: BlockStmt = field(default_factory=BlockStmt)
    else_branch: Optional[Stmt] = None

@dataclass
class WhileStmt(Stmt):
    condition: Expr = field(default_factory=Expr)
    body: BlockStmt = field(default_factory=BlockStmt)

@dataclass
class WhileLetStmt(Stmt):
    pattern_type: str = "Some" # "Some" or "Ok"
    var_name: str = ""
    expr: Expr = field(default_factory=Expr)
    body: BlockStmt = field(default_factory=BlockStmt)

@dataclass
class ForInStmt(Stmt):
    var_name: str = ""
    iter_expr: Expr = field(default_factory=Expr)
    body: BlockStmt = field(default_factory=BlockStmt)
    is_mut: bool = False

@dataclass
class ForEnumerateStmt(Stmt):
    idx_var: str = ""
    val_var: str = ""
    iter_expr: Expr = field(default_factory=Expr)
    body: BlockStmt = field(default_factory=BlockStmt)
    is_mut: bool = False

@dataclass
class MatchArm(ASTNode):
    pattern_val: Optional[str] = None # None means wildcard '_'
    body: Stmt = field(default_factory=Stmt)

@dataclass
class MatchStmt(Stmt):
    expr: Expr = field(default_factory=Expr)
    arms: List[MatchArm] = field(default_factory=list)

@dataclass
class DeferStmt(Stmt):
    body: Stmt = field(default_factory=Stmt)

@dataclass
class BenchStmt(Stmt):
    name: str = ""
    body: BlockStmt = field(default_factory=BlockStmt)

@dataclass
class RawCppStmt(Stmt):
    code: str = ""

# ==========================================
# Declarations / Top-Level
# ==========================================
@dataclass
class Decl(ASTNode):
    pass

@dataclass
class SoAField(ASTNode):
    type_name: str = ""
    name: str = ""

@dataclass
class SoAStructDecl(Decl):
    name: str = ""
    fields: List[SoAField] = field(default_factory=list)

@dataclass
class FnParam(ASTNode):
    name: str = ""
    type_name: str = ""

@dataclass
class FnDecl(Decl):
    name: str = ""
    params: List[FnParam] = field(default_factory=list)
    return_type: str = "void"
    body: BlockStmt = field(default_factory=BlockStmt)
    is_pub: bool = False

@dataclass
class TestDecl(Decl):
    name: str = ""
    body: BlockStmt = field(default_factory=BlockStmt)

@dataclass
class ModuleDecl(Decl):
    name: str = ""

@dataclass
class ImportDecl(Decl):
    path: str = ""

@dataclass
class Program(ASTNode):
    declarations: List[Decl] = field(default_factory=list)
