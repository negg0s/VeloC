# VeloC Recursive Descent + Pratt Parser
# Supports pure VeloC declarations and statements as well as embedded C++ blocks.

from typing import List, Optional, Tuple, Dict, Any
from lexer import Token, TokenType, Lexer, LexerError
from ast_nodes import *
from diagnostics import DiagnosticReporter, Diagnostic, DiagnosticCode
from codegen import CppCodegen

def format_raw_tokens(tokens: List[Token]) -> str:
    parts = []
    for t in tokens:
        if t.type == TokenType.STRING_LIT:
            esc = t.value.replace("\r", "\\r").replace("\n", "\\n").replace('"', '\\"')
            parts.append(f'"{esc}"')
        elif t.type == TokenType.CHAR_LIT:
            parts.append(f"'{t.value}'")
        else:
            parts.append(t.value)
    return " ".join(parts)

def is_ident_token(t: Token) -> bool:
    v = t.value
    return bool(v) and (v[0].isalpha() or v[0] == '_') and all(c.isalnum() or c == '_' for c in v)

def format_type_tokens(tokens: List[Token]) -> str:
    res = []
    for i, t in enumerate(tokens):
        if i > 0:
            prev = tokens[i-1]
            if is_ident_token(prev) and is_ident_token(t):
                res.append(" ")
            elif prev.value in ("*", "&") and is_ident_token(t):
                res.append(" ")
        res.append(t.value)
    return "".join(res)

# Operator Precedence for Pratt Parser
PRECEDENCE: Dict[TokenType, int] = {
    TokenType.EQ: 5,           # =
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

class MultiParseError(Exception):
    def __init__(self, errors: List[ParseError]):
        super().__init__(f"Encountered {len(errors)} parse error(s)")
        self.errors = errors

class Parser:
    def __init__(self, tokens: List[Token], source_code: str = "", filename: str = "<stdin>"):
        self.tokens = tokens
        self.source_code = source_code
        self.filename = filename
        self.pos = 0
        self.diagnostics = DiagnosticReporter(source_code, filename)
        self.errors: List[ParseError] = []
        self.max_errors: int = 10

    def record_error(self, err: ParseError):
        self.errors.append(err)
        if len(self.errors) >= self.max_errors:
            raise MultiParseError(self.errors)

    def synchronize_stmt(self):
        while not self.check(TokenType.EOF):
            tok = self.current()
            if tok.type in (TokenType.SEMICOLON, TokenType.RBRACE):
                self.advance()
                return
            if tok.type in (TokenType.LET, TokenType.IF, TokenType.WHILE, TokenType.FOR,
                            TokenType.RETURN, TokenType.MATCH, TokenType.DEFER, TokenType.BENCH):
                return
            self.advance()

    def synchronize_decl(self):
        while not self.check(TokenType.EOF):
            tok = self.current()
            if tok.type in (TokenType.FN, TokenType.SOA, TokenType.STRUCT,
                            TokenType.MODULE, TokenType.IMPORT, TokenType.TEST, TokenType.PUB):
                return
            self.advance()

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

            # Postfix error propagation: expr?
            if self.check(TokenType.QUESTION):
                op_tok = self.advance()
                left = TryExpr(op_tok.line, op_tok.col, self.filename, expr=left)
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
                member_name = member_tok.value
                # Check for template arguments: member<T, ...>
                if self.check(TokenType.LT):
                    save_lt = self.pos
                    self.advance() # <
                    tmpl_parts = []
                    depth = 1
                    while not self.check(TokenType.EOF) and depth > 0:
                        t = self.advance()
                        if t.type == TokenType.LT: depth += 1
                        elif t.type == TokenType.GT: depth -= 1
                        elif t.type in (TokenType.SEMICOLON, TokenType.LBRACE): break
                        if depth > 0:
                            tmpl_parts.append(t)
                    if depth == 0 and (self.check(TokenType.LPAREN) or self.check(TokenType.DOT)):
                        tmpl_str = format_type_tokens(tmpl_parts)
                        member_name += f"<{tmpl_str}>"
                    else:
                        self.pos = save_lt
                left = MemberAccessExpr(op_tok.line, op_tok.col, self.filename, object=left, member=member_name)
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

            # Assignment operators: left = right (Right-associative)
            if op_tok.type == TokenType.EQ:
                right = self.parse_expr(prec - 1)
                left = BinaryExpr(op_tok.line, op_tok.col, self.filename, left=left, op=op_tok.value, right=right)
                continue

            # Standard binary expression
            right = self.parse_expr(prec)
            left = BinaryExpr(op_tok.line, op_tok.col, self.filename, left=left, op=op_tok.value, right=right)

        return left

    def parse_prefix(self) -> Expr:
        tok = self.current()

        # Unary operators: +, -, !, ~, *, &
        if tok.type in (TokenType.PLUS, TokenType.MINUS, TokenType.NOT, TokenType.BIT_NOT, TokenType.STAR, TokenType.BIT_AND):
            self.advance()
            operand = self.parse_expr(140)
            return UnaryExpr(tok.line, tok.col, self.filename, op=tok.value, operand=operand)

        # Parenthesized expression, C-style cast: (f32*)expr, or Tuple: (a, b)
        if tok.type == TokenType.LPAREN:
            # Check if this is a C-style cast like (f32*), (i32), (const char*)
            save_pos = self.pos
            self.advance() # (
            type_tokens = []
            while self.current().type in (TokenType.IDENT, TokenType.STAR, TokenType.BIT_AND, TokenType.CONST, TokenType.COLON_COLON) and len(type_tokens) < 5:
                t = self.advance()
                type_tokens.append(t)
            if len(type_tokens) > 0 and self.check(TokenType.RPAREN):
                self.advance() # )
                # If next token can begin an expression or unary operator
                if self.check(TokenType.IDENT) or self.check(TokenType.LPAREN) or self.check(TokenType.INT_LIT) or self.check(TokenType.FLOAT_LIT) or self.check(TokenType.STAR) or self.check(TokenType.PLUS) or self.check(TokenType.MINUS):
                    type_str = format_type_tokens(type_tokens)
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
                        lambda_toks.append(self.advance()) # (
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

        if tok.type == TokenType.LBRACE:
            start_tok = self.advance() # {
            items = []
            if not self.check(TokenType.RBRACE):
                while True:
                    items.append(self.parse_expr(0))
                    if not self.match(TokenType.COMMA):
                        break
            self.expect(TokenType.RBRACE, "Expected '}' closing initializer list")
            item_strs = [CppCodegen("<include>").emit_expr(it) for it in items]
            return Identifier(start_tok.line, start_tok.col, self.filename, name=f"{{{', '.join(item_strs)}}}")

        if tok.type == TokenType.MATCH:
            start_tok = self.advance()
            has_paren = self.match(TokenType.LPAREN)
            cond_expr = self.parse_expr(0)
            if has_paren:
                self.expect(TokenType.RPAREN, "Expected ')' after match expression")
            self.expect(TokenType.LBRACE, "Expected '{' to start match body")
            arms = []
            while not self.check(TokenType.RBRACE) and not self.check(TokenType.EOF):
                arm_tok = self.advance()
                if arm_tok.value == "_":
                    pat_val = "_"
                elif arm_tok.type in (TokenType.STRING_LIT, TokenType.INT_LIT, TokenType.FLOAT_LIT, TokenType.IDENT):
                    pat_val = f'"{arm_tok.value}"' if arm_tok.type == TokenType.STRING_LIT else arm_tok.value
                else:
                    raise ParseError(f"Expected match pattern (string, integer or '_'), got '{arm_tok.value}'", arm_tok, DiagnosticCode.E0001)
                self.expect(TokenType.ARROW, "Expected '=>' after match pattern")
                arm_body = self.parse_expr(0)
                arms.append(MatchArm(arm_tok.line, arm_tok.col, self.filename, pattern_val=pat_val, body=arm_body))
                self.match(TokenType.COMMA)
            self.expect(TokenType.RBRACE, "Expected '}' closing match body")
            return MatchExpr(start_tok.line, start_tok.col, self.filename, expr=cond_expr, arms=arms)

        raise ParseError(f"Unexpected token in expression: '{tok.value}'", tok, DiagnosticCode.E0001)

    # ==========================================
    # Statement Parsing
    # ==========================================
    def _format_prep_directive(self, tokens: List[Token]) -> str:
        parts = []
        for i, t in enumerate(tokens):
            if t.type == TokenType.HASH:
                parts.append("#")
            elif i > 0 and (tokens[i-1].value in ("<", "#", ".") or t.value in (">", ".")):
                parts.append(t.value)
            elif t.type == TokenType.STRING_LIT:
                parts.append(f'"{t.value}"')
            else:
                if parts and parts[-1] not in ("#", "<"):
                    parts.append(" ")
                parts.append(t.value)
        return "".join(parts)

    def parse_stmt(self) -> Stmt:
        tok = self.current()

        # Preprocessor directive statement: #pragma, etc.
        if tok.type == TokenType.HASH:
            prep_tokens = []
            dir_line = tok.line
            while not self.check(TokenType.EOF) and self.current().line == dir_line:
                prep_tokens.append(self.advance())
            return RawCppStmt(tok.line, tok.col, self.filename, code=self._format_prep_directive(prep_tokens))

        # Let statement: let [mut] [(a, b) | x[: type]] [= expr];
        if tok.type == TokenType.LET:
            return self.parse_let_stmt()

        # C-style variable declaration: [const] type [*|&]* name [= init];
        # e.g.: u8* hash_buf = ...; const usize N = 100; int x = 0;
        is_const = False
        save_pos = self.pos
        if self.check(TokenType.CONST):
            is_const = True
            self.advance()
        
        if self.check(TokenType.IDENT) or self.check(TokenType.COLON_COLON):
            type_tokens = []
            while self.check(TokenType.IDENT) or self.check(TokenType.COLON_COLON):
                type_tokens.append(self.advance())
            if self.check(TokenType.LT):
                type_tokens.append(self.advance())
                depth = 1
                while self.pos < len(self.tokens) and depth > 0:
                    t = self.advance()
                    type_tokens.append(t)
                    if t.type == TokenType.LT: depth += 1
                    elif t.type == TokenType.GT: depth -= 1
                    elif t.type in (TokenType.SEMICOLON, TokenType.LBRACE): break
            while self.check(TokenType.STAR) or self.check(TokenType.BIT_AND):
                type_tokens.append(self.advance())
            if self.check(TokenType.IDENT):
                var_stmts = []
                type_str = format_type_tokens(type_tokens)
                while not self.check(TokenType.EOF):
                    if not self.check(TokenType.IDENT):
                        break
                    var_name_tok = self.advance()
                    init_expr = None
                    cargs = None
                    if self.match(TokenType.EQ):
                        init_expr = self.parse_expr(0)
                    elif self.match(TokenType.LPAREN):
                        cargs = []
                        if not self.check(TokenType.RPAREN):
                            while True:
                                cargs.append(self.parse_expr(0))
                                if not self.match(TokenType.COMMA):
                                    break
                        self.expect(TokenType.RPAREN, "Expected ')' after constructor arguments")
                    var_stmts.append(LetStmt(tok.line, tok.col, self.filename, name=var_name_tok.value,
                                             type_annotation=type_str, is_mut=not is_const, init_expr=init_expr,
                                             constructor_args=cargs))
                    if self.match(TokenType.COMMA):
                        continue
                    break
                if self.match(TokenType.SEMICOLON):
                    if len(var_stmts) == 1:
                        return var_stmts[0]
                    return SeqStmt(tok.line, tok.col, self.filename, statements=var_stmts)
        self.pos = save_pos

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
            type_tokens = []
            depth = 0
            while not self.check(TokenType.EOF) and not self.check(TokenType.SEMICOLON):
                if depth == 0 and self.check(TokenType.EQ):
                    break
                t = self.advance()
                if t.type == TokenType.LT:
                    depth += 1
                elif t.type == TokenType.GT:
                    depth -= 1
                type_tokens.append(t)
            type_annot = format_type_tokens(type_tokens)
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
            elif pat_tok.type == TokenType.IDENT:
                pat_type = "Some"
                var_tok = self.advance()
            else:
                pat_type = "Some"
                var_tok = self.expect(TokenType.IDENT, "Expected variable name in pattern")
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
            elif pat_tok.type == TokenType.IDENT:
                pat_type = "Some"
                var_tok = self.advance()
            else:
                pat_type = "Some"
                var_tok = self.expect(TokenType.IDENT, "Expected variable name in pattern")
            self.expect(TokenType.EQ, "Expected '=' in while let statement")
            expr = self.parse_expr(0)
            body = self.parse_block()
            return WhileLetStmt(start_tok.line, start_tok.col, self.filename, pattern_type=pat_type,
                                var_name=var_tok.value, expr=expr, body=body)

        has_paren = self.match(TokenType.LPAREN)
        cond = self.parse_expr(0)
        if has_paren:
            self.expect(TokenType.RPAREN, "Expected ')' after while condition")

        if self.check(TokenType.LBRACE):
            body = self.parse_block()
        else:
            body = BlockStmt(start_tok.line, start_tok.col, self.filename, statements=[self.parse_stmt()])
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
            raw_tokens.append(Token(TokenType.LPAREN, "(", start_tok.line, start_tok.col, 1, start_tok.file))
            paren_depth = 1
            while paren_depth > 0 and not self.check(TokenType.EOF):
                t = self.advance()
                raw_tokens.append(t)
                if t.type == TokenType.LPAREN: paren_depth += 1
                elif t.type == TokenType.RPAREN: paren_depth -= 1

        if self.check(TokenType.LBRACE):
            body = self.parse_block()
            body_cpp = CppCodegen("<include>").emit_stmt(body)
        else:
            body = self.parse_stmt()
            # Strip any line directives in single statement
            body_cpp = "{ " + CppCodegen("<include>").emit_stmt(body).strip() + " }"
            body_cpp = re.sub(r'#line\s+\d+\s+"[^"]*"\n?', '', body_cpp)
        raw_header = format_raw_tokens(raw_tokens)
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
            try:
                stmts.append(self.parse_stmt())
            except ParseError as err:
                self.record_error(err)
                self.synchronize_stmt()
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

        raw_str = format_raw_tokens(raw_tokens)
        return RawCppStmt(start_tok.line, start_tok.col, self.filename, code=raw_str)

    # ==========================================
    # Top-Level Declarations
    # ==========================================
    def parse_program(self) -> Program:
        decls = []
        while not self.check(TokenType.EOF):
            try:
                decl = self.parse_decl()
                if decl:
                    decls.append(decl)
            except ParseError as err:
                self.record_error(err)
                self.synchronize_decl()
        if self.errors:
            if len(self.errors) == 1:
                raise self.errors[0]
            raise MultiParseError(self.errors)
        return Program(1, 1, self.filename, declarations=decls)

    def _parse_fn_param(self, tokens: List[Token]) -> FnParam:
        if not tokens:
            return FnParam(0, 0, self.filename, name="arg", type_name="auto")
        colon_indices = [idx for idx, t in enumerate(tokens) if t.type == TokenType.COLON]
        if colon_indices:
            c_idx = colon_indices[0]
            name_tokens = tokens[:c_idx]
            t_tokens = tokens[c_idx + 1:]
            p_name = name_tokens[-1].value if name_tokens else "arg"
            p_type = format_type_tokens(t_tokens) if t_tokens else "auto"
            return FnParam(tokens[0].line, tokens[0].col, self.filename, name=p_name, type_name=p_type)
        elif len(tokens) == 1:
            return FnParam(tokens[0].line, tokens[0].col, self.filename, name=tokens[0].value, type_name="auto")
        else:
            name_p = tokens[-1]
            type_str = format_type_tokens(tokens[:-1])
            return FnParam(name_p.line, name_p.col, self.filename, name=name_p.value, type_name=type_str)

    def parse_decl(self) -> Optional[Decl]:
        tok = self.current()

        # Preprocessor directive: #include, #define, #pragma, etc.
        if tok.type == TokenType.HASH:
            prep_tokens = []
            dir_line = tok.line
            while not self.check(TokenType.EOF) and self.current().line == dir_line:
                prep_tokens.append(self.advance())
            return RawCppStmt(tok.line, tok.col, self.filename, code=self._format_prep_directive(prep_tokens))

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
                    type_part = []
                    while not self.check(TokenType.COMMA) and not self.check(TokenType.RPAREN) and not self.check(TokenType.EOF):
                        type_part.append(self.advance())
                    params.append(self._parse_fn_param(type_part))
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

        # C-style function: [type] name(params) [-> ret] { ... } (e.g. int main(), void test())
        if tok.type == TokenType.IDENT:
            save_pos = self.pos
            type_tokens = []
            while self.pos < len(self.tokens) and self.current().type in (TokenType.IDENT, TokenType.STAR, TokenType.BIT_AND, TokenType.CONST):
                type_tokens.append(self.advance())
            if len(type_tokens) >= 1 and self.check(TokenType.LPAREN):
                fn_name = type_tokens[-1].value
                ret_type = format_type_tokens(type_tokens[:-1]) if len(type_tokens) > 1 else "auto"
                self.advance() # consume '('
                
                params = []
                if not self.check(TokenType.RPAREN):
                    while not self.check(TokenType.EOF):
                        param_tokens = []
                        while not self.check(TokenType.COMMA) and not self.check(TokenType.RPAREN) and not self.check(TokenType.EOF):
                            param_tokens.append(self.advance())
                        params.append(self._parse_fn_param(param_tokens))
                        if not self.match(TokenType.COMMA):
                            break
                if self.check(TokenType.RPAREN):
                    self.advance() # consume ')'
                    if self.match(TokenType.THIN_ARROW):
                        ret_parts = []
                        while not self.check(TokenType.LBRACE) and not self.check(TokenType.EOF):
                            ret_parts.append(self.advance().value)
                        ret_type = " ".join(ret_parts)
                    
                    if self.check(TokenType.LBRACE):
                        body = self.parse_block()
                        return FnDecl(tok.line, tok.col, self.filename, name=fn_name,
                                      params=params, return_type=ret_type, body=body, is_pub=is_pub)
            # Not a function, backtrack
            self.pos = save_pos

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

        raw_str = format_raw_tokens(raw_tokens)
        return RawCppStmt(tok.line, tok.col, self.filename, code=raw_str)
