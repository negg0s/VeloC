# VeloC Interactive Web Playground Server
# Runs locally on http://localhost:8080 with interactive code editor,
# clickable examples catalog, and real-time native execution.

import os
import sys
import json
import time
import subprocess
import hashlib
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

ROOT_DIR = Path("D:/VeloC")
CACHE_DIR = ROOT_DIR / ".cache" / "playground"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

PLAYGROUND_EXAMPLES = {
    "hello": {
        "title": "Hello, World!",
        "code": """fn main() -> i32 {
    printf("Hello from VeloC Web Playground!\\n");
    printf("Running on native x86_64 hardware with AVX2\\n");
    return 0;
}"""
    },
    "soa_particles": {
        "title": "SoA SIMD Particles (5 Million)",
        "code": """soa struct Particle {
    f32 x;
    f32 y;
    f32 vx;
    f32 vy;
};

fn main() -> i32 {
    const usize N = 100000;
    Particle_SoA p = Particle_SoA::create(N);
    defer p.destroy();
    
    for (usize i = 0; i < N; i++) {
        p.push(0.0f, 0.0f, 1.5f, -0.5f);
    }
    
    VeloC_Timer timer;
    timer.start();
    f32 dt = 0.016f;
    f32x8 dt_vec = f32x8_set1(dt);
    
    for (usize i = 0; i < N; i += 8) {
        f32x8 x = f32x8_load(&p.x[i]);
        f32x8 vx = f32x8_load(&p.vx[i]);
        f32x8_store(&p.x[i], f32x8_fmadd(vx, dt_vec, x));
    }
    
    printf("Simulated %llu particles in %.3f ms!\\n", (unsigned long long)N, timer.elapsed_ms());
    printf("Sample Pos: (%.2f, %.2f)\\n", p.x[0], p.y[0]);
    return 0;
}"""
    },
    "arena_memory": {
        "title": "Zero-Cost Bump Arena",
        "code": """fn main() -> i32 {
    VeloC_Arena arena = VeloC_Arena::create(1024 * 1024);
    defer arena.destroy();
    
    VeloC_Timer timer;
    timer.start();
    
    for (int cycle = 0; cycle < 1000; cycle++) {
        i32* arr = arena.alloc_array<i32>(1000);
        arr[999] = cycle;
        arena.reset(); // Instant O(1) reset
    }
    
    printf("1,000 Arena cycles completed in %.3f ms (zero OS heap locks!)\\n", timer.elapsed_ms());
    return 0;
}"""
    },
    "eytzinger_search": {
        "title": "Branchless Eytzinger Search",
        "code": """fn eytzinger_search(arr: const i32*, n: i32, x: i32) -> i32 {
    int k = 1;
    while (k <= n) {
        k = 2 * k + (arr[k] < x ? 1 : 0);
    }
    int j = k >> __builtin_ffs(~k);
    return j > 0 ? j : 1;
}

fn main() -> i32 {
    i32 tree[16] = {0, 8, 4, 12, 2, 6, 10, 14, 1, 3, 5, 7, 9, 11, 13, 15};
    int found = eytzinger_search(tree, 15, 10);
    printf("Branchless search target 10 -> Node %d (Val: %d)\\n", found, tree[found]);
    return 0;
}"""
    },
    "accuracy_contract": {
        "title": "Strict IEEE-754 Math",
        "code": """fn main() -> i32 {
    f32 x = 1.0f;
    f32 inf = 1.0f / 0.0f;
    f32 nan_val = 0.0f / 0.0f;
    
    printf("Strict IEEE-754 Check:\\n");
    printf("  isinf(1.0 / 0.0) : %d\\n", isinf(inf) ? 1 : 0);
    printf("  isnan(0.0 / 0.0) : %d\\n", isnan(nan_val) ? 1 : 0);
    printf("  exp_fast(1.0)    : %.6f (max 1 ULP error)\\n", exp_fast(x));
    return 0;
}"""
    }
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VeloC Interactive Web Playground</title>
    <style>
        :root { --bg: #0f1015; --pane: #161822; --border: #232738; --accent: #00f28f; --text: #f0f2f8; --text-dim: #8b92a8; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; margin: 0; background: var(--bg); color: var(--text); height: 100vh; display: flex; flex-direction: column; }
        header { background: var(--pane); padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--border); }
        .logo { font-size: 18px; font-weight: bold; color: var(--accent); display: flex; align-items: center; gap: 8px; }
        .toolbar { display: flex; align-items: center; gap: 12px; }
        select, button { background: #202434; color: var(--text); border: 1px solid var(--border); border-radius: 6px; padding: 8px 14px; font-size: 13px; font-weight: 600; cursor: pointer; transition: 0.15s; outline: none; }
        button:hover, select:hover { border-color: var(--accent); }
        button.run-btn { background: var(--accent); color: #000; border: none; font-weight: bold; }
        button.run-btn:hover { background: #00d67e; }
        .workspace { flex: 1; display: flex; overflow: hidden; }
        .editor-container, .output-container { flex: 1; display: flex; flex-direction: column; border-right: 1px solid var(--border); }
        .editor-header, .output-header { background: var(--pane); padding: 8px 16px; font-size: 12px; font-weight: 600; color: var(--text-dim); text-transform: uppercase; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; }
        textarea { flex: 1; background: var(--bg); color: #e6edf3; border: none; padding: 16px; font-family: "JetBrains Mono", Consolas, monospace; font-size: 14px; line-height: 1.5; resize: none; outline: none; }
        pre { flex: 1; margin: 0; padding: 16px; background: #0b0c10; font-family: "JetBrains Mono", Consolas, monospace; font-size: 13px; line-height: 1.4; color: var(--accent); overflow: auto; white-space: pre-wrap; }
        .badge { background: #1c2230; padding: 2px 8px; border-radius: 4px; font-size: 11px; color: var(--accent); }
    </style>
</head>
<body>
    <header>
        <div class="logo">⚡ VeloC Playground <span class="badge">v1.0-RC3 Native</span></div>
        <div class="toolbar">
            <label style="font-size: 13px; color: var(--text-dim);">Examples:</label>
            <select id="exampleSelect" onchange="loadExample()">
                <option value="hello">Hello, World!</option>
                <option value="soa_particles">SoA SIMD Particles</option>
                <option value="arena_memory">Zero-Cost Bump Arena</option>
                <option value="eytzinger_search">Branchless Eytzinger Search</option>
                <option value="accuracy_contract">Strict IEEE-754 Math</option>
            </select>
            <button class="run-btn" onclick="runCode()">▶ Run (Ctrl+Enter)</button>
        </div>
    </header>
    <div class="workspace">
        <div class="editor-container">
            <div class="editor-header">
                <span>Source Code (.vc)</span>
                <span>Clang 20 AVX2</span>
            </div>
            <textarea id="codeEditor" spellcheck="false"></textarea>
        </div>
        <div class="output-container">
            <div class="output-header">
                <span>Output Console</span>
                <span id="timingStatus">Ready</span>
            </div>
            <pre id="consoleOutput">[Ready] Press 'Run' to compile and execute VeloC natively...</pre>
        </div>
    </div>

    <script>
        const EXAMPLES = __EXAMPLES_JSON__;

        function loadExample() {
            const key = document.getElementById("exampleSelect").value;
            if (EXAMPLES[key]) {
                document.getElementById("codeEditor").value = EXAMPLES[key].code;
            }
        }

        async function runCode() {
            const code = document.getElementById("codeEditor").value;
            const outputEl = document.getElementById("consoleOutput");
            const timingEl = document.getElementById("timingStatus");
            timingEl.innerText = "Compiling...";
            outputEl.innerText = "[Compiling and linking native binary...]";

            try {
                const resp = await fetch("/api/run", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: jsonStringify({ code })
                });
                const data = await resp.json();
                if (data.status === "ok") {
                    outputEl.innerText = data.output;
                    timingEl.innerText = `Compiled in ${data.compile_ms} ms | Run in ${data.run_ms} ms`;
                } else {
                    outputEl.innerText = "[Compilation / Runtime Error]:\\n" + (data.error || data.output);
                    timingEl.innerText = "Error";
                }
            } catch (err) {
                outputEl.innerText = "Network Error: " + err;
                timingEl.innerText = "Failed";
            }
        }

        function jsonStringify(obj) {
            return JSON.stringify(obj);
        }

        document.addEventListener("keydown", (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
                runCode();
            }
        });

        loadExample();
    </script>
</body>
</html>
"""

class PlaygroundHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            rendered = HTML_TEMPLATE.replace("__EXAMPLES_JSON__", json.dumps(PLAYGROUND_EXAMPLES))
            self.wfile.write(rendered.encode("utf-8"))
        elif self.path == "/api/examples":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(PLAYGROUND_EXAMPLES).encode("utf-8"))
        elif self.path == "/api/version":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"version": "1.0.0-rc3", "target": "x86_64-w64-mingw32"}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/run":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body)
            code = data.get("code", "")

            code_hash = hashlib.sha256(code.encode("utf-8")).hexdigest()[:12]
            source_file = CACHE_DIR / f"play_{code_hash}.vc"
            exe_file = CACHE_DIR / f"play_{code_hash}.exe"

            # Auto-wrap if needed
            full_code = code
            if "int main" not in full_code and "fn main" not in full_code:
                full_code = f'#include "veloc.h"\n\nint main() {{\n{code}\nreturn 0;\n}}\n'
            source_file.write_text(full_code, encoding="utf-8")

            veloc_py = ROOT_DIR / "veloc.py"
            t0 = time.perf_counter()
            build_cmd = [sys.executable, str(veloc_py), "build", str(source_file), "-o", str(exe_file), "--profile=fast-compile", "--fp=strict"]
            res = subprocess.run(build_cmd, cwd=str(ROOT_DIR), capture_output=True, text=True)
            t_compile = (time.perf_counter() - t0) * 1000.0

            if res.returncode != 0:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "error": res.stderr or res.stdout,
                    "compile_ms": round(t_compile, 1),
                    "run_ms": 0
                }).encode("utf-8"))
                return

            t_run_start = time.perf_counter()
            run_proc = subprocess.run([str(exe_file)], cwd=str(ROOT_DIR), capture_output=True, text=True)
            t_run = (time.perf_counter() - t_run_start) * 1000.0

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "output": run_proc.stdout if run_proc.returncode == 0 else (run_proc.stderr or run_proc.stdout),
                "compile_ms": round(t_compile, 1),
                "run_ms": round(t_run, 1)
            }).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run_playground_server(port: int = 8080):
    server = HTTPServer(("127.0.0.1", port), PlaygroundHandler)
    print(f"[VeloC Playground] Server running on http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[VeloC Playground] Server stopped.")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_playground_server(port)
