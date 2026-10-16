# VeloC Hygienic Declarative Macro Expander
# Supports pattern-based macro_rules! definition and hygienic expansion.

import re
from typing import Dict, List, Tuple

class MacroRule:
    def __init__(self, pattern_vars: List[str], template: str):
        self.pattern_vars = pattern_vars
        self.template = template

class MacroDefinition:
    def __init__(self, name: str):
        self.name = name
        self.rules: List[MacroRule] = []

    def add_rule(self, pattern_vars: List[str], template: str):
        self.rules.append(MacroRule(pattern_vars, template))

    def expand(self, args: List[str], hygiene_id: int) -> str:
        # Match rule by argument count
        for rule in self.rules:
            if len(rule.pattern_vars) == len(args):
                expanded = rule.template
                for var, arg in zip(rule.pattern_vars, args):
                    # Replace $var with arg
                    expanded = re.sub(r'\$' + re.escape(var) + r'\b', arg.strip(), expanded)
                # Hygienic renaming of local variables prefixed with _tmp
                expanded = re.sub(r'\b_tmp_([a-zA-Z0-9_]+)\b', rf'_h{hygiene_id}_\1', expanded)
                return expanded
        raise ValueError(f"No matching macro rule for '{self.name}!' with {len(args)} arguments")

class MacroExpander:
    def __init__(self):
        self.macros: Dict[str, MacroDefinition] = {}
        self.hygiene_counter = 0

    def parse_and_strip_macros(self, code: str) -> str:
        idx = 0
        res = []
        while idx < len(code):
            m = re.search(r'macro_rules!\s+([a-zA-Z_]\w*)\s*\{', code[idx:])
            if not m:
                res.append(code[idx:])
                break
            start = idx + m.start()
            name = m.group(1)
            brace_start = idx + m.end() - 1
            
            # Find matching closing brace
            depth = 0
            brace_end = brace_start
            while brace_end < len(code):
                if code[brace_end] == '{': depth += 1
                elif code[brace_end] == '}':
                    depth -= 1
                    if depth == 0:
                        break
                brace_end += 1
            
            body = code[brace_start+1:brace_end]
            macro_def = MacroDefinition(name)
            
            # Extract arms: ($a:expr, $b:ident) => { template };
            arm_idx = 0
            while arm_idx < len(body):
                arm_m = re.search(r'\(([^)]*)\)\s*=>\s*\{', body[arm_idx:])
                if not arm_m:
                    break
                params_raw = arm_m.group(1)
                t_start = arm_idx + arm_m.end() - 1
                t_depth = 0
                t_end = t_start
                while t_end < len(body):
                    if body[t_end] == '{': t_depth += 1
                    elif body[t_end] == '}':
                        t_depth -= 1
                        if t_depth == 0:
                            break
                    t_end += 1
                template = body[t_start+1:t_end].strip()
                
                params = []
                if params_raw.strip():
                    for p in params_raw.split(','):
                        clean_p = p.strip()
                        if clean_p.startswith('$'):
                            var_name = clean_p[1:].split(':')[0].strip()
                            params.append(var_name)
                macro_def.add_rule(params, template)
                arm_idx = t_end + 1
            
            self.macros[name] = macro_def
            res.append(code[idx:start])
            res.append(f"// [macro_rules! {name} defined]")
            
            after_brace = brace_end + 1
            while after_brace < len(code) and code[after_brace] in (' ', '\t', '\r', '\n'):
                after_brace += 1
            if after_brace < len(code) and code[after_brace] == ';':
                after_brace += 1
            idx = after_brace

        return "".join(res)

    def expand_invocations(self, code: str) -> str:
        for name, macro_def in self.macros.items():
            call_pat = re.compile(rf'\b{name}!\s*\((.*?)\)', re.DOTALL)
            
            def replace_call(match):
                self.hygiene_counter += 1
                args_raw = match.group(1).strip()
                args = []
                if args_raw:
                    cur = []
                    depth = 0
                    for ch in args_raw:
                        if ch in ('(', '[', '{'): depth += 1
                        elif ch in (')', ']', '}'): depth -= 1
                        elif ch == ',' and depth == 0:
                            args.append("".join(cur).strip())
                            cur = []
                            continue
                        cur.append(ch)
                    if cur:
                        args.append("".join(cur).strip())
                try:
                    return macro_def.expand(args, self.hygiene_counter)
                except ValueError as err:
                    return f"/* Macro Expansion Error: {err} */"

            code = call_pat.sub(replace_call, code)
        return code

    def expand_source(self, code: str) -> str:
        code_without_defs = self.parse_and_strip_macros(code)
        return self.expand_invocations(code_without_defs)

def expand_file(source_path: str) -> str:
    from pathlib import Path
    content = Path(source_path).read_text(encoding="utf-8")
    expander = MacroExpander()
    return expander.expand_source(content)
