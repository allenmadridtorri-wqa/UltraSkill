#!/usr/bin/env python3
"""
3-Frame Colab Cycles Benchmark & 3-Hour Budget Gate (`benchmark_scene.py`).

Enforces Section 4 Colab Safety:
  - Renders three representative frames (default: start, middle, end/peak).
  - Measures per-frame wall time and queries peak GPU VRAM via `nvidia-smi`.
  - Computes estimated total sequence hours:
      estimated_hours = (mean_frame_seconds * total_frames) / 3600
  - If estimated_hours > 3.0 and `--user-approved-over-3h` is not set, exits with
    status code 4 so the pipeline halts and asks the user for approval.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


APPROVAL_THRESHOLD_HOURS = 3.0
T4_SAFE_VRAM_MB = 12800  # 12.5 GB starting value on a 15 GB Tesla T4


def extract_script_args(argv: list[str]) -> list[str]:
    if "--" in argv:
        return argv[argv.index("--") + 1 :]
    return argv[1:]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    raw_args = extract_script_args(sys.argv if argv is None else ["benchmark_scene.py", *argv])
    parser = argparse.ArgumentParser(
        prog="benchmark_scene.py",
        description=(
            "Benchmark 3 representative frames in Blender Cycles OptiX, report peak VRAM "
            "and estimated total hours, and block jobs > 3.0 hours without user approval."
        ),
    )
    parser.add_argument(
        "--frames",
        default="1,50,100",
        help="Comma-separated list of 3 representative frame numbers (default: '1,50,100').",
    )
    parser.add_argument(
        "--total-frames",
        type=int,
        required=True,
        help="Total number of frames in the planned render job.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/tmp/ultraskill_benchmark"),
        help="Directory to write benchmark frames and JSON report.",
    )
    parser.add_argument(
        "--simulate-times",
        default=None,
        help=(
            "Optional comma-separated frame times in seconds (e.g. '12.4,15.1,14.5') for "
            "dry-run budget calculation outside Blender."
        ),
    )
    parser.add_argument(
        "--user-approved-over-3h",
        action="store_true",
        help="Pass only after the user explicitly approves an estimated render time > 3.0 hours.",
    )
    return parser.parse_args(raw_args)


def get_gpu_vram_used_mb() -> int:
    cmd = ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=5)
        if proc.returncode == 0 and proc.stdout.strip():
            return int(proc.stdout.strip().splitlines()[0].strip())
    except Exception:
        return 0
    return 0


def evaluate_budget(
    frame_numbers: list[int],
    frame_times: list[float],
    peak_vram_mb: int,
    total_frames: int,
    approved_over_3h: bool,
) -> tuple[dict, int]:
    avg_sec = sum(frame_times) / len(frame_times)
    max_sec = max(frame_times)
    estimated_hours = (avg_sec * total_frames) / 3600.0
    pessimistic_hours = (max_sec * total_frames) / 3600.0

    requires_approval = estimated_hours > APPROVAL_THRESHOLD_HOURS
    vram_warning = peak_vram_mb > T4_SAFE_VRAM_MB

    status = "APPROVED"
    exit_code = 0
    if requires_approval and not approved_over_3h:
        status = "REQUIRES_USER_APPROVAL_OVER_3H"
        exit_code = 4

    report = {
        "benchmark_frames": frame_numbers,
        "frame_seconds": [round(t, 3) for t in frame_times],
        "mean_frame_seconds": round(avg_sec, 3),
        "max_frame_seconds": round(max_sec, 3),
        "total_frames": total_frames,
        "estimated_total_hours": round(estimated_hours, 3),
        "pessimistic_total_hours": round(pessimistic_hours, 3),
        "approval_threshold_hours": APPROVAL_THRESHOLD_HOURS,
        "peak_vram_mb": peak_vram_mb,
        "t4_safe_vram_ceiling_mb": T4_SAFE_VRAM_MB,
        "vram_warning": vram_warning,
        "status": status,
    }
    return report, exit_code


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        frame_numbers = [int(x.strip()) for x in args.frames.split(",") if x.strip()]
    except ValueError:
        print(f"[ERROR] Invalid --frames list: '{args.frames}'", file=sys.stderr)
        return 2

    if len(frame_numbers) != 3:
        print(
            f"[ERROR] Exactly 3 representative frames are required (got {len(frame_numbers)}: {frame_numbers}).",
            file=sys.stderr,
        )
        return 2

    output_dir: Path = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    frame_times: list[float] = []
    peak_vram_mb = 0

    if args.simulate_times is not None:
        frame_times = [float(x.strip()) for x in args.simulate_times.split(",") if x.strip()]
        if len(frame_times) != 3:
            print("[ERROR] --simulate-times must provide 3 comma-separated floats.", file=sys.stderr)
            return 2
    else:
        try:
            import bpy  # type: ignore
        except ImportError:
            print(
                "[ERROR] 'bpy' not found. Run inside Blender (`blender -b scene.blend -P ...`) "
                "or pass --simulate-times for dry-run calculation.",
                file=sys.stderr,
            )
            return 2

        scene = bpy.context.scene
        if scene.cycles.device != "GPU":
            print("[FATAL] Scene Cycles device is not set to GPU. Run optix_verify.py first.", file=sys.stderr)
            return 1

        for frame_no in frame_numbers:
            scene.frame_set(frame_no)
            out_file = output_dir / f"bench_frame_{frame_no:04d}.png"
            scene.render.filepath = str(out_file)
            t0 = time.monotonic()
            bpy.ops.render.render(write_still=True)
            dt = time.monotonic() - t0
            frame_times.append(dt)
            vram_now = get_gpu_vram_used_mb()
            peak_vram_mb = max(peak_vram_mb, vram_now)
            print(f"[BENCH] Frame {frame_no:04d}: {dt:.2f}s (VRAM: {vram_now} MB)")

    report, exit_code = evaluate_budget(
        frame_numbers=frame_numbers,
        frame_times=frame_times,
        peak_vram_mb=peak_vram_mb,
        total_frames=args.total_frames,
        approved_over_3h=args.user_approved_over_3h,
    )

    report_path = output_dir / "benchmark_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("=== 3-Frame Cycles OptiX Benchmark Summary ===")
    print(f"Frames Tested         : {report['benchmark_frames']}")
    print(f"Frame Times (s)       : {report['frame_seconds']} (mean: {report['mean_frame_seconds']}s)")
    print(f"Total Planned Frames  : {report['total_frames']}")
    print(f"Estimated Total Hours : {report['estimated_total_hours']} h (max-based: {report['pessimistic_total_hours']} h)")
    print(f"Peak GPU VRAM         : {report['peak_vram_mb']} MB (safe ceiling: {T4_SAFE_VRAM_MB} MB)")
    print(f"Report Written        : {report_path}")

    if exit_code == 4:
        print(
            f"[HALT] Estimated render time ({report['estimated_total_hours']} h) exceeds the "
            f"{APPROVAL_THRESHOLD_HOURS} h safety gate. Show this estimate to the user and wait "
            "for explicit approval before passing --user-approved-over-3h.",
            file=sys.stderr,
        )
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
