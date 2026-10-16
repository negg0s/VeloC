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

    def create_project(self, project_dir: Path, name: str):
        project_dir.mkdir(parents=True, exist_ok=True)
        src_dir = project_dir / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        tests_dir = project_dir / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)

        manifest_content = f"""[package]
name = "{name}"
version = "0.1.0"
authors = ["Developer"]
edition = "2026"
description = "High-performance VeloC application"

[dependencies]

[build]
opt_level = "-O3"
simd = "avx2"
fma = true
"""
        main_content = f"""module Main;

fn main() -> i32 {{
    println("==================================================");
    println("      Welcome to {name} powered by VeloC 9.0!     ");
    println("==================================================");

    let mut count = 1000;
    println(f"Running application with count = {{count}}");
    return 0;
}}
"""
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
        print(f"[VeloC Package Manager] Project '{name}' created at {project_dir}")

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
