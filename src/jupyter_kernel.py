# VeloC Jupyter Notebook Kernel
# Provides interactive high-performance execution of VeloC cells within Jupyter/VS Code notebooks.

import sys
import os
import subprocess
import hashlib
from pathlib import Path
from ipykernel.kernelbase import Kernel

ROOT_DIR = Path("D:/VeloC")
CACHE_DIR = ROOT_DIR / ".cache" / "jupyter"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

class VeloCKernel(Kernel):
    implementation = 'VeloC'
    implementation_version = '1.0'
    language = 'veloc'
    language_version = '1.0'
    language_info = {
        'name': 'veloc',
        'mimetype': 'text/x-veloc',
        'file_extension': '.vc'
    }
    banner = "⚡ VeloC Interactive Jupyter Kernel - Native Hardware Performance"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.veloc_py = ROOT_DIR / "veloc.py"

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        code_str = code.strip()
        if not code_str:
            return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [], 'user_expressions': {}}

        # Automatically wrap bare expressions or statements into main() if needed
        has_main = ("int main" in code_str) or ("fn main" in code_str) or ("void main" in code_str)
        if not has_main:
            cell_code = f"""#include "veloc.h"

int main() {{
    {code_str}
    return 0;
}}
"""
        else:
            cell_code = code_str
            if "include" not in cell_code:
                cell_code = '#include "veloc.h"\n\n' + cell_code

        code_hash = hashlib.sha256(cell_code.encode("utf-8")).hexdigest()[:12]
        cell_file = CACHE_DIR / f"cell_{code_hash}.vc"
        cell_file.write_text(cell_code, encoding="utf-8")

        # Compile and execute
        cmd = [sys.executable, str(self.veloc_py), "run", str(cell_file)]
        res = subprocess.run(cmd, cwd=str(ROOT_DIR), capture_output=True, text=True)

        if not silent:
            if res.stdout:
                # Clean up compiler banner if desired, or stream directly
                clean_lines = [l for l in res.stdout.splitlines() if not l.startswith("[VeloC") and not l.startswith("---")]
                stream_text = "\n".join(clean_lines).strip()
                if not stream_text and res.stdout:
                    stream_text = res.stdout.strip()
                if stream_text:
                    stream_content = {'name': 'stdout', 'text': stream_text + '\n'}
                    self.send_response(self.iopub_socket, 'stream', stream_content)
            
            if res.stderr or res.returncode != 0:
                err_text = res.stderr if res.stderr else res.stdout
                err_content = {'name': 'stderr', 'text': err_text + '\n'}
                self.send_response(self.iopub_socket, 'stream', err_content)

        return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [], 'user_expressions': {}}

def install_kernel():
    """Installs the VeloC kernel spec into Jupyter."""
    from jupyter_client.kernelspec import KernelSpecManager
    import json
    import tempfile

    kernel_dict = {
        "argv": [sys.executable, str(ROOT_DIR / "src" / "jupyter_kernel.py"), "-f", "{connection_file}"],
        "display_name": "VeloC",
        "language": "veloc"
    }

    with tempfile.TemporaryDirectory() as td:
        spec_path = Path(td) / "kernel.json"
        spec_path.write_text(json.dumps(kernel_dict, indent=2), encoding="utf-8")
        ksm = KernelSpecManager()
        ksm.install_kernel_spec(td, kernel_name="veloc", user=True)
        print("[SUCCESS] VeloC Jupyter Kernel registered successfully.")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        install_kernel()
    else:
        from ipykernel.kernelapp import IPKernelApp
        IPKernelApp.launch_instance(kernel_class=VeloCKernel)
