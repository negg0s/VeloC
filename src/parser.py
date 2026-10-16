# VeloC Recursive Descent + Pratt Parser
# Supports pure VeloC declarations and statements as well as embedded C++ blocks.

from typing import List, Optional, Tuple, Dict, Any
from lexer import Token, TokenType, Lexer, LexerError
from ast_nodes import *
from diagnostics import DiagnosticReporter, Diagnostic, DiagnosticCode
from codegen import CppCodegen

# Operator Precedence for Pratt Parser
PRECEDENCE: Dict[TokenType, int] = {
    TokenType.PIPE: 10,        # |>
    TokenType.COALESCE: 20,    # ??
    TokenType.OR: 30,          # ||
    TokenType.AND: 40,         # &&
    TokenType.BIT_OR: 50,      # |
    TokenType.BIT_XOR: 60,     # ^
    TokenType.BIT_AND: 70,     # &
    TokenType.EQEQ: 80,        # ==
    TokenType.NEQ: 80,         # !=
    TokenType.LT: 90,          # <
    TokenType.LTE: 90,         # <=
    TokenType.GT: 90,          # >
    TokenType.GTE: 90,         # >=
    TokenType.SHL: 100,        # <<
    TokenType.SHR: 100,        # >>
    TokenType.PLUS: 110,       # +
    TokenType.MINUS: 110,      # -
    TokenType.STAR: 120,       # *
    TokenType.SLASH: 120,      # /
    TokenType.PERCENT: 120,    # %
    TokenType.AS: 130,         # as Type
    # Postfix / Primary operators (handled specifically)
    TokenType.DOT: 150,        # .
    TokenType.LBRACKET: 150,   # [
    TokenType.LPAREN: 150,     # (
    TokenType.NOT: 160,        # opt! postfix unwrap
}

class ParseError(Exception):
    def __init__(self, message: str, token: Token, code: DiagnosticCode = DiagnosticCode.E0001, help_text: Optional[str] = None):
        super().__init__(f"{token.file}:{token.line}:{token.col}: error [{code.value}]: {message}")
        self.message = message
        self.token = token
        self.code = code
        self.help_text = help_text

class Parser:
    def __init__(self, tokens: List[Token], source_code: str = "", filename: str = "<stdin>"):
        self.tokens = tokens
        self.source_code = source_code
        self.filename = filename
        self.pos = 0
        self.diagnostics = DiagnosticReporter(source_code, filename)

    def current(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def peek(self, offset: int = 1) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]

    def advance(self) -> Token:
        tok = self.current()
        if self.pos < len(self.tokens):
            self.pos += 1
        return tok

    def check(self, token_type: TokenType) -> bool:
        return self.current().type == token_type

    def match(self, *token_types: TokenType) -> bool:
        for tt in token_types:
            if self.check(tt):
                self.advance()
                return True
        return False

    def expect(self, token_type: TokenType, err_msg: str, code: DiagnosticCode = DiagnosticCode.E0001) -> Token:
        if self.check(token_type):
            return self.advance()
        tok = self.current()
        raise ParseError(f"{err_msg}, got '{tok.value}'", tok, code)

    # ==========================================
    # Pratt Expression Parser
    # ==========================================
    def parse_expr(self, min_prec: int = 0) -> Expr:
        # Check for Lambda expression: |a, b| => expr
        if self.check(TokenType.BIT_OR):
            # Probe if this is a lambda: |id, ...| =>
            probe_idx = self.pos + 1
            is_lambda = False
            params = []
            while probe_idx < len(self.tokens):
                t = self.tokens[probe_idx]
                if t.type == TokenType.IDENT:
                    params.append(t.value)
                    probe_idx += 1
                    if probe_idx < len(self.tokens) and self.tokens[probe_idx].type == TokenType.COMMA:
                        probe_idx += 1
                        continue
                elif t.type == TokenType.BIT_OR:
                    if probe_idx + 1 < len(self.tokens) and self.tokens[probe_idx + 1].type == TokenType.ARROW:
                        is_lambda = True
                    break
                else:
                    break

            if is_lambda:
                start_tok = self.advance() # |
                lambda_params = []
                while not self.check(TokenType.BIT_OR) and not self.check(TokenType.EOF):
                    param_tok = self.expect(TokenType.IDENT, "Expected parameter identifier in lambda")
                    lambda_params.append(param_tok.value)
                    if self.check(TokenType.COMMA):
                        self.advance()
                self.expect(TokenType.BIT_OR, "Expected '|' closing lambda parameter list")
                self.expect(TokenType.ARROW, "Expected '=>' in lambda definition")
                body = self.parse_expr(0)
                return LambdaExpr(start_tok.line, start_tok.col, self.filename, params=lambda_params, body=body)

        left = self.parse_prefix()

        while True:
            # Postfix non-null unwrap: expr!
            if self.check(TokenType.NOT) and min_prec <= PRECEDENCE[TokenType.NOT]:
                # In VeloC, postfix '!' is opt! (unwrap), only if immediately following operand
                op_tok = self.advance()
                left = AssertNonNullExpr(op_tok.line, op_tok.col, self.filename, expr=left)
                continue

            tok = self.current()
            prec = PRECEDENCE.get(tok.type, 0)
            if prec <= min_prec:
                break

            op_tok = self.advance()

            # Handle Cast: expr as TargetType
            if op_tok.type == TokenType.AS:
                # Read target type (e.g. f32, usize, int, etc.)
                type_tok = self.expect(TokenType.IDENT, "Expected target type after 'as'")
                left = CastExpr(op_tok.line, op_tok.col, self.filename, expr=left, target_type=type_tok.value)
                continue

            # Handle Pipe: left |> right
            if op_tok.type == TokenType.PIPE:
                right = self.parse_expr(prec)
                left = PipeExpr(op_tok.line, op_tok.col, self.filename, left=left, right=right)
                continue

            # Handle Coalesce: left ?? right
            if op_tok.type == TokenType.COALESCE:
                right = self.parse_expr(prec - 1) # right-associative
                left = CoalesceExpr(op_tok.line, op_tok.col, self.filename, left=left, right=right)
                continue

            # Member access: left.member
            if op_tok.type == TokenType.DOT:
                member_tok = self.expect(TokenType.IDENT, "Expected member name after '.'")
                left = MemberAccessExpr(op_tok.line, op_tok.col, self.filename, object=left, member=member_tok.value)
                continue

            # Indexing: left[index]
            if op_tok.type == TokenType.LBRACKET:
                idx_expr = self.parse_expr(0)
                self.expect(TokenType.RBRACKET, "Expected ']' after array index")
                left = IndexExpr(op_tok.line, op_tok.col, self.filename, collection=left, index=idx_expr)
                continue

            # Function call: left(args)
            if op_tok.type == TokenType.LPAREN:
                args = []
                if not self.check(TokenType.RPAREN):
                    while True:
                        args.append(self.parse_expr(0))
                        if not self.match(TokenType.COMMA):
                            break
                self.expect(TokenType.RPAREN, "Expected ')' after function arguments")
                left = CallExpr(op_tok.line, op_tok.col, self.filename, callee=left, args=args)
                continue

            # Standard binary expression
            right = self.parse_expr(prec)
            left = BinaryExpr(op_tok.line, op_tok.col, self.filename, left=left, op=op_tok.value, right=right)

        return left

    def parse_prefix(self) -> Expr:
        tok = self.current()

        # Unary operators: +, -, !, ~, *
        if tok.type in (TokenType.PLUS, TokenType.MINUS, TokenType.NOT, TokenType.BIT_NOT, TokenType.STAR):
            self.advance()
            operand = self.parse_expr(140)
            return UnaryExpr(tok.line, tok.col, self.filename, op=tok.value, operand=operand)

        # Parenthesized expression, C-style cast: (f32*)expr, or Tuple: (a, b)
        if tok.type == TokenType.LPAREN:
            # Check if this is a C-style cast like (f32*), (i32), (const char*)
            save_pos = self.pos
            self.advance() # (
            type_tokens = []
            while not self.check(TokenType.RPAREN) and not self.check(TokenType.EOF) and len(type_tokens) < 5:
                t = self.advance()
                type_tokens.append(t)
            if self.check(TokenType.RPAREN):
                self.advance() # )
                # If next token can begin an expression or unary operator
                if self.check(TokenType.IDENT) or self.check(TokenType.LPAREN) or self.check(TokenType.INT_LIT) or self.check(TokenType.FLOAT_LIT) or self.check(TokenType.STAR) or self.check(TokenType.PLUS) or self.check(TokenType.MINUS):
                    type_str = "".join(t.value for t in type_tokens)
                    try:
                        operand = self.parse_expr(140)
                        return CastExpr(tok.line, tok.col, self.filename, expr=operand, target_type=type_str)
                    except Exception:
                        pass
            # Backtrack if not a cast
            self.pos = save_pos
            self.advance() # (
            first = self.parse_expr(0)
            if self.match(TokenType.COMMA):
                # Tuple
                elems = [first]
                while not self.check(TokenType.RPAREN) and not self.check(TokenType.EOF):
                    elems.append(self.parse_expr(0))
                    if not self.match(TokenType.COMMA):
                        break
                self.expect(TokenType.RPAREN, "Expected ')' after tuple elements")
                return TupleExpr(tok.line, tok.col, self.filename, elements=elems)
            else:
                self.expect(TokenType.RPAREN, "Expected ')' after parenthesized expression")
                return first

        # C++ lambda expression: [](params) { ... } or [&]() { ... }
        if tok.type == TokenType.LBRACKET:
            save_pos = self.pos
            self.advance() # [
            # Check capture list: &, =, this, or empty
            while not self.check(TokenType.RBRACKET) and not self.check(TokenType.EOF):
                self.advance()
            if self.check(TokenType.RBRACKET):
                self.advance() # ]
                if self.check(TokenType.LPAREN) or self.check(TokenType.LBRACE):
                    # Capture parameters and body as a lambda
                    lambda_toks = self.tokens[save_pos:self.pos]
                    if self.check(TokenType.LPAREN):
                        self.advance() # (
                        while not self.check(TokenType.RPAREN) and not self.check(TokenType.EOF):
                            lambda_toks.append(self.advance())
                        if self.check(TokenType.RPAREN):
                            lambda_toks.append(self.advance()) # )
                    if self.check(TokenType.LBRACE):
                        body_stmt = self.parse_block()
                        body_code = CppCodegen("<include>").emit_stmt(body_stmt)
                        head_code = " ".join(t.value for t in lambda_toks)
                        return Identifier(tok.line, tok.col, self.filename, name=f"{head_code} {body_code}")
            self.pos = save_pos

        # Literals
        if tok.type == TokenType.INT_LIT:
            self.advance()
            return IntLiteral(tok.line, tok.col, self.filename, value=tok.value)

        if tok.type == TokenType.FLOAT_LIT:
            self.advance()
            return FloatLiteral(tok.line, tok.col, self.filename, value=tok.value)

        if tok.type == TokenType.STRING_LIT:
            self.advance()
            return StringLiteral(tok.line, tok.col, self.filename, value=tok.value)

        if tok.type == TokenType.FSTRING_LIT:
            self.advance()
            return FStringLiteral(tok.line, tok.col, self.filename, raw_value=tok.value)

        if tok.type == TokenType.CHAR_LIT:
            self.advance()
            return CharLiteral(tok.line, tok.col, self.filename, value=tok.value)

        if tok.type == TokenType.TRUE:
            self.advance()
            return BoolLiteral(tok.line, tok.col, self.filename, value=True)

        if tok.type == TokenType.FALSE:
            self.advance()
            return BoolLiteral(tok.line, tok.col, self.filename, value=False)

        if tok.type == TokenType.NULL:
            self.advance()
            return NullLiteral(tok.line, tok.col, self.filename)

        # Identifiers (including template/namespace scope e.g. Result<f32, const char*>::Ok)
        if tok.type in (TokenType.IDENT, TokenType.SOME, TokenType.OK, TokenType.ERR, TokenType.NONE):
            name_parts = [tok.value]
            self.advance()
            while True:
                if self.check(TokenType.LT):
                    # Potential template instantiation in expression context: SmallVec<i32, 8>() or Result<T>::Ok
                    save_pos = self.pos
                    try:
                        self.advance() # <
                        depth = 1
                        tmpl_parts = []
                        while depth > 0 and not self.check(TokenType.EOF) and not self.check(TokenType.SEMICOLON):
                            t = self.advance()
                            if t.type == TokenType.LT: depth += 1
                            elif t.type == TokenType.GT: depth -= 1
                            if depth > 0: tmpl_parts.append(t.value)
                        
                        # A valid template must end with depth == 0 and be followed by '(', '{', '::' or '.'
                        if depth == 0 and (self.check(TokenType.LPAREN) or self.check(TokenType.LBRACE) or self.check(TokenType.COLON_COLON) or self.check(TokenType.DOT)):
                            # Reconstruct template args with proper spacing between identifier words
                            formatted_parts = []
                            for i, t in enumerate(tmpl_parts):
                                if i > 0:
                                    prev = tmpl_parts[i-1]
                                    if (prev.isalnum() or prev == '_') and (t.isalnum() or t == '_'):
                                        formatted_parts.append(" ")
                                formatted_parts.append(t)
                            tmpl_str = "".join(formatted_parts)
                            name_parts[-1] += f"<{tmpl_str}>"
                        else:
                            # Not a template qualifier, backtrack
                            self.pos = save_pos
                            break
                    except Exception:
                        self.pos = save_pos
                        break

                if self.check(TokenType.COLON_COLON):
                    self.advance() # ::
                    next_tok = self.advance()
                    name_parts.append(next_tok.value)
                else:
                    break

            full_name = "::".join(name_parts)
            return Identifier(tok.line, tok.col, self.filename, name=full_name)

        raise ParseError(f"Unexpected token in expression: '{tok.value}'", tok, DiagnosticCode.E0001)

    # ==========================================
    # Statement Parsing
    # ==========================================
    def parse_stmt(self) -> Stmt:
        tok = self.current()

        # Let statement: let [mut] [(a, b) | x[: type]] [= expr];
        if tok.type == TokenType.LET:
            return self.parse_let_stmt()

        # Return statement
        if tok.type == TokenType.RETURN:
            self.advance()
            if self.check(TokenType.SEMICOLON):
                self.advance()
                return ReturnStmt(tok.line, tok.col, self.filename, value=None)
            val = self.parse_expr(0)
            self.expect(TokenType.SEMICOLON, "Expected ';' after return expression")
            return ReturnStmt(tok.line, tok.col, self.filename, value=val)

        # Defer statement
        if tok.type == TokenType.DEFER:
            self.advance()
            if self.check(TokenType.LBRACE):
                body = self.parse_block()
                return DeferStmt(tok.line, tok.col, self.filename, body=body)
            else:
                stmt = self.parse_stmt()
                return DeferStmt(tok.line, tok.col, self.filename, body=stmt)

        # Bench statement: bench "name" { ... }
        if tok.type == TokenType.BENCH:
            self.advance()
            name_tok = self.expect(TokenType.STRING_LIT, "Expected benchmark name as string literal")
            body = self.parse_block()
            return BenchStmt(tok.line, tok.col, self.filename, name=name_tok.value, body=body)

        # If statement & If let
        if tok.type == TokenType.IF:
            return self.parse_if_stmt()

        # While statement & While let
        if tok.type == TokenType.WHILE:
            return self.parse_while_stmt()

        # For loop
        if tok.type == TokenType.FOR:
            return self.parse_for_stmt()

        # Match statement
        if tok.type == TokenType.MATCH:
            return self.parse_match_stmt()

        # Block statement { ... }
        if tok.type == TokenType.LBRACE:
            return self.parse_block()

        # Raw C++ / standard statement fallback
        # If it doesn't match a high-level VeloC statement, capture until ';' or block
        return self.parse_raw_or_expr_stmt()

    def parse_let_stmt(self) -> LetStmt:
        start_tok = self.advance() # 'let'
        is_mut = False
        if self.check(TokenType.MUT):
            self.advance()
            is_mut = True

        # Check for destructuring: let (a, b) = ...
        if self.check(TokenType.LPAREN):
            self.advance()
            names = []
            while not self.check(TokenType.RPAREN) and not self.check(TokenType.EOF):
                name_tok = self.expect(TokenType.IDENT, "Expected identifier in destructuring")
                names.append(name_tok.value)
                if not self.match(TokenType.COMMA):
                    break
            self.expect(TokenType.RPAREN, "Expected ')' after destructuring list")
            self.expect(TokenType.EQ, "Expected '=' in destructuring let")
            init_expr = self.parse_expr(0)
            self.expect(TokenType.SEMICOLON, "Expected ';' after let statement")
            return LetStmt(start_tok.line, start_tok.col, self.filename, name="", is_mut=is_mut,
                           init_expr=init_expr, destructure=names)

        # Single variable: let [mut] name [: type] [= expr];
        name_tok = self.expect(TokenType.IDENT, "Expected variable name after 'let'")
        type_annot = None
        if self.match(TokenType.COLON):
            type_tok = self.expect(TokenType.IDENT, "Expected type name after ':' in let declaration")
            type_annot = type_tok.value
        elif self.check(TokenType.IDENT) and self.peek().type == TokenType.EQ:
            # Syntax: let type name = ...
            type_annot = name_tok.value
            name_tok = self.advance()

        init_expr = None
        if self.match(TokenType.EQ):
            init_expr = self.parse_expr(0)

        self.expect(TokenType.SEMICOLON, "Expected ';' after let statement")
        return LetStmt(start_tok.line, start_tok.col, self.filename, name=name_tok.value,
                       type_annotation=type_annot, is_mut=is_mut, init_expr=init_expr)

    def parse_if_stmt(self) -> Stmt:
        start_tok = self.advance() # 'if'
        # Check for if let Some(var) = expr or if let Ok(var) = expr
        if self.check(TokenType.LET):
            self.advance() # let
            pat_tok = self.current()
            if pat_tok.type in (TokenType.SOME, TokenType.OK):
                pat_type = pat_tok.value
                self.advance()
                self.expect(TokenType.LPAREN, "Expected '(' after pattern")
                var_tok = self.expect(TokenType.IDENT, "Expected variable name in pattern")
                self.expect(TokenType.RPAREN, "Expected ')' after variable name")
                self.expect(TokenType.EQ, "Expected '=' in if let statement")
                expr = self.parse_expr(0)
                then_b = self.parse_block()
                else_b = None
                if self.match(TokenType.ELSE):
                    else_b = self.parse_block() if self.check(TokenType.LBRACE) else self.parse_if_stmt()
                return IfLetStmt(start_tok.line, start_tok.col, self.filename, pattern_type=pat_type,
                                 var_name=var_tok.value, expr=expr, then_branch=then_b, else_branch=else_b)

        # Standard if
        has_paren = self.match(TokenType.LPAREN)
        cond = self.parse_expr(0)
        if has_paren:
            self.expect(TokenType.RPAREN, "Expected ')' after if condition")

        if self.check(TokenType.LBRACE):
            then_branch = self.parse_block()
        else:
            single_stmt = self.parse_stmt()
            then_branch = BlockStmt(single_stmt.line, single_stmt.col, self.filename, statements=[single_stmt])

        else_branch = None
        if self.match(TokenType.ELSE):
            if self.check(TokenType.IF):
                else_branch = self.parse_if_stmt()
            elif self.check(TokenType.LBRACE):
                else_branch = self.parse_block()
            else:
                else_branch = self.parse_stmt()

        return IfStmt(start_tok.line, start_tok.col, self.filename, condition=cond,
                      then_branch=then_branch, else_branch=else_branch)

    def parse_while_stmt(self) -> Stmt:
        start_tok = self.advance() # 'while'
        if self.check(TokenType.LET):
            self.advance()
            pat_tok = self.current()
            if pat_tok.type in (TokenType.SOME, TokenType.OK):
                pat_type = pat_tok.value
                self.advance()
                self.expect(TokenType.LPAREN, "Expected '(' after pattern")
                var_tok = self.expect(TokenType.IDENT, "Expected variable name in pattern")
                self.expect(TokenType.RPAREN, "Expected ')' after variable name")
                self.expect(TokenType.EQ, "Expected '=' in while let statement")
                expr = self.parse_expr(0)
                body = self.parse_block()
                return WhileLetStmt(start_tok.line, start_tok.col, self.filename, pattern_type=pat_type,
                                    var_name=var_tok.value, expr=expr, body=body)

        has_paren = self.match(TokenType.LPAREN)
        cond = self.parse_expr(0)
        if has_paren:
            self.expect(TokenType.RPAREN, "Expected ')' after while condition")

        body = self.parse_block()
        return WhileStmt(start_tok.line, start_tok.col, self.filename, condition=cond, body=body)

    def parse_for_stmt(self) -> Stmt:
        start_tok = self.advance() # 'for'
        has_paren = self.match(TokenType.LPAREN)

        # Case A: for (let [mut] (i, v) in enumerate(expr))
        # Case B: for (let [mut] v in expr)
        # Case C: raw C++ for loop: for (int i = 0; i < N; i++)
        if self.check(TokenType.LET):
            self.advance() # let
            is_mut = self.match(TokenType.MUT)

            if self.check(TokenType.LPAREN):
                # Destructured: (idx, val) in enumerate(expr)
                self.advance()
                idx_tok = self.expect(TokenType.IDENT, "Expected index identifier")
                self.expect(TokenType.COMMA, "Expected ',' in enumerate tuple")
                val_tok = self.expect(TokenType.IDENT, "Expected value identifier")
                self.expect(TokenType.RPAREN, "Expected ')'")
                self.expect(TokenType.IN, "Expected 'in' in for loop")

                # Parse iter expr: enumerate(expr) or expr
                iter_expr = self.parse_expr(0)
                if has_paren:
                    self.expect(TokenType.RPAREN, "Expected ')'")
                body = self.parse_block()
                return ForEnumerateStmt(start_tok.line, start_tok.col, self.filename,
                                       idx_var=idx_tok.value, val_var=val_tok.value,
                                       iter_expr=iter_expr, body=body, is_mut=is_mut)
            else:
                var_tok = self.expect(TokenType.IDENT, "Expected variable identifier in for loop")
                self.expect(TokenType.IN, "Expected 'in' in for loop")
                iter_expr = self.parse_expr(0)
                if has_paren:
                    self.expect(TokenType.RPAREN, "Expected ')'")
                body = self.parse_block()
                return ForInStmt(start_tok.line, start_tok.col, self.filename,
                                 var_name=var_tok.value, iter_expr=iter_expr, body=body, is_mut=is_mut)

        # Fallback to Raw C++ for loop
        raw_tokens = [start_tok]
        if has_paren:
            paren_depth = 1
            while paren_depth > 0 and not self.check(TokenType.EOF):
                t = self.advance()
                raw_tokens.append(t)
                if t.type == TokenType.LPAREN: paren_depth += 1
                elif t.type == TokenType.RPAREN: paren_depth -= 1

        body = self.parse_block()
        raw_header = " ".join(t.value for t in raw_tokens)
        body_cpp = CppCodegen("<include>").emit_stmt(body)
        return RawCppStmt(start_tok.line, start_tok.col, self.filename, code=f"{raw_header} {body_cpp}")

    def parse_match_stmt(self) -> MatchStmt:
        start_tok = self.advance() # 'match'
        has_paren = self.match(TokenType.LPAREN)
        target = self.parse_expr(0)
        if has_paren:
            self.expect(TokenType.RPAREN, "Expected ')' after match expression")

        self.expect(TokenType.LBRACE, "Expected '{' to start match body")
        arms = []
        while not self.check(TokenType.RBRACE) and not self.check(TokenType.EOF):
            # Pattern: string, int, or wildcard '_'
            arm_tok = self.current()
            pat_val = None
            if arm_tok.type == TokenType.STRING_LIT:
                pat_val = f'"{arm_tok.value}"'
                self.advance()
            elif arm_tok.type == TokenType.INT_LIT:
                pat_val = arm_tok.value
                self.advance()
            elif arm_tok.type == TokenType.IDENT and arm_tok.value == "_":
                pat_val = None # wildcard
                self.advance()
            else:
                raise ParseError(f"Expected match pattern (string, integer or '_'), got '{arm_tok.value}'", arm_tok, DiagnosticCode.E0001)

            self.expect(TokenType.ARROW, "Expected '=>' after match pattern")

            # Body can be block { ... } or single statement
            if self.check(TokenType.LBRACE):
                arm_body = self.parse_block()
            else:
                arm_body = self.parse_stmt()

            arms.append(MatchArm(arm_tok.line, arm_tok.col, self.filename, pattern_val=pat_val, body=arm_body))

        self.expect(TokenType.RBRACE, "Expected '}' closing match body")
        return MatchStmt(start_tok.line, start_tok.col, self.filename, expr=target, arms=arms)

    def parse_block(self) -> BlockStmt:
        start_tok = self.expect(TokenType.LBRACE, "Expected '{'")
        stmts = []
        while not self.check(TokenType.RBRACE) and not self.check(TokenType.EOF):
            stmts.append(self.parse_stmt())
        self.expect(TokenType.RBRACE, "Expected '}'")
        return BlockStmt(start_tok.line, start_tok.col, self.filename, statements=stmts)

    def parse_raw_or_expr_stmt(self) -> Stmt:
        start_tok = self.current()
        # Attempt to parse as high-level expression statement (e.g. function call, pipeline)
        save_pos = self.pos
        try:
            expr = self.parse_expr(0)
            if self.match(TokenType.SEMICOLON):
                return ExprStmt(start_tok.line, start_tok.col, self.filename, expr=expr)
        except Exception:
            pass

        # Backtrack and consume as Raw C++ statement up to semicolon
        self.pos = save_pos
        raw_tokens = []
        brace_depth = 0
        while not self.check(TokenType.EOF):
            t = self.advance()
            raw_tokens.append(t)
            if t.type == TokenType.LBRACE:
                brace_depth += 1
            elif t.type == TokenType.RBRACE:
                brace_depth -= 1
                if brace_depth <= 0:
                    break
            elif t.type == TokenType.SEMICOLON and brace_depth == 0:
                break

        raw_str = " ".join(t.value for t in raw_tokens)
        return RawCppStmt(start_tok.line, start_tok.col, self.filename, code=raw_str)

    # ==========================================
    # Top-Level Declarations
    # ==========================================
    def parse_program(self) -> Program:
        decls = []
        while not self.check(TokenType.EOF):
            decl = self.parse_decl()
            if decl:
                decls.append(decl)
        return Program(1, 1, self.filename, declarations=decls)

    def parse_decl(self) -> Optional[Decl]:
        tok = self.current()

        # Module: module Name;
        if tok.type == TokenType.MODULE:
            self.advance()
            mod_tok = self.expect(TokenType.IDENT, "Expected module name")
            self.expect(TokenType.SEMICOLON, "Expected ';' after module declaration")
            return ModuleDecl(tok.line, tok.col, self.filename, name=mod_tok.value)

        # Import: import Name;
        if tok.type == TokenType.IMPORT:
            self.advance()
            path_parts = []
            while not self.check(TokenType.SEMICOLON) and not self.check(TokenType.EOF):
                path_parts.append(self.advance().value)
            self.expect(TokenType.SEMICOLON, "Expected ';' after import")
            return ImportDecl(tok.line, tok.col, self.filename, path="".join(path_parts))

        # SoA Struct: soa struct Name { ... };
        if tok.type == TokenType.SOA:
            self.advance()
            self.expect(TokenType.STRUCT, "Expected 'struct' after 'soa'")
            name_tok = self.expect(TokenType.IDENT, "Expected struct name")
            self.expect(TokenType.LBRACE, "Expected '{' to start struct body")
            fields = []
            while not self.check(TokenType.RBRACE) and not self.check(TokenType.EOF):
                # field: type name;
                type_tok = self.advance()
                field_name_tok = self.expect(TokenType.IDENT, "Expected field name")
                self.expect(TokenType.SEMICOLON, "Expected ';' after field")
                fields.append(SoAField(type_tok.line, type_tok.col, self.filename,
                                       type_name=type_tok.value, name=field_name_tok.value))
            self.expect(TokenType.RBRACE, "Expected '}' closing struct")
            self.match(TokenType.SEMICOLON) # optional ';'
            return SoAStructDecl(tok.line, tok.col, self.filename, name=name_tok.value, fields=fields)

        # Test block: test "name" { ... }
        if tok.type == TokenType.TEST:
            self.advance()
            name_tok = self.expect(TokenType.STRING_LIT, "Expected test name as string literal")
            body = self.parse_block()
            return TestDecl(tok.line, tok.col, self.filename, name=name_tok.value, body=body)

        # Function: [pub] fn name(params) [-> ret] { ... }
        is_pub = False
        if tok.type == TokenType.PUB:
            is_pub = True
            self.advance()
            tok = self.current()

        if tok.type == TokenType.FN:
            start_tok = self.advance()
            name_tok = self.expect(TokenType.IDENT, "Expected function name")
            self.expect(TokenType.LPAREN, "Expected '(' for parameter list")
            params = []
            if not self.check(TokenType.RPAREN):
                while True:
                    # param: [type] name
                    type_part = []
                    while not self.check(TokenType.COMMA) and not self.check(TokenType.RPAREN) and not self.check(TokenType.EOF):
                        type_part.append(self.advance())
                    if len(type_part) == 1:
                        params.append(FnParam(type_part[0].line, type_part[0].col, self.filename,
                                              name=type_part[0].value, type_name="auto"))
                    elif len(type_part) >= 2:
                        name_p = type_part[-1]
                        type_str = " ".join(t.value for t in type_part[:-1])
                        params.append(FnParam(name_p.line, name_p.col, self.filename,
                                              name=name_p.value, type_name=type_str))
                    if not self.match(TokenType.COMMA):
                        break

            self.expect(TokenType.RPAREN, "Expected ')' after parameters")

            ret_type = "auto"
            if self.match(TokenType.THIN_ARROW):
                # Read return type until '{'
                ret_parts = []
                while not self.check(TokenType.LBRACE) and not self.check(TokenType.EOF):
                    ret_parts.append(self.advance().value)
                ret_type = " ".join(ret_parts)

            body = self.parse_block()
            return FnDecl(start_tok.line, start_tok.col, self.filename, name=name_tok.value,
                          params=params, return_type=ret_type, body=body, is_pub=is_pub)

        # Top-level C++ statement / block (e.g. #include, typedef, standard struct, global variable)
        # Parse until balanced block or semicolon
        raw_tokens = []
        brace_depth = 0
        while not self.check(TokenType.EOF):
            t = self.advance()
            raw_tokens.append(t)
            if t.type == TokenType.LBRACE:
                brace_depth += 1
            elif t.type == TokenType.RBRACE:
                brace_depth -= 1
                if brace_depth <= 0:
                    break
            elif t.type == TokenType.SEMICOLON and brace_depth == 0:
                break

        raw_str = " ".join(t.value for t in raw_tokens)
        return RawCppStmt(tok.line, tok.col, self.filename, code=raw_str)
