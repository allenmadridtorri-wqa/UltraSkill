#!/usr/bin/env python3
"""
Crash-Safe Resumable Cycles OptiX Sequence Renderer (`render_sequence.py`).

Enforces Section 4 Colab Safety:
  - Never assumes how long a Google Colab session will last.
  - Writes every finished frame (EXR or 16-bit PNG) directly to Google Drive.
  - Atomically updates `render_manifest.json` after each frame with SHA-256 hash,
    byte size, render duration, and completion timestamp.
  - On resume after a Colab disconnect, skips every frame that already exists on
    Google Drive, has non-zero size, and matches its manifest SHA-256 record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def extract_script_args(argv: list[str]) -> list[str]:
    if "--" in argv:
        return argv[argv.index("--") + 1 :]
    return argv[1:]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    raw_args = extract_script_args(sys.argv if argv is None else ["render_sequence.py", *argv])
    parser = argparse.ArgumentParser(
        prog="render_sequence.py",
        description="Render a frame range in Cycles OptiX with per-frame Google Drive persistence and automatic resume.",
    )
    parser.add_argument(
        "--start",
        type=int,
        required=True,
        help="First frame number (inclusive).",
    )
    parser.add_argument(
        "--end",
        type=int,
        required=True,
        help="Last frame number (inclusive).",
    )
    parser.add_argument(
        "--step",
        type=int,
        default=1,
        help="Frame step increment (default: 1).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Google Drive directory where rendered frames are saved (e.g. /content/drive/MyDrive/renders/shot01).",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
        help="Path to render_manifest.json on Google Drive.",
    )
    parser.add_argument(
        "--prefix",
        default="frame_",
        help="Filename prefix for rendered frames (default: 'frame_').",
    )
    parser.add_argument(
        "--format",
        choices=["OPEN_EXR_MULTILAYER", "OPEN_EXR", "PNG"],
        default="PNG",
        help="Output image format: PNG (16-bit) or OPEN_EXR_MULTILAYER (default: PNG).",
    )
    return parser.parse_args(raw_args)


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with filepath.open("rb") as fh:
        while chunk := fh.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_or_init_manifest(manifest_path: Path, args: argparse.Namespace) -> dict:
    if manifest_path.is_file():
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"[WARN] Could not parse existing manifest ({exc}); initializing fresh record.", file=sys.stderr)

    return {
        "schema_version": "1.0.0",
        "start_frame": args.start,
        "end_frame": args.end,
        "frame_step": args.step,
        "format": args.format,
        "output_dir": str(args.output_dir.resolve()),
        "updated_utc": datetime.now(timezone.utc).isoformat(),
        "frames": {},
    }


def save_manifest_atomic(manifest_path: Path, data: dict) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_utc"] = datetime.now(timezone.utc).isoformat()
    tmp_path = manifest_path.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp_path, manifest_path)


def is_frame_valid_on_disk(frame_path: Path, record: dict | None) -> bool:
    if not frame_path.is_file():
        return False
    size = frame_path.stat().st_size
    if size < 128:
        return False
    if record and record.get("status") == "COMPLETED":
        expected_size = record.get("bytes")
        expected_sha = record.get("sha256")
        if expected_size and size != expected_size:
            return False
        if expected_sha and compute_sha256(frame_path) != expected_sha:
            return False
        return True
    return False


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.end < args.start or args.step < 1:
        print("[ERROR] Invalid frame range: ensure --end >= --start and --step >= 1.", file=sys.stderr)
        return 2

    try:
        import bpy  # type: ignore
    except ImportError:
        print(
            "[ERROR] 'bpy' module not found. Run inside headless Blender on Google Colab:\n"
            "  blender -b scene.blend -P skills/14-blender-pipeline/scripts/render_sequence.py -- ...",
            file=sys.stderr,
        )
        return 2

    output_dir: Path = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path: Path = args.manifest.resolve()
    manifest = load_or_init_manifest(manifest_path, args)

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    if scene.cycles.device != "GPU":
        print("[FATAL] Cycles device is not GPU. Run optix_verify.py before render_sequence.py.", file=sys.stderr)
        return 1

    ext = ".exr" if "EXR" in args.format else ".png"
    scene.render.image_settings.file_format = args.format
    scene.render.image_settings.color_depth = "16"

    frames_to_process = list(range(args.start, args.end + 1, args.step))
    skipped = 0
    rendered = 0

    for frame_no in frames_to_process:
        frame_key = str(frame_no)
        frame_filename = f"{args.prefix}{frame_no:04d}{ext}"
        frame_path = output_dir / frame_filename
        existing_record = manifest.get("frames", {}).get(frame_key)

        if is_frame_valid_on_disk(frame_path, existing_record):
            print(f"[SKIP] Frame {frame_no:04d} already verified on Drive ({frame_filename})")
            skipped += 1
            continue

        scene.frame_set(frame_no)
        scene.render.filepath = str(frame_path)
        t0 = time.monotonic()
        bpy.ops.render.render(write_still=True)
        elapsed = time.monotonic() - t0

        if not frame_path.is_file() or frame_path.stat().st_size < 128:
            manifest["frames"][frame_key] = {
                "file": frame_filename,
                "status": "CORRUPT_OR_MISSING",
                "updated_utc": datetime.now(timezone.utc).isoformat(),
            }
            save_manifest_atomic(manifest_path, manifest)
            print(f"[FATAL] Frame {frame_no:04d} failed to write valid output at {frame_path}", file=sys.stderr)
            return 1

        size_bytes = frame_path.stat().st_size
        sha256_hex = compute_sha256(frame_path)
        manifest["frames"][frame_key] = {
            "file": frame_filename,
            "status": "COMPLETED",
            "bytes": size_bytes,
            "sha256": sha256_hex,
            "render_seconds": round(elapsed, 3),
            "completed_utc": datetime.now(timezone.utc).isoformat(),
        }
        save_manifest_atomic(manifest_path, manifest)
        rendered += 1
        print(f"[DONE] Frame {frame_no:04d} -> {frame_filename} ({size_bytes} B, {elapsed:.2f}s)")

    print(
        f"[OK] Sequence complete: {rendered} rendered, {skipped} skipped on resume "
        f"(total {len(frames_to_process)} frames). Manifest: {manifest_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
