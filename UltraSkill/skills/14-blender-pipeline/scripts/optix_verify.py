#!/usr/bin/env python3
"""
Mandatory Blender Cycles OptiX GPU Proof Script (`optix_verify.py`).

Usage inside headless Blender on Google Colab:
  blender -b -P skills/14-blender-pipeline/scripts/optix_verify.py -- --output /tmp/optix_proof.png

Usage for standalone CLI help or dry-run validation:
  python3 skills/14-blender-pipeline/scripts/optix_verify.py --help

Enforces Section 4 Render Standard:
  1. Sets Cycles preferences `compute_device_type = 'OPTIX'`.
  2. Refreshes device list via `get_devices()`, enables only hardware GPU devices,
     and explicitly disables CPU fallback devices.
  3. Sets `scene.cycles.device = 'GPU'`.
  4. Prints Blender version, GPU name, driver version, and `nvidia-smi` telemetry.
  5. Renders 1 test frame and confirms output file creation and GPU memory usage.
  6. Never falls back to CPU silently. If OptiX fails, exits non-zero, prints the
     exact error, and instructs the agent to ask the user before passing
     `--allow-cuda-fallback`.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def extract_script_args(argv: list[str]) -> list[str]:
    if "--" in argv:
        idx = argv.index("--")
        return argv[idx + 1 :]
    return argv[1:]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    raw_args = extract_script_args(sys.argv if argv is None else ["optix_verify.py", *argv])
    parser = argparse.ArgumentParser(
        prog="optix_verify.py",
        description=(
            "Configure and prove Blender Cycles OptiX GPU rendering on Google Colab. "
            "Fails loudly if OptiX is unavailable; never falls back to CPU silently."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("/tmp/optix_proof_0001.png"),
        help="Output path for the 1-frame GPU proof render (default: /tmp/optix_proof_0001.png).",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=32,
        help="Sample count for the proof frame (default: 32 starting value).",
    )
    parser.add_argument(
        "--allow-cuda-fallback",
        action="store_true",
        help=(
            "Only set this after the user explicitly approves falling back from OPTIX to CUDA. "
            "CPU fallback remains strictly forbidden."
        ),
    )
    parser.add_argument(
        "--json-report",
        type=Path,
        default=None,
        help="Optional path to write structured JSON telemetry report.",
    )
    return parser.parse_args(raw_args)


def query_nvidia_smi() -> dict[str, str]:
    cmd = [
        "nvidia-smi",
        "--query-gpu=name,driver_version,memory.total,memory.used,utilization.gpu",
        "--format=csv,noheader",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=10)
    except FileNotFoundError:
        return {
            "ok": "false",
            "error": "nvidia-smi binary not found in PATH. No NVIDIA GPU runtime detected.",
        }
    except Exception as exc:
        return {"ok": "false", "error": f"nvidia-smi execution failed: {exc}"}

    if proc.returncode != 0:
        return {
            "ok": "false",
            "error": f"nvidia-smi exited with code {proc.returncode}: {proc.stderr.strip()}",
        }

    first_line = proc.stdout.strip().splitlines()[0] if proc.stdout.strip() else ""
    parts = [p.strip() for p in first_line.split(",")]
    if len(parts) >= 5:
        return {
            "ok": "true",
            "gpu_name": parts[0],
            "driver_version": parts[1],
            "memory_total": parts[2],
            "memory_used": parts[3],
            "utilization_gpu": parts[4],
            "raw": proc.stdout.strip(),
        }
    return {"ok": "true", "raw": proc.stdout.strip()}


def configure_and_prove_blender(args: argparse.Namespace) -> int:
    try:
        import bpy  # type: ignore
    except ImportError:
        print(
            "[ERROR] 'bpy' module not found. Run this script inside headless Blender:\n"
            "  blender -b -P skills/14-blender-pipeline/scripts/optix_verify.py -- --output /tmp/optix_proof.png",
            file=sys.stderr,
        )
        return 2

    smi_before = query_nvidia_smi()
    print("=== UltraSkill Cycles OptiX Hardware Proof ===")
    print(f"Blender Version : {bpy.app.version_string}")
    if smi_before.get("ok") == "true":
        print(f"NVIDIA GPU Name : {smi_before.get('gpu_name', smi_before.get('raw'))}")
        print(f"Driver Version  : {smi_before.get('driver_version', 'unknown')}")
        print(f"VRAM Total/Used : {smi_before.get('memory_total')} / {smi_before.get('memory_used')}")
    else:
        print(f"[FATAL] nvidia-smi check failed before render: {smi_before.get('error')}", file=sys.stderr)
        return 1

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"

    prefs = bpy.context.preferences
    if "cycles" not in prefs.addons:
        bpy.ops.preferences.addon_enable(module="cycles")
    cprefs = prefs.addons["cycles"].preferences

    requested_backend = "OPTIX"
    try:
        cprefs.compute_device_type = "OPTIX"
    except Exception as exc:
        if not args.allow_cuda_fallback:
            print(
                f"[FATAL] Failed to set Cycles compute_device_type = 'OPTIX': {exc}\n"
                "STOPPING: Silent fallback is forbidden. Report this exact error to the user "
                "and ask if they approve re-running with --allow-cuda-fallback.",
                file=sys.stderr,
            )
            return 1
        print(f"[WARN] OPTIX unavailable ({exc}); user approved CUDA fallback.")
        requested_backend = "CUDA"
        cprefs.compute_device_type = "CUDA"

    cprefs.get_devices()
    enabled_gpu_devices: list[str] = []
    disabled_devices: list[str] = []

    for device in cprefs.devices:
        if device.type == requested_backend:
            device.use = True
            enabled_gpu_devices.append(f"{device.name} ({device.type})")
        else:
            device.use = False
            disabled_devices.append(f"{device.name} ({device.type})")

    if not enabled_gpu_devices:
        if requested_backend == "OPTIX" and not args.allow_cuda_fallback:
            print(
                "[FATAL] Zero OPTIX GPU devices found after refreshing device list.\n"
                f"Detected non-OptiX devices: {disabled_devices}\n"
                "STOPPING: Silent CPU fallback is forbidden. Ask the user whether to approve "
                "--allow-cuda-fallback or check the Colab GPU runtime.",
                file=sys.stderr,
            )
            return 1
        print(
            f"[FATAL] Zero {requested_backend} GPU devices found. Refusing to render on CPU.",
            file=sys.stderr,
        )
        return 1

    scene.cycles.device = "GPU"
    print(f"Compute Backend : {cprefs.compute_device_type}")
    print(f"Scene Device    : {scene.cycles.device}")
    print(f"Enabled GPUs    : {', '.join(enabled_gpu_devices)}")
    print(f"Disabled (CPU)  : {', '.join(disabled_devices)}")

    # Configure a fast, deterministic 1-frame proof render
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100
    scene.cycles.samples = args.samples
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.05

    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(output_path)

    t0 = time.monotonic()
    bpy.ops.render.render(write_still=True)
    elapsed = time.monotonic() - t0

    smi_after = query_nvidia_smi()
    if not output_path.is_file() or output_path.stat().st_size == 0:
        print(f"[FATAL] Proof render output missing or empty at {output_path}", file=sys.stderr)
        return 1

    print(f"Proof Frame     : {output_path} ({output_path.stat().st_size} bytes)")
    print(f"Render Duration : {elapsed:.2f} s")
    print(
        f"nvidia-smi Post : VRAM Used={smi_after.get('memory_used', 'N/A')}, "
        f"GPU Util={smi_after.get('utilization_gpu', 'N/A')}"
    )
    print("[OK] Cycles GPU hardware proof succeeded without CPU fallback.")

    if args.json_report:
        report = {
            "status": "PASS",
            "blender_version": bpy.app.version_string,
            "compute_device_type": cprefs.compute_device_type,
            "scene_device": scene.cycles.device,
            "enabled_gpus": enabled_gpu_devices,
            "disabled_devices": disabled_devices,
            "render_seconds": round(elapsed, 3),
            "output_file": str(output_path),
            "output_bytes": output_path.stat().st_size,
            "nvidia_smi_before": smi_before,
            "nvidia_smi_after": smi_after,
        }
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return configure_and_prove_blender(args)


if __name__ == "__main__":
    sys.exit(main())
