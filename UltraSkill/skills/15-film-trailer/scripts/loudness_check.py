#!/usr/bin/env python3
"""
EBU R128 Audio Loudness & True Peak Verifier (`loudness_check.py`).

Runs FFmpeg's `ebur128=peak=true` filter on an audio or video deliverable (or parses
an existing FFmpeg ebur128 summary log via `--parse-log`) and verifies:
  1. Integrated Loudness (`I`) is within `--target-lufs +- --tolerance-lu`
     (default: `-14.0 LUFS +- 1.0 LU`).
  2. Maximum True Peak (`TP`) is `<= --max-true-peak` (default: `-1.0 dBTP`).
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="loudness_check.py",
        description="Verify integrated loudness (-14 LUFS) and true peak (<= -1.0 dBTP) via FFmpeg ebur128.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Path to audio (.wav/.flac) or video (.mp4/.mov) file to measure.",
    )
    parser.add_argument(
        "--parse-log",
        type=Path,
        default=None,
        help="Optional path to a saved FFmpeg ebur128 stderr output text file (for offline/unit testing).",
    )
    parser.add_argument(
        "--target-lufs",
        type=float,
        default=-14.0,
        help="Target integrated loudness in LUFS (default: -14.0).",
    )
    parser.add_argument(
        "--tolerance-lu",
        type=float,
        default=1.0,
        help="Allowed deviation from target LUFS in LU (default: 1.0).",
    )
    parser.add_argument(
        "--max-true-peak",
        type=float,
        default=-1.0,
        help="Maximum allowed True Peak in dBTP (default: -1.0).",
    )
    return parser.parse_args(argv)


def extract_ebur128_metrics(log_text: str) -> tuple[float | None, float | None]:
    integrated_matches = re.findall(r"I:\s*(-?\d+(?:\.\d+)?)\s*LUFS", log_text)
    tp_matches = re.findall(r"Peak:\s*(-?\d+(?:\.\d+)?)\s*dBFS", log_text)

    i_lufs = float(integrated_matches[-1]) if integrated_matches else None
    tp_db = float(tp_matches[-1]) if tp_matches else None
    return i_lufs, tp_db


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.input is None and args.parse_log is None:
        print("[ERROR] Provide either --input <media_file> or --parse-log <log_file>.", file=sys.stderr)
        return 2

    if args.parse_log is not None:
        if not args.parse_log.is_file():
            print(f"[ERROR] Log file not found: {args.parse_log}", file=sys.stderr)
            return 1
        raw_log = args.parse_log.read_text(encoding="utf-8")
    else:
        media_path = args.input.resolve()
        if not media_path.is_file():
            print(f"[ERROR] Media file not found: {media_path}", file=sys.stderr)
            return 1
        if shutil.which("ffmpeg") is None:
            print("[ERROR] 'ffmpeg' binary not found in PATH.", file=sys.stderr)
            return 1
        cmd = [
            "ffmpeg",
            "-nostats",
            "-i",
            str(media_path),
            "-filter_complex",
            "ebur128=peak=true",
            "-f",
            "null",
            "-",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        raw_log = proc.stderr

    i_lufs, tp_db = extract_ebur128_metrics(raw_log)
    if i_lufs is None or tp_db is None:
        print("[ERROR] Could not parse Integrated Loudness (I:) or True Peak (Peak:) from ebur128 output.", file=sys.stderr)
        return 1

    min_lufs = args.target_lufs - args.tolerance_lu
    max_lufs = args.target_lufs + args.tolerance_lu

    errors: list[str] = []
    if not (min_lufs <= i_lufs <= max_lufs):
        errors.append(
            f"Integrated Loudness {i_lufs:.1f} LUFS is outside target window [{min_lufs:.1f}, {max_lufs:.1f}] LUFS."
        )
    if tp_db > args.max_true_peak:
        errors.append(
            f"True Peak {tp_db:.1f} dBTP exceeds ceiling {args.max_true_peak:.1f} dBTP."
        )

    print("=== EBU R128 Audio Loudness Audit ===")
    print(f"Integrated Loudness : {i_lufs:.1f} LUFS (target: {args.target_lufs:.1f} +- {args.tolerance_lu:.1f} LU)")
    print(f"Max True Peak       : {tp_db:.1f} dBTP (ceiling: <= {args.max_true_peak:.1f} dBTP)")

    if errors:
        for err in errors:
            print(f"  [FAIL] {err}", file=sys.stderr)
        return 1

    print("[OK] Audio loudness and true peak comply with trailer delivery standard.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
