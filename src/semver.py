# VeloC Semantic Versioning & Public ABI Verifier
# Automatically audits API surfaces to detect breaking changes (Major/Minor/Patch).

import sys
from typing import Dict, List, Tuple
from pathlib import Path
from lexer import Lexer
from parser import Parser
from ast_nodes import FnDecl, SoAStructDecl, Program

class ApiSignature:
    def __init__(self, kind: str, name: str, signature: str):
        self.kind = kind
        self.name = name
        self.signature = signature

    def __repr__(self):
        return f"{self.kind} {self.name}: {self.signature}"

class SemverChecker:
    @staticmethod
    def extract_api(source_code: str, filename: str = "<source>") -> Dict[str, ApiSignature]:
        tokens = Lexer(source_code, filename).tokenize()
        program = Parser(tokens, source_code, filename).parse_program()
        api: Dict[str, ApiSignature] = {}

        for decl in program.declarations:
            if isinstance(decl, FnDecl) and decl.is_pub:
                param_types = [f"{p.name}: {p.type_name}" for p in decl.params]
                sig = f"fn({', '.join(param_types)}) -> {decl.return_type}"
                api[decl.name] = ApiSignature("fn", decl.name, sig)
            elif isinstance(decl, SoAStructDecl):
                field_sigs = [f"{f.name}: {f.type_name}" for f in decl.fields]
                sig = f"soa struct {{{', '.join(field_sigs)}}}"
                api[decl.name] = ApiSignature("soa", decl.name, sig)
        return api

    @staticmethod
    def compare(old_api: Dict[str, ApiSignature], new_api: Dict[str, ApiSignature]) -> Tuple[str, List[str]]:
        breaking_changes = []
        minor_additions = []

        # Check for removed or modified APIs
        for name, old_sig in old_api.items():
            if name not in new_api:
                breaking_changes.append(f"REMOVED: {old_sig.kind} '{name}' was deleted or made private")
            else:
                new_sig = new_api[name]
                if old_sig.signature != new_sig.signature:
                    breaking_changes.append(
                        f"CHANGED: {name} signature modified:\n"
                        f"         Old: {old_sig.signature}\n"
                        f"         New: {new_sig.signature}"
                    )

        # Check for newly added APIs
        for name, new_sig in new_api.items():
            if name not in old_api:
                minor_additions.append(f"ADDED: {new_sig.kind} '{name}': {new_sig.signature}")

        if breaking_changes:
            return "MAJOR", breaking_changes + minor_additions
        elif minor_additions:
            return "MINOR", minor_additions
        else:
            return "PATCH", ["No public API changes detected (Internal patch only)"]
