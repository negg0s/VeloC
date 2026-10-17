# VeloC Lexer / Tokenizer
# Tracks exact line, column, and span for high-precision Rust-style diagnostics

import enum
from typing import List, Optional, NamedTuple

class TokenType(enum.Enum):
    # End of file / newline
    EOF = "EOF"
    
    # Identifiers & Literals
    IDENT = "IDENT"
    INT_LIT = "INT_LIT"
    FLOAT_LIT = "FLOAT_LIT"
    STRING_LIT = "STRING_LIT"
    FSTRING_LIT = "FSTRING_LIT"
    CHAR_LIT = "CHAR_LIT"
    
    # Keywords
    LET = "let"
    MUT = "mut"
    FN = "fn"
    RETURN = "return"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    FOR = "for"
    IN = "in"
    MATCH = "match"
    STRUCT = "struct"
    SOA = "soa"
    ENUM = "enum"
    MODULE = "module"
    IMPORT = "import"
    PUB = "pub"
    DEFER = "defer"
    BENCH = "bench"
    TEST = "test"
    AS = "as"
    CONST = "const"
    STATIC = "static"
    AUTO = "auto"
    BREAK = "break"
    CONTINUE = "continue"
    TRUE = "true"
    FALSE = "false"
    NULL = "NULL"
    SOME = "Some"
    OK = "Ok"
    ERR = "Err"
    NONE = "None"
    
    # Operators & Delimiters
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    PERCENT = "%"
    EQ = "="
    EQEQ = "=="
    NEQ = "!="
    LT = "<"
    LTE = "<="
    GT = ">"
    GTE = ">="
    NOT = "!"
    AND = "&&"
    OR = "||"
    BIT_AND = "&"
    BIT_OR = "|"
    BIT_XOR = "^"
    BIT_NOT = "~"
    SHL = "<<"
    SHR = ">>"
    
    # Advanced Operators
    PIPE = "|>"
    COALESCE = "??"
    ARROW = "=>"
    THIN_ARROW = "->"
    COLON_COLON = "::"
    
    # Punctuation
    COLON = ":"
    SEMICOLON = ";"
    COMMA = ","
    DOT = "."
    DOT_DOT = ".."
    QUESTION = "?"
    AT = "@"
    HASH = "#"
    
    # Brackets
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"

KEYWORDS = {
    "let": TokenType.LET,
    "mut": TokenType.MUT,
    "fn": TokenType.FN,
    "return": TokenType.RETURN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "match": TokenType.MATCH,
    "struct": TokenType.STRUCT,
    "soa": TokenType.SOA,
    "enum": TokenType.ENUM,
    "module": TokenType.MODULE,
    "import": TokenType.IMPORT,
    "pub": TokenType.PUB,
    "defer": TokenType.DEFER,
    "bench": TokenType.BENCH,
    "test": TokenType.TEST,
    "as": TokenType.AS,
    "const": TokenType.CONST,
    "static": TokenType.STATIC,
    "auto": TokenType.AUTO,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "NULL": TokenType.NULL,
    "Some": TokenType.SOME,
    "Ok": TokenType.OK,
    "Err": TokenType.ERR,
    "None": TokenType.NONE,
}

class Token(NamedTuple):
    type: TokenType
    value: str
    line: int
    col: int
    span_len: int
    file: str

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, line={self.line}, col={self.col})"

class LexerError(Exception):
    def __init__(self, message: str, line: int, col: int, file: str):
        super().__init__(f"{file}:{line}:{col}: error: {message}")
        self.message = message
        self.line = line
        self.col = col
        self.file = file

class Lexer:
    def __init__(self, source: str, filename: str = "<stdin>"):
        self.source = source
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.col = 1
        self.length = len(source)

    def peek(self, offset: int = 0) -> str:
        idx = self.pos + offset
        if idx < self.length:
            return self.source[idx]
        return ""

    def advance(self) -> str:
        if self.pos < self.length:
            ch = self.source[self.pos]
            self.pos += 1
            if ch == "\n":
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            return ch
        return ""

    def match(self, expected: str) -> bool:
        if self.peek() == expected:
            self.advance()
            return True
        return False

    def skip_whitespace_and_comments(self):
        while self.pos < self.length:
            ch = self.peek()
            if ch in (" ", "\t", "\r", "\n"):
                self.advance()
            elif ch == "/" and self.peek(1) == "/":
                # Line comment
                while self.pos < self.length and self.peek() != "\n":
                    self.advance()
            elif ch == "/" and self.peek(1) == "*":
                # Block comment
                self.advance()
                self.advance()
                while self.pos < self.length and not (self.peek() == "*" and self.peek(1) == "/"):
                    self.advance()
                if self.pos < self.length:
                    self.advance() # *
                    self.advance() # /
            else:
                break

    def read_string(self, is_fstring: bool = False) -> Token:
        start_line = self.line
        start_col = self.col - (2 if is_fstring else 1)
        start_pos = self.pos
        val = []
        while self.pos < self.length:
            ch = self.peek()
            if ch == '"':
                self.advance()
                span_len = self.pos - start_pos + (2 if is_fstring else 1)
                token_type = TokenType.FSTRING_LIT if is_fstring else TokenType.STRING_LIT
                return Token(token_type, "".join(val), start_line, start_col, span_len, self.filename)
            elif ch == "\\":
                self.advance()
                escaped = self.advance()
                if escaped == "n": val.append("\n")
                elif escaped == "t": val.append("\t")
                elif escaped == "r": val.append("\r")
                elif escaped == '"': val.append('"')
                elif escaped == "\\": val.append("\\")
                else: val.append("\\" + escaped)
            else:
                val.append(self.advance())
        raise LexerError("Unterminated string literal", start_line, start_col, self.filename)

    def read_char(self) -> Token:
        start_line = self.line
        start_col = self.col
        self.advance() # '
        ch = self.advance()
        if ch == "\\":
            esc = self.advance()
            ch = "\\" + esc
        if self.advance() != "'":
            raise LexerError("Unterminated character literal", start_line, start_col, self.filename)
        return Token(TokenType.CHAR_LIT, ch, start_line, start_col, len(ch) + 2, self.filename)

    def read_number(self) -> Token:
        start_line = self.line
        start_col = self.col
        start_pos = self.pos
        is_float = False

        if self.peek() == "0" and self.peek(1) in ("x", "X"):
            self.advance()
            self.advance()
            while self.peek().lower() in "0123456789abcdef":
                self.advance()
        else:
            while self.peek().isdigit():
                self.advance()
            if self.peek() == "." and self.peek(1).isdigit():
                is_float = True
                self.advance() # .
                while self.peek().isdigit():
                    self.advance()
            if self.peek().lower() == "e":
                is_float = True
                self.advance()
                if self.peek() in ("+", "-"):
                    self.advance()
                while self.peek().isdigit():
                    self.advance()

        # Check suffixes: f, f32, u, u32, ull, i64, etc.
        suffix = []
        while self.peek().isalnum() or self.peek() == "_":
            suffix.append(self.advance())
        suffix_str = "".join(suffix).lower()
        if suffix_str in ("f", "f32", "f64"):
            is_float = True

        raw_num = self.source[start_pos:self.pos]
        token_type = TokenType.FLOAT_LIT if is_float else TokenType.INT_LIT
        return Token(token_type, raw_num, start_line, start_col, len(raw_num), self.filename)

    def read_ident(self) -> Token:
        start_line = self.line
        start_col = self.col
        start_pos = self.pos
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()
        text = self.source[start_pos:self.pos]
        token_type = KEYWORDS.get(text, TokenType.IDENT)
        return Token(token_type, text, start_line, start_col, len(text), self.filename)

    def tokenize(self) -> List[Token]:
        tokens = []
        while self.pos < self.length:
            self.skip_whitespace_and_comments()
            if self.pos >= self.length:
                break

            start_line = self.line
            start_col = self.col
            ch = self.peek()

            # String literals & F-strings
            if ch == "f" and self.peek(1) == '"':
                self.advance() # f
                self.advance() # "
                tokens.append(self.read_string(is_fstring=True))
                continue
            elif ch == '"':
                self.advance() # "
                tokens.append(self.read_string(is_fstring=False))
                continue
            elif ch == "'":
                tokens.append(self.read_char())
                continue

            # Numbers
            if ch.isdigit():
                tokens.append(self.read_number())
                continue

            # Identifiers and keywords
            if ch.isalpha() or ch == "_":
                tokens.append(self.read_ident())
                continue

            # Multi-char operators
            self.advance()
            if ch == "|" and self.match(">"):
                tokens.append(Token(TokenType.PIPE, "|>", start_line, start_col, 2, self.filename))
            elif ch == "?" and self.match("?"):
                tokens.append(Token(TokenType.COALESCE, "??", start_line, start_col, 2, self.filename))
            elif ch == "=" and self.match(">"):
                tokens.append(Token(TokenType.ARROW, "=>", start_line, start_col, 2, self.filename))
            elif ch == "-" and self.match(">"):
                tokens.append(Token(TokenType.THIN_ARROW, "->", start_line, start_col, 2, self.filename))
            elif ch == ":" and self.match(":"):
                tokens.append(Token(TokenType.COLON_COLON, "::", start_line, start_col, 2, self.filename))
            elif ch == "=" and self.match("="):
                tokens.append(Token(TokenType.EQEQ, "==", start_line, start_col, 2, self.filename))
            elif ch == "!" and self.match("="):
                tokens.append(Token(TokenType.NEQ, "!=", start_line, start_col, 2, self.filename))
            elif ch == "<" and self.match("="):
                tokens.append(Token(TokenType.LTE, "<=", start_line, start_col, 2, self.filename))
            elif ch == ">" and self.match("="):
                tokens.append(Token(TokenType.GTE, ">=", start_line, start_col, 2, self.filename))
            elif ch == "<" and self.match("<"):
                tokens.append(Token(TokenType.SHL, "<<", start_line, start_col, 2, self.filename))
            elif ch == ">" and self.match(">"):
                tokens.append(Token(TokenType.SHR, ">>", start_line, start_col, 2, self.filename))
            elif ch == "&" and self.match("&"):
                tokens.append(Token(TokenType.AND, "&&", start_line, start_col, 2, self.filename))
            elif ch == "|" and self.match("|"):
                tokens.append(Token(TokenType.OR, "||", start_line, start_col, 2, self.filename))
            elif ch == "." and self.match("."):
                tokens.append(Token(TokenType.DOT_DOT, "..", start_line, start_col, 2, self.filename))
            elif ch == "+" and self.match("="):
                tokens.append(Token(TokenType.PLUS, "+=", start_line, start_col, 2, self.filename))
            elif ch == "-" and self.match("="):
                tokens.append(Token(TokenType.MINUS, "-=", start_line, start_col, 2, self.filename))
            elif ch == "*" and self.match("="):
                tokens.append(Token(TokenType.STAR, "*=", start_line, start_col, 2, self.filename))
            elif ch == "/" and self.match("="):
                tokens.append(Token(TokenType.SLASH, "/=", start_line, start_col, 2, self.filename))
            elif ch == "%" and self.match("="):
                tokens.append(Token(TokenType.PERCENT, "%=", start_line, start_col, 2, self.filename))
            elif ch == "+" and self.match("+"):
                tokens.append(Token(TokenType.PLUS, "++", start_line, start_col, 2, self.filename))
            elif ch == "-" and self.match("-"):
                tokens.append(Token(TokenType.MINUS, "--", start_line, start_col, 2, self.filename))
            # Single-char punctuation & operators
            elif ch == "+": tokens.append(Token(TokenType.PLUS, "+", start_line, start_col, 1, self.filename))
            elif ch == "-": tokens.append(Token(TokenType.MINUS, "-", start_line, start_col, 1, self.filename))
            elif ch == "*": tokens.append(Token(TokenType.STAR, "*", start_line, start_col, 1, self.filename))
            elif ch == "/": tokens.append(Token(TokenType.SLASH, "/", start_line, start_col, 1, self.filename))
            elif ch == "%": tokens.append(Token(TokenType.PERCENT, "%", start_line, start_col, 1, self.filename))
            elif ch == "=": tokens.append(Token(TokenType.EQ, "=", start_line, start_col, 1, self.filename))
            elif ch == "!": tokens.append(Token(TokenType.NOT, "!", start_line, start_col, 1, self.filename))
            elif ch == "<": tokens.append(Token(TokenType.LT, "<", start_line, start_col, 1, self.filename))
            elif ch == ">": tokens.append(Token(TokenType.GT, ">", start_line, start_col, 1, self.filename))
            elif ch == "&": tokens.append(Token(TokenType.BIT_AND, "&", start_line, start_col, 1, self.filename))
            elif ch == "|": tokens.append(Token(TokenType.BIT_OR, "|", start_line, start_col, 1, self.filename))
            elif ch == "^": tokens.append(Token(TokenType.BIT_XOR, "^", start_line, start_col, 1, self.filename))
            elif ch == "~": tokens.append(Token(TokenType.BIT_NOT, "~", start_line, start_col, 1, self.filename))
            elif ch == ":": tokens.append(Token(TokenType.COLON, ":", start_line, start_col, 1, self.filename))
            elif ch == ";": tokens.append(Token(TokenType.SEMICOLON, ";", start_line, start_col, 1, self.filename))
            elif ch == ",": tokens.append(Token(TokenType.COMMA, ",", start_line, start_col, 1, self.filename))
            elif ch == ".": tokens.append(Token(TokenType.DOT, ".", start_line, start_col, 1, self.filename))
            elif ch == "?": tokens.append(Token(TokenType.QUESTION, "?", start_line, start_col, 1, self.filename))
            elif ch == "@": tokens.append(Token(TokenType.AT, "@", start_line, start_col, 1, self.filename))
            elif ch == "#": tokens.append(Token(TokenType.HASH, "#", start_line, start_col, 1, self.filename))
            elif ch == "(": tokens.append(Token(TokenType.LPAREN, "(", start_line, start_col, 1, self.filename))
            elif ch == ")": tokens.append(Token(TokenType.RPAREN, ")", start_line, start_col, 1, self.filename))
            elif ch == "{": tokens.append(Token(TokenType.LBRACE, "{", start_line, start_col, 1, self.filename))
            elif ch == "}": tokens.append(Token(TokenType.RBRACE, "}", start_line, start_col, 1, self.filename))
            elif ch == "[": tokens.append(Token(TokenType.LBRACKET, "[", start_line, start_col, 1, self.filename))
            elif ch == "]": tokens.append(Token(TokenType.RBRACKET, "]", start_line, start_col, 1, self.filename))
            else:
                raise LexerError(f"Unexpected character: {ch!r}", start_line, start_col, self.filename)

        tokens.append(Token(TokenType.EOF, "", self.line, self.col, 0, self.filename))
        return tokens
