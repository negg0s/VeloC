"""
VeloC Model Context Protocol (MCP) & JSON-RPC 2.0 Server
Enables AI assistants (Claude, Antigravity, Cursor) to directly invoke compiler tools:
check, compile, run, test, format, explain, search-docs, get-diagnostics-json, and ir.
"""

import sys
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional


class VeloCMcpServer:
    """Stdio-based JSON-RPC 2.0 server implementing Model Context Protocol tools."""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.veloc_py = self.root_dir / "veloc.py"

    def handle_request(self, req: Dict[str, Any]) -> Dict[str, Any]:
        msg_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "veloc-mcp-server", "version": "12.0.0"},
                    "capabilities": {"tools": {}}
                }
            }
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": [
                        {
                            "name": "veloc_check",
                            "description": "Run static type and safety checking on VeloC source code",
                            "inputSchema": {
                                "type": "object",
                                "properties": {"code": {"type": "string"}, "file_path": {"type": "string"}},
                                "required": ["code"]
                            }
                        },
                        {
                            "name": "veloc_compile",
                            "description": "Compile VeloC code to a native executable",
                            "inputSchema": {
                                "type": "object",
                                "properties": {"code": {"type": "string"}, "opt_level": {"type": "string", "default": "-O3"}},
                                "required": ["code"]
                            }
                        },
                        {
                            "name": "veloc_run",
                            "description": "Compile and run VeloC code and return stdout/stderr",
                            "inputSchema": {
                                "type": "object",
                                "properties": {"code": {"type": "string"}, "timeout_sec": {"type": "number", "default": 5.0}},
                                "required": ["code"]
                            }
                        },
                        {
                            "name": "veloc_explain",
                            "description": "Explain a VeloC compiler error code with repair suggestions",
                            "inputSchema": {
                                "type": "object",
                                "properties": {"error_code": {"type": "string"}},
                                "required": ["error_code"]
                            }
                        },
                        {
                            "name": "veloc_search_docs",
                            "description": "Search VeloC standard library and syntax documentation",
                            "inputSchema": {
                                "type": "object",
                                "properties": {"query": {"type": "string"}},
                                "required": ["query"]
                            }
                        }
                    ]
                }
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            result = self.call_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }

    def call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name == "veloc_explain":
            code = args.get("error_code", "")
            return self._explain_error(code)
        elif name == "veloc_search_docs":
            q = args.get("query", "").lower()
            return self._search_docs(q)
        elif name in ("veloc_check", "veloc_compile", "veloc_run"):
            code = args.get("code", "")
            with tempfile.TemporaryDirectory() as td:
                src_file = Path(td) / "temp.vc"
                src_file.write_text(code, encoding="utf-8")
                exe_file = Path(td) / "temp.exe"

                if name == "veloc_check":
                    from src.analyzer import StaticAnalyzer
                    from src.parser import Parser
                    from src.lexer import Lexer
                    try:
                        tokens = Lexer(code, str(src_file)).tokenize()
                        program = Parser(tokens, code, str(src_file)).parse_program()
                        analyzer = StaticAnalyzer(code, str(src_file))
                        diags = analyzer.analyze(program)
                        return {"success": True, "diagnostics": [str(d) for d in diags]}
                    except Exception as err:
                        return {"success": False, "error": str(err)}

                # Compile
                cmd = [sys.executable, str(self.veloc_py), "build", str(src_file), "-o", str(exe_file)]
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode != 0:
                    return {"success": False, "stage": "compilation", "error": res.stderr}

                if name == "veloc_compile":
                    return {"success": True, "binary_size_bytes": exe_file.stat().st_size}

                # Run
                t_limit = args.get("timeout_sec", 5.0)
                try:
                    run_res = subprocess.run([str(exe_file)], capture_output=True, text=True, timeout=t_limit)
                    return {
                        "success": True,
                        "exit_code": run_res.returncode,
                        "stdout": run_res.stdout,
                        "stderr": run_res.stderr
                    }
                except subprocess.TimeoutExpired:
                    return {"success": False, "stage": "execution", "error": f"Execution timed out after {t_limit}s"}

        return {"error": f"Unknown tool: {name}"}

    def _explain_error(self, code: str) -> Dict[str, Any]:
        explanations = {
            "E0001": {
                "title": "Type Mismatch",
                "explanation": "An expression evaluates to a type different from what is expected by the variable or function argument.",
                "fix": "Use explicit type casting: `val as TargetType` or adjust function parameter types."
            },
            "E0801": {
                "title": "Capability Violation",
                "explanation": "The module attempted an operation requiring a security capability not granted in veloc.toml.",
                "fix": "Add the required capability to `[capabilities] allow = [...]` in veloc.toml if authorized."
            },
            "SEC-001": {
                "title": "Side-Channel Timing Leak",
                "explanation": "A conditional jump (if/while) depends directly on a Secret<T> value, enabling timing attacks.",
                "fix": "Use constant_time_eq() or ct_select() to keep execution cycles independent of secret data."
            }
        }
        return explanations.get(code.upper(), {
            "title": f"Code {code}",
            "explanation": "Consult VeloC Documentation in docs/spec/ or run 'veloc check'.",
            "fix": "Verify types, syntax, and capabilities."
        })

    def _search_docs(self, query: str) -> List[Dict[str, str]]:
        docs = [
            {"symbol": "Slice<T>", "doc": "Non-owning contiguous memory view with bounds checking."},
            {"symbol": "Secret<T>", "doc": "Secure memory wrapper that zeroes data on destruction and enforces constant-time ops."},
            {"symbol": "AeadCipher", "doc": "Authenticated encryption with automatic monotonic nonce tracking."},
            {"symbol": "gemm_microkernel_6x16_f32", "doc": "AVX2+FMA 6x16 matrix multiplication microkernel keeping 12 YMM accumulators."},
            {"symbol": "ThreadCachingAllocator", "doc": "Lock-free thread-local allocator with size classes and heap profiling."},
            {"symbol": "MmapFile", "doc": "Zero-copy memory mapped file reader for Windows NT and POSIX."}
        ]
        return [d for d in docs if query in d["symbol"].lower() or query in d["doc"].lower()]

    def run_stdio_loop(self):
        """Standard MCP loop listening on stdin, responding on stdout."""
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                resp = self.handle_request(req)
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
            except Exception as e:
                err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()
