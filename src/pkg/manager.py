# VeloC Package Manager (veloc.toml / veloc.lock)
# Provides 'new', 'init', 'add', 'remove', 'build', 'run', 'test', 'clean' for VeloC projects.

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List

class PackageManager:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir

    def create_project(self, project_dir: Path, name: str, template: str = "minimal"):
        project_dir.mkdir(parents=True, exist_ok=True)
        src_dir = project_dir / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        tests_dir = project_dir / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)

        dep_lines = ""
        if template == "cli":
            dep_lines = 'veloc-cli = "0.1.0"\n'
            main_body = f"""import veloc_cli;

fn main() -> i32 {{
    let mut parser = ArgParser("{name}");
    println("=== {name} CLI App ===");
    println("Terminal tools powered by VeloC");
    return 0;
}}
"""
        elif template == "game":
            dep_lines = 'veloc-game = "0.1.0"\n'
            main_body = f"""import veloc_game;

fn main() -> i32 {{
    let mut world = GameWorld();
    let e = world.spawn();
    println("=== {name} Game Engine App ===");
    println(f"Spawned entity ID {{e}} in high-performance sparse-set ECS");
    return 0;
}}
"""
        elif template == "ai":
            dep_lines = 'veloc-ai = "0.1.0"\n'
            main_body = f"""import veloc_ai;

fn main() -> i32 {{
    let t = Tensor<f32>(16, 16);
    println("=== {name} AI & Tensor App ===");
    println(f"Allocated 32-byte aligned 16x16 tensor (elements: {{t.total_size}})");
    return 0;
}}
"""
        elif template == "web":
            dep_lines = 'veloc-net = "0.1.0"\n'
            main_body = f"""import veloc_net;

fn main() -> i32 {{
    let mut req = HttpRequest();
    HttpRequest::parse("GET /api/v1/health HTTP/1.1\\r\\nHost: localhost\\r\\n\\r\\n", req);
    let resp = HttpResponse(200, "application/json", "{{\\"status\\": \\"healthy\\"}}");
    println("=== {name} High-Speed Web Server ===");
    println(f"Routed request path: {{req.path}} -> HTTP {{resp.status_code}}");
    return 0;
}}
"""
        else: # minimal
            main_body = f"""fn main() -> i32 {{
    println("==================================================");
    println("      Welcome to {name} powered by VeloC 9.2!     ");
    println("==================================================");

    let mut count = 1000;
    println(f"Running application with count = {{count}}");
    return 0;
}}
"""

        manifest_content = f"""[package]
name = "{name}"
version = "0.1.0"
authors = ["Developer"]
edition = "2026"
description = "High-performance VeloC application"

[dependencies]
{dep_lines}
[build]
opt_level = "-O3"
simd = "avx2"
fma = true
"""
        main_content = f"module Main;\n\n{main_body}"
        test_content = f"""module Tests;

test "sanity check" {{
    assert_eq(2 + 2, 4);
    assert_true(100 > 50);
}}
"""
        (project_dir / "veloc.toml").write_text(manifest_content, encoding="utf-8")
        (src_dir / "main.vc").write_text(main_content, encoding="utf-8")
        (tests_dir / "test_main.vc").write_text(test_content, encoding="utf-8")
        self.update_lock(project_dir)
        print(f"[VeloC Package Manager] Project '{name}' (template: {template}) created at {project_dir}")

    def update_lock(self, project_dir: Path):
        manifest_path = project_dir / "veloc.toml"
        if not manifest_path.exists():
            return
        manifest_bytes = manifest_path.read_bytes()
        manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()

        lock_data = {
            "version": 1,
            "manifest_hash": manifest_hash,
            "packages": [
                {
                    "name": self.get_package_name(project_dir),
                    "version": "0.1.0",
                    "dependencies": []
                }
            ]
        }
        (project_dir / "veloc.lock").write_text(json.dumps(lock_data, indent=2), encoding="utf-8")

    def get_package_name(self, project_dir: Path) -> str:
        manifest_path = project_dir / "veloc.toml"
        if manifest_path.exists():
            for line in manifest_path.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("name ="):
                    return line.split("=")[1].strip().strip('"').strip("'")
        return project_dir.name

    def add_dependency(self, project_dir: Path, dep_name: str, version: str = "*"):
        manifest_path = project_dir / "veloc.toml"
        if not manifest_path.exists():
            print(f"[Error] veloc.toml not found in {project_dir}")
            return
        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        new_lines = []
        in_deps = False
        added = False
        for line in lines:
            new_lines.append(line)
            if line.strip() == "[dependencies]":
                in_deps = True
                new_lines.append(f'{dep_name} = "{version}"')
                added = True
        if not added:
            new_lines.append("\n[dependencies]")
            new_lines.append(f'{dep_name} = "{version}"')

        manifest_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        self.update_lock(project_dir)
        print(f"[VeloC Package Manager] Added dependency '{dep_name}' to {manifest_path}")

    def remove_dependency(self, project_dir: Path, dep_name: str):
        manifest_path = project_dir / "veloc.toml"
        if not manifest_path.exists():
            return
        lines = manifest_path.read_text(encoding="utf-8").splitlines()
        new_lines = [l for l in lines if not l.strip().startswith(dep_name + " =")]
        manifest_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        self.update_lock(project_dir)
        print(f"[VeloC Package Manager] Removed dependency '{dep_name}'")
