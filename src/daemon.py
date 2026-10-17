"""
VeloC Compiler Daemon (veloc daemon)
Persistent background compiler process providing warm AST cache,
pre-warmed PCH, and fast IPC build dispatching over localhost.
"""

import socket
import threading
import json
import time
import sys
import subprocess
from pathlib import Path
from typing import Optional, Dict

HOST = "127.0.0.1"
PORT = 45731
ROOT_DIR = Path("D:/VeloC")
PID_FILE = ROOT_DIR / ".cache" / "veloc_daemon.pid"

class CompilerDaemon:
    def __init__(self, root_dir: Path = ROOT_DIR, host: str = HOST, port: int = PORT):
        self.root_dir = Path(root_dir)
        self.host = host
        self.port = port
        self.running = False
        self.server_sock = None
        self.build_count = 0
        self.start_time = time.time()

        # Warm up PchManager and internal modules
        from pch_manager import PchManager
        self.pch_mgr = PchManager(ROOT_DIR)
        self.pch_mgr.ensure_pch("veloc.h", "-O3")
        self.pch_mgr.ensure_pch("veloc_core.h", "-O3")

    def handle_client(self, conn: socket.socket):
        try:
            raw_data = conn.recv(65536).decode("utf-8")
            if not raw_data:
                return
            req = json.loads(raw_data)
            cmd = req.get("command")

            if cmd == "ping":
                resp = {"status": "ok", "uptime_s": round(time.time() - self.start_time, 1), "build_count": self.build_count}
            elif cmd == "build":
                src_path = Path(req.get("file"))
                opt = req.get("opt", "-O3")
                profile = req.get("profile")

                t0 = time.perf_counter()
                from veloc import build_veloc
                out_exe = build_veloc(src_path, opt_level=opt, profile=profile, quiet=True)
                dur = (time.perf_counter() - t0) * 1000.0

                self.build_count += 1
                resp = {
                    "status": "ok",
                    "output": str(out_exe),
                    "duration_ms": round(dur, 2),
                    "build_id": self.build_count
                }
            elif cmd == "stop":
                resp = {"status": "stopping"}
                conn.sendall(json.dumps(resp).encode("utf-8"))
                self.running = False
                return
            else:
                resp = {"status": "error", "message": f"Unknown command: {cmd}"}

            conn.sendall(json.dumps(resp).encode("utf-8"))
        except Exception as e:
            err_resp = {"status": "error", "message": str(e)}
            conn.sendall(json.dumps(err_resp).encode("utf-8"))
        finally:
            conn.close()

    def start_foreground(self):
        self.running = True
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen(5)
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        PID_FILE.write_text(str(subprocess.os.getpid()))

        print(f"[VeloC Daemon] Running on {self.host}:{self.port} (PID: {subprocess.os.getpid()})")
        while self.running:
            try:
                self.server_sock.settimeout(1.0)
                conn, _ = self.server_sock.accept()
                threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()
            except socket.timeout:
                continue
            except Exception:
                break
        self.server_sock.close()
        if PID_FILE.exists():
            PID_FILE.unlink()
        print("[VeloC Daemon] Stopped.")

def is_daemon_running() -> bool:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        s.connect((HOST, PORT))
        s.sendall(json.dumps({"command": "ping"}).encode("utf-8"))
        res = json.loads(s.recv(4096).decode("utf-8"))
        s.close()
        return res.get("status") == "ok"
    except Exception:
        return False

def send_daemon_build(file_path: Path, opt: str = "-O3", profile: str = None) -> Optional[dict]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(60.0)
        s.connect((HOST, PORT))
        req = {"command": "build", "file": str(file_path), "opt": opt, "profile": profile}
        s.sendall(json.dumps(req).encode("utf-8"))
        res = json.loads(s.recv(65536).decode("utf-8"))
        s.close()
        return res
    except Exception:
        return None

def daemon_client_request(req_dict: dict, host: str = HOST, port: int = PORT) -> dict:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3.0)
        s.connect((host, port))
        cmd = req_dict.get("cmd") or req_dict.get("command")
        if cmd == "shutdown":
            cmd = "stop"
        req = dict(req_dict)
        req["command"] = cmd
        s.sendall(json.dumps(req).encode("utf-8"))
        res = json.loads(s.recv(65536).decode("utf-8"))
        s.close()
        return res
    except Exception as e:
        return {"status": "error", "message": str(e)}

VeloCDaemonServer = CompilerDaemon

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stop":
        stop_daemon()
    elif len(sys.argv) > 1 and sys.argv[1] == "status":
        running = is_daemon_running()
        print(f"[VeloC Daemon] Status: {'RUNNING' if running else 'STOPPED'}")
    else:
        daemon = CompilerDaemon()
        daemon.start_foreground()
