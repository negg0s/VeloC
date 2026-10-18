"""
VeloC Hardware Inspector & Topology Discovery Engine
Extracts CPUID, cache hierarchy, SIMD ISA extensions, and GPU capabilities.
Outputs structured JSON and human-readable terminal reports.
"""

import sys
import os
import platform
import subprocess
import json
import hashlib
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any

ROOT_DIR = Path("D:/VeloC")

@dataclass
class CacheInfo:
    level: str
    size_kb: int
    line_size: int
    associativity: int
    shared_threads: int

@dataclass
class HardwareProfile:
    cpu_model: str
    physical_cores: int
    logical_cores: int
    base_mhz: int
    max_mhz: int
    arch: str
    simd_extensions: Dict[str, bool]
    vector_width_bits: int
    caches: Dict[str, CacheInfo]
    ram_total_gb: float
    gpu_info: Optional[Dict[str, Any]]
    hw_hash: str = ""

    def compute_hash(self) -> str:
        ident = f"{self.cpu_model}:{self.physical_cores}:{self.logical_cores}:{sorted(self.simd_extensions.items())}"
        return hashlib.sha256(ident.encode()).hexdigest()[:16]

class HardwareInspector:
    @staticmethod
    def _powershell_json(cmd: str):
        import subprocess
        try:
            res = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=30)
            if res.returncode == 0 and res.stdout.strip():
                return json.loads(res.stdout)
        except Exception:
            pass
        return None

    @staticmethod
    def _proc_cpuinfo() -> dict:
        try:
            info = Path("/proc/cpuinfo")
            if info.exists():
                text = info.read_text(encoding="utf-8", errors="replace")
                blocks = [b for b in text.split("\n\n") if b]
                first = dict(line.split(":", 1) for line in blocks[0].splitlines() if ":" in line)
                return {k.strip(): v.strip() for k, v in first.items()}
        except Exception:
            pass
        return {}

    @staticmethod
    def inspect() -> HardwareProfile:
        flags_map = {
            "sse": "SSE", "sse2": "SSE2", "sse3": "SSE3", "ssse3": "SSSE3",
            "sse4_1": "SSE4_1", "sse4_2": "SSE4_2", "avx": "AVX", "avx2": "AVX2",
            "fma": "FMA3", "f16c": "F16C", "bmi1": "BMI1", "bmi2": "BMI2",
            "aes": "AES_NI", "pclmulqdq": "PCLMULQDQ",
            "avx512f": "AVX512F", "neon": "ARM_NEON", "sve": "ARM_SVE",
        }
        cpu_model = "Unknown CPU"
        phys_cores = 0
        log_cores = os.cpu_count() or 0
        base_mhz = 0
        max_mhz = 0
        ram_gb = 0.0

        proc = HardwareInspector._proc_cpuinfo()
        if proc.get("model name"):
            cpu_model = proc["model name"]
            mhz = proc.get("cpu MHz", "").strip()
            if mhz:
                base_mhz = int(float(mhz))

        if sys.platform == "win32":
            data = HardwareInspector._powershell_json(
                "Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, "
                "NumberOfLogicalProcessors, MaxClockSpeed | ConvertTo-Json")
            if data:
                if data.get("Name"):
                    cpu_model = str(data["Name"]).strip()
                phys_cores = int(data.get("NumberOfCores", 0) or 0)
                log_cores = int(data.get("NumberOfLogicalProcessors", 0) or log_cores)
                max_mhz = int(data.get("MaxClockSpeed", 0) or 0)

        if sys.platform == "win32":
            data_ram = HardwareInspector._powershell_json(
                "Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory | ConvertTo-Json")
            if data_ram:
                total_bytes = int(data_ram.get("TotalPhysicalMemory", 0) or 0)
                ram_gb = round(total_bytes / (1024**3), 2)
        else:
            try:
                meminfo = Path("/proc/meminfo")
                if meminfo.exists():
                    for line in meminfo.read_text(encoding="utf-8").splitlines():
                        if line.startswith("MemTotal:"):
                            ram_gb = round(int(line.split()[1]) / (1024**2), 2)
                            break
            except Exception:
                pass

        # SIMD feature detection: trustworthy only via /proc/cpuinfo flags.
        # On Windows without a CPUID probe we report nothing as True rather
        # than guessing a marketing table.
        cpu_flags: list[str] = []
        if "flags" in proc:
            cpu_flags = proc["flags"].split()
        simd_features = {nice: (flag in cpu_flags) for flag, nice in flags_map.items()}

        vector_width = 256 if simd_features.get("AVX2") else (128 if any(simd_features.values()) else 0)

        # Cache hierarchy: reported only when actually detected (/proc/cpuinfo
        # or platform APIs); the previous hardcoded table was removed.
        caches: Dict[str, CacheInfo] = {}
        if "cache size" in proc:
            try:
                caches["L3"] = CacheInfo(level="L3", size_kb=int(proc["cache size"]), line_size=64,
                                         associativity=0, shared_threads=log_cores or 0)
            except (ValueError, TypeError):
                pass

        gpu_info = None
        if sys.platform == "win32":
            gdata = HardwareInspector._powershell_json(
                "Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, AdapterRAM | ConvertTo-Json")
            if gdata:
                candidates = gdata if isinstance(gdata, list) else [gdata]
                gpu = candidates[0] if candidates else None
                if gpu and gpu.get("Name"):
                    ram_bytes = int(gpu.get("AdapterRAM") or 0)
                    gpu_info = {
                        "name": gpu.get("Name"),
                        "driver": gpu.get("DriverVersion"),
                        "vram_mb": round(ram_bytes / (1024**2)) if ram_bytes else None,
                    }

        arch = platform.machine() or "unknown"

        profile = HardwareProfile(
            cpu_model=cpu_model,
            physical_cores=phys_cores,
            logical_cores=log_cores,
            base_mhz=base_mhz,
            max_mhz=max_mhz,
            arch=arch,
            simd_extensions=simd_features,
            vector_width_bits=vector_width,
            caches=caches,
            ram_total_gb=ram_gb,
            gpu_info=gpu_info
        )
        profile.hw_hash = profile.compute_hash()
        return profile

    @staticmethod
    def render_report(profile: HardwareProfile, as_json: bool = False) -> str:
        if as_json:
            d = asdict(profile)
            return json.dumps(d, indent=2)

        def val(x, unit="", unknown="unknown"):
            return unknown if not x else f"{x}{unit}"

        def fmt_cores(phys, logical):
            if logical > 0 and phys > 0:
                return f"{phys} Physical Cores / {logical} Hardware Threads (SMT/HT)"
            if logical > 0:
                return f"{logical} Logical Cores (physical count not detected)"
            return "unknown"

        def fmt_clocks(base, mx):
            if base or mx:
                base_str = f"{base} MHz" if base else "unknown"
                mx_str = f"{mx} MHz" if mx else "unknown"
                return f"Base {base_str} / Max {mx_str}"
            return "unknown"

        lines = [
            "================================================================================",
            "                   VeloC Hardware Inspector & Topology Report                   ",
            "================================================================================",
            f"  CPU Model:             {profile.cpu_model}",
            f"  Architecture:          {profile.arch} (Vector register width: {profile.vector_width_bits or 'unknown'}-bit)",
            f"  Topology:              {fmt_cores(profile.physical_cores, profile.logical_cores)}",
            f"  Clocks:                {fmt_clocks(profile.base_mhz, profile.max_mhz)}",
            f"  Total RAM:             {val(profile.ram_total_gb, ' GB')}",
            f"  Hardware Hash:         {profile.hw_hash}",
            "--------------------------------------------------------------------------------",
            "  Memory Cache Hierarchy:",
        ]

        cache_names = {"L1D": "L1 Data", "L1I": "L1 Instruction", "L2": "L2 Cache", "L3": "L3 Shared Cache"}
        if profile.caches:
            for key, info in profile.caches.items():
                lines.append(f"    - {cache_names.get(key, key)}: {info.size_kb} KB")
        else:
            lines.append("    - not detected on this platform (use `veloc hwinfo` after adding a CPUID probe)")

        lines.append("--------------------------------------------------------------------------------")
        lines.append("  SIMD & Instruction Set Architecture Extensions:")
        supported = [k for k, v in profile.simd_extensions.items() if v]
        if supported:
            lines.append(f"    [SUPPORTED]   {', '.join(supported)}")
            unsupported = [k for k, v in profile.simd_extensions.items() if not v]
            lines.append(f"    [UNSUPPORTED] {', '.join(unsupported)}")
        else:
            lines.append("    [UNKNOWN] no reliable detection on this platform yet (no /proc/cpuinfo)")

        lines.append("--------------------------------------------------------------------------------")
        if profile.gpu_info:
            lines.append("  Detected Hardware Accelerators (GPU):")
            lines.append(f"    - Device:            {profile.gpu_info.get('name')}")
            lines.append(f"    - Driver Version:    {profile.gpu_info.get('driver')}")
            lines.append(f"    - Dedicated VRAM:    {profile.gpu_info.get('vram_mb') or 'unknown'} MB")
            v = profile.gpu_info.get("vulkan_support")
            if v is not None:
                lines.append(f"    - Vulkan support:    {'yes' if v else 'no (detected, unverified)'}")
        else:
            lines.append("  Detected Accelerators: none detected")
        lines.append("================================================================================")
        return "\n".join(lines)

def run_hwinfo_cli(as_json: bool = False):
    prof = HardwareInspector.inspect()
    out_dir = ROOT_DIR / ".veloc"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "hw_profile.json").write_text(json.dumps(asdict(prof), indent=2), encoding="utf-8")
    print(HardwareInspector.render_report(prof, as_json=as_json))

if __name__ == "__main__":
    as_json = "--json" in sys.argv
    run_hwinfo_cli(as_json=as_json)
