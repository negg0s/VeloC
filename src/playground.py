import os
import sys
import json
import subprocess
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>VeloC Interactive Web Playground</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; margin: 0; background: #121214; color: #e1e1e6; }
        header { background: #1a1a1e; padding: 15px 30px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #29292e; }
        h1 { margin: 0; font-size: 20px; color: #04d361; }
        .container { display: flex; height: calc(100vh - 70px); }
        .editor-pane, .output-pane { flex: 1; display: flex; flex-direction: column; padding: 20px; box-sizing: border-box; }
        textarea { flex: 1; background: #19191d; color: #a8a8b3; border: 1px solid #29292e; border-radius: 8px; padding: 15px; font-family: monospace; font-size: 14px; resize: none; outline: none; }
        textarea:focus { border-color: #04d361; }
        .controls { margin-bottom: 15px; display: flex; gap: 10px; }
        button { background: #04d361; color: #000; border: none; padding: 10px 20px; font-weight: bold; border-radius: 6px; cursor: pointer; transition: 0.2s; }
        button:hover { background: #00b34d; }
        pre { flex: 1; background: #0d0d0f; border: 1px solid #29292e; border-radius: 8px; padding: 15px; font-family: monospace; font-size: 14px; overflow: auto; color: #04d361; white-space: pre-wrap; }
    </style>
</head>
<body>
    <header>
        <h1>⚡ VeloC Web Playground</h1>
        <span>Target: Clang 20 AVX2 Windows Native</span>
    </header>
    <div class="container">
        <div class="editor-pane">
            <div class="controls">
                <button onclick="runCode()">▶ Run VeloC Code (Ctrl+Enter)</button>
            </div>
            <textarea id="code" spellcheck="false">module Playground;

pub fn main() -> i32 {
    let name = "Developer";
    println(f"Welcome to VeloC, {name}!");
    
    let mut sum = 0;
    for (let i in range(1, 11)) {
        sum += i;
    }
    println(f"Sum of 1..10 is: {sum}");
    return 0;
}
</textarea>
        </div>
        <div class="output-pane">
            <h3>Execution Console & Compiler Diagnostics</h3>
            <pre id="output">[Ready] Press 'Run' to compile and execute VeloC in sub-millisecond speeds...</pre>
        </div>
    </div>

    <script>
        async function runCode() {
            const code = document.getElementById('code').value;
            const out = document.getElementById('output');
            out.innerText = "[Compiling...]";
            try {
                const resp = await fetch('/compile', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code })
                });
                const data = await resp.json();
                out.innerText = data.output;
            } catch (err) {
                out.innerText = "Error: " + err;
            }
        }
        document.addEventListener('keydown', e => {
            if (e.ctrlKey && e.key === 'Enter') runCode();
        });
    </script>
</body>
</html>
"""

class PlaygroundHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML_TEMPLATE.encode('utf-8'))

    def do_POST(self):
        if self.path == '/compile':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            req = json.loads(post_data.decode('utf-8'))
            source_code = req.get('code', '')

            temp_vc = Path("D:/VeloC/.cache/playground_temp.vc")
            temp_vc.parent.mkdir(parents=True, exist_ok=True)
            temp_vc.write_text(source_code, encoding="utf-8")

            # Run via veloc.py run
            res = subprocess.run([sys.executable, "D:/VeloC/veloc.py", "run", str(temp_vc)],
                                 capture_output=True, text=True)
            output = res.stdout
            if res.stderr:
                output += "\n" + res.stderr

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'output': output}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def start_server(port=8080):
    server = HTTPServer(('127.0.0.1', port), PlaygroundHandler)
    print(f"[VeloC Playground] Server live at http://127.0.0.1:{port}")
    server.serve_forever()

if __name__ == "__main__":
    start_server()
