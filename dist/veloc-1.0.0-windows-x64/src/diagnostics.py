# VeloC Diagnostics and Error Reporting Engine
# Provides Rust/Elm-grade error formatting with exact source line underlining,
# suggestions (Levenshtein distance), and error codes (E0001..)
# Full Bilingual (Russian / English) localization and Beginner mode support.

import os
import enum
from typing import List, Optional

_CURRENT_LANG = os.environ.get("VELOC_LANG", "en").lower()

def set_diagnostic_lang(lang: str):
    global _CURRENT_LANG
    if lang.lower() in ("ru", "russian", "rus"):
        _CURRENT_LANG = "ru"
    else:
        _CURRENT_LANG = "en"

def get_diagnostic_lang() -> str:
    return _CURRENT_LANG

class DiagnosticCode(enum.Enum):
    E0001 = "E0001"
    E0002 = "E0002"
    E0003 = "E0003"
    E0004 = "E0004"
    E0005 = "E0005"
    E0006 = "E0006"
    E0007 = "E0007"
    E0008 = "E0008"
    E0009 = "E0009"
    E0010 = "E0010"
    E0011 = "E0011"
    E0012 = "E0012"
    E0013 = "E0013"
    E0014 = "E0014"
    E0015 = "E0015"

ERROR_CATALOG_EN = {
    "E0001": "Syntax Error: Unexpected token encountered during parsing.",
    "E0002": "Type Error: Incompatible types in assignment or expression.",
    "E0003": "Undeclared Identifier: Symbol could not be resolved in the current scope.",
    "E0004": "Unterminated String or Character Literal.",
    "E0005": "Duplicate Symbol: Identifier has already been declared in this scope.",
    "E0006": "Unwrap / Assertion Panic: Value was None or Err when unwrapped.",
    "E0007": "Invalid Cast: Types cannot be safely converted via `as`.",
    "E0008": "Invalid Module or Import Declaration.",
    "E0009": "Non-exhaustive Match: Not all cases or wildcard `_` are covered.",
    "E0010": "Missing Return: Function must return a value along all control flow paths.",
    "E0011": "Ownership / Lifetime Violation: Borrowed reference outlives its container or source.",
    "E0012": "Division by Zero: Constant divisor evaluated to zero.",
    "E0013": "Out-of-Bounds Index: Array or buffer index statically proven to exceed length.",
    "E0014": "Linear Resource Not Consumed: Linear value must be used exactly once.",
    "E0015": "Performance Cost Warning: Unintentional heap allocation or heavy copy detected in tight loop.",
}

ERROR_CATALOG_RU = {
    "E0001": "Синтаксическая ошибка: Встречен неожиданный токен во время разбора.",
    "E0002": "Ошибка типов: Несовместимые типы данных в присваивании или выражении.",
    "E0003": "Необъявленный идентификатор: Символ не найден в текущей области видимости.",
    "E0004": "Незакрытый строковый или символьный литерал.",
    "E0005": "Повторное объявление: Идентификатор уже объявлен в этой области видимости.",
    "E0006": "Паника unwrap / assert: Значение было None или Err при разворачивании.",
    "E0007": "Недопустимое приведение: Типы не могут быть безопасно преобразованы через `as`.",
    "E0008": "Некорректная декларация модуля или импорта.",
    "E0009": "Неисчерпывающее сопоставление: Не все варианты или `_` покрыты в `match`.",
    "E0010": "Отсутствует возврат: Функция обязана вернуть значение на всех путях выполнения.",
    "E0011": "Нарушение времени жизни/владения: Заимствованная ссылка живёт дольше источника.",
    "E0012": "Деление на ноль: Константный делитель равен нулю.",
    "E0013": "Выход за границы массива: Индекс статически превышает размер буфера.",
    "E0014": "Линейный ресурс не использован: Линейный тип обязан быть потреблён ровно один раз.",
    "E0015": "Предупреждение о скрытой цене: Обнаружена неявная аллокация в куче или тяжёлое копирование в цикле.",
}

BEGINNER_ADVICE_EN = {
    "E0001": "Tip for beginners: Check if you missed a closing brace '}', parenthesis ')', or semicolon ';'.",
    "E0002": "Tip for beginners: VeloC requires explicit type conversions using `as Type` (e.g., `x as f32`).",
    "E0003": "Tip for beginners: Did you spell the variable name correctly? Make sure it is declared with `let` before use.",
    "E0004": "Tip for beginners: Make sure every quote '\"' or single quote '\\'' has a matching closing quote on the same line.",
    "E0005": "Tip for beginners: Variable names cannot be declared twice in the same block. Use assignment `=` to change an existing variable.",
    "E0006": "Tip for beginners: Always handle potential errors with `match opt` or the try operator `?` instead of blindly calling `.unwrap()`.",
    "E0007": "Tip for beginners: You can only cast between scalar primitive types (e.g. i32 to f64). Structs require explicit mapping.",
    "E0008": "Tip for beginners: Ensure that the imported module file exists in your project src/ or packages/ directory.",
    "E0009": "Tip for beginners: Add a fallback arm `_ => { ... }` at the end of your match block to catch any unhandled values.",
    "E0010": "Tip for beginners: Check that every `if`/`else` branch in your function ends with a `return` statement or tail expression.",
    "E0011": "Tip for beginners: Never return a reference `&local_var` pointing to a local stack variable. Return by value or allocate in an Arena.",
    "E0012": "Tip for beginners: Always check if the divisor is non-zero before dividing: `if denom != 0 { val / denom }`.",
    "E0013": "Tip for beginners: Check array boundaries using `idx < array.len()` before accessing elements.",
    "E0014": "Tip for beginners: A linear value represents an exclusive resource (like an open file or socket) that must be explicitly closed or consumed.",
    "E0015": "Tip for beginners: Passing large structs by value causes memory copying. Consider passing by reference `&T` or using `Span<T>`.",
}

BEGINNER_ADVICE_RU = {
    "E0001": "Совет новичку: Проверьте, не забыта ли закрывающая фигурная скобка '}', круглая ')' или точка с запятой ';'.",
    "E0002": "Совет новичку: VeloC требует явного приведения типов с помощью ключевого слова `as` (например, `x as f32`).",
    "E0003": "Совет новичку: Проверьте правильность написания имени переменной. Убедитесь, что она объявлена через `let` перед использованием.",
    "E0004": "Совет новичку: Убедитесь, что у каждой кавычки '\"' или апострофа '\\'' есть закрывающая пара на той же строке.",
    "E0005": "Совет новичку: Имя переменной не может быть объявлено повторно в том же блоке. Используйте `=` для изменения значения.",
    "E0006": "Совет новичку: Всегда обрабатывайте возможные ошибки через `match opt` или оператор `?` вместо вызова `.unwrap()`.",
    "E0007": "Совет новичку: Преобразование через `as` допустимо только между скалярными примитивными типами (например, i32 в f64).",
    "E0008": "Совет новичку: Убедитесь, что импортируемый файл модуля существует в папке проекта src/ или packages/.",
    "E0009": "Совет новичку: Добавьте ветку по умолчанию `_ => { ... }` в конец блока match для обработки остальных случаев.",
    "E0010": "Совет новичку: Проверьте, чтобы каждая ветка `if`/`else` в функции заканчивалась `return` или хвостовым выражением.",
    "E0011": "Совет новичку: Никогда не возвращайте адрес локальной стековой переменной `&local_var`. Возвращайте по значению или используйте Арену.",
    "E0012": "Совет новичку: Всегда проверяйте делитель перед делением: `if denom != 0 { val / denom }`.",
    "E0013": "Совет новичку: Проверяйте границы массива `idx < array.len()` перед доступом по индексу.",
    "E0014": "Совет новичку: Линейный тип представляет эксклюзивный ресурс (файл, сокет), который обязан быть явно закрыт или потреблён.",
    "E0015": "Совет новичку: Передача больших структур по значению приводит к копированию памяти. Передавайте по константной ссылке `&T` или используйте `Span<T>`.",
}

ERROR_CATALOG = ERROR_CATALOG_EN

def levenshtein_distance(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev[j + 1] + 1
            deletions = curr[j] + 1
            substitutions = prev[j] + (c1 != c2)
            curr.append(min(insertions, deletions, substitutions))
        prev = curr
    return prev[-1]

def find_closest_match(name: str, candidates: List[str], max_dist: int = 3) -> Optional[str]:
    best_candidate = None
    best_dist = max_dist + 1
    for c in candidates:
        d = levenshtein_distance(name, c)
        if d < best_dist:
            best_dist = d
            best_candidate = c
    return best_candidate

class Diagnostic:
    def __init__(self, code: str, message: str, file: str, line: int, col: int, 
                 span_len: int = 1, suggestion: Optional[str] = None,
                 beginner_mode: bool = False, lang: Optional[str] = None):
        self.code = code
        self.message = message
        self.file = file
        self.line = line
        self.col = col
        self.span_len = max(1, span_len)
        self.suggestion = suggestion
        self.beginner_mode = beginner_mode
        self.lang = lang or _CURRENT_LANG

    def format_with_source(self, source_code: str) -> str:
        lines = source_code.splitlines()
        source_line = ""
        if 1 <= self.line <= len(lines):
            source_line = lines[self.line - 1]

        gutter = f" {self.line} | "
        indent = " " * len(gutter)
        col_offset = " " * (self.col - 1)
        underline = "^" * self.span_len

        err_label = "ошибка" if self.lang == "ru" else "error"
        help_label = "подсказка" if self.lang == "ru" else "help"
        beginner_label = "совет новичку" if self.lang == "ru" else "beginner tip"

        header = f"\033[1;31m{err_label}[{self.code}]\033[0m\033[1m: {self.message}\033[0m"
        loc = f"  --> {self.file}:{self.line}:{self.col}"
        
        result = [
            header,
            loc,
            f"{indent}|",
            f"{gutter}{source_line}",
            f"{indent}|{col_offset}\033[1;31m{underline}\033[0m",
        ]
        if self.suggestion:
            result.append(f"{indent}\033[1;36m= {help_label}: {self.suggestion}\033[0m")
        
        if self.beginner_mode:
            advice_dict = BEGINNER_ADVICE_RU if self.lang == "ru" else BEGINNER_ADVICE_EN
            advice = advice_dict.get(self.code)
            if advice:
                result.append(f"{indent}\033[1;33m= {beginner_label}: {advice}\033[0m")

        result.append(f"{indent}|")
        return "\n".join(result)

def explain_error_code(code: str, lang: Optional[str] = None) -> str:
    active_lang = lang or _CURRENT_LANG
    catalog = ERROR_CATALOG_RU if active_lang == "ru" else ERROR_CATALOG_EN
    advice_dict = BEGINNER_ADVICE_RU if active_lang == "ru" else BEGINNER_ADVICE_EN
    
    code_up = code.upper()
    explanation = catalog.get(code_up)
    if explanation:
        advice = advice_dict.get(code_up, "")
        res = f"\033[1;33m[{code_up}]\033[0m: {explanation}"
        if advice:
            res += f"\n  \033[1;36m{advice}\033[0m"
        return res
    return f"Unknown error code / Неизвестный код ошибки: {code}"

class DiagnosticReporter:
    def __init__(self, source_code: str = "", filename: str = "<stdin>", beginner_mode: bool = False, lang: Optional[str] = None):
        self.source_code = source_code
        self.filename = filename
        self.beginner_mode = beginner_mode
        self.lang = lang or _CURRENT_LANG
        self.diagnostics: List[Diagnostic] = []

    def error(self, code: DiagnosticCode, message: str, line: int, col: int, span_len: int = 1, suggestion: Optional[str] = None):
        # Localize default message if appropriate
        if self.lang == "ru":
            ru_catalog = ERROR_CATALOG_RU
            code_str = code.value if isinstance(code, DiagnosticCode) else str(code)
            # If default English message, replace with Russian description if available
            en_desc = ERROR_CATALOG_EN.get(code_str)
            if en_desc and en_desc.lower() in message.lower():
                message = ru_catalog.get(code_str, message)
        
        code_val = code.value if isinstance(code, DiagnosticCode) else str(code)
        diag = Diagnostic(code_val, message, self.filename, line, col, span_len, suggestion, 
                          beginner_mode=self.beginner_mode, lang=self.lang)
        self.diagnostics.append(diag)
        return diag

    def render(self) -> str:
        return "\n\n".join(d.format_with_source(self.source_code) for d in self.diagnostics)

    def print_all(self):
        if self.diagnostics:
            print(self.render())
