#!/usr/bin/env python3
"""
Multi-Shot Color Continuity Contact Sheet Generator (`contact_sheet.py`).

Uses FFmpeg's `scale` and `tile` video filters to composite a folder or explicit
list of keyframe stills (`SH-010.png`, `SH-020.png`, etc.) into a single tiled
overview image (`contact_sheet.png`) so the art director can inspect shot-to-shot
black floor, white balance, and value hierarchy side by side.
"""

from __future__ import annotations

import argparse
import math
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="contact_sheet.py",
        description="Build a tiled contact sheet image from rendered keyframe stills using FFmpeg.",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Directory containing rendered keyframe PNG/JPG images.",
    )
    parser.add_argument(
        "--columns",
        type=int,
        default=4,
        help="Number of tile columns across the contact sheet (default: 4).",
    )
    parser.add_argument(
        "--thumb-width",
        type=int,
        default=480,
        help="Width in pixels of each thumbnail tile (default: 480).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output path for the generated contact sheet PNG.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Verify input images and print the FFmpeg tile filter command without executing.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    in_dir = args.input_dir.resolve()
    if not in_dir.is_dir():
        print(f"[ERROR] Input directory not found: {in_dir}", file=sys.stderr)
        return 1

    images = sorted(
        [p for p in in_dir.iterdir() if p.is_file() and p.suffix.lower() in (".png", ".jpg", ".jpeg")]
    )
    if not images:
        print(f"[ERROR] Zero PNG/JPG images found in {in_dir}", file=sys.stderr)
        return 1

    cols = max(1, args.columns)
    rows = max(1, math.ceil(len(images) / cols))
    thumb_h = int(round(args.thumb_width * 9.0 / 16.0))

    cmd = ["ffmpeg", "-y"]
    for img in images:
        cmd.extend(["-i", str(img)])

    filter_parts: list[str] = []
    stream_labels: list[str] = []
    for idx in range(len(images)):
        lbl = f"[v{idx}]"
        filter_parts.append(
            f"[{idx}:v]scale={args.thumb_width}:{thumb_h}:force_original_aspect_ratio=decrease,"
            f"pad={args.thumb_width}:{thumb_h}:(ow-iw)/2:(oh-ih)/2:black{lbl}"
        )
        stream_labels.append(lbl)

    concat_And_tile = (
        f"{''.join(stream_labels)}concat=n={len(images)}:v=1:a=0,"
        f"tile={cols}x{rows}:margin=8:padding=6:color=0x141414[out]"
    )
    filter_parts.append(concat_And_tile)

    cmd.extend(
        [
            "-filter_complex",
            ";".join(filter_parts),
            "-map",
            "[out]",
            "-frames:v",
            "1",
            str(args.output.resolve()),
        ]
    )

    print(f"[INFO] Found {len(images)} keyframes -> {cols}x{rows} contact sheet grid.")
    print(f"[CMD]  {' '.join(cmd)}")

    if args.dry_run:
        print("[OK] Contact sheet dry-run complete.")
        return 0

    if shutil.which("ffmpeg") is None:
        print("[ERROR] 'ffmpeg' binary not found in PATH.", file=sys.stderr)
        return 1

    args.output.resolve().parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(cmd, check=False)
    if proc.returncode != 0:
        print(f"[FAIL] FFmpeg contact sheet generation failed (code {proc.returncode}).", file=sys.stderr)
        return proc.returncode

    print(f"[OK] Saved contact sheet -> {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
