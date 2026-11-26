#!/usr/bin/env python3
"""
FFmpeg Sequence Assembler & Trailer Mastering Wrapper (`assemble_sequence.py`).

Validates that all numbered frames in `[--start, --end]` exist on disk, constructs
the exact FFmpeg command line for H.264 web delivery or ProRes 422 HQ archival
(with optional burned-in timecode/frame overlay for REVIEW workprints and EBU R128
`-14 LUFS` audio normalization), and executes or prints (`--dry-run`) the encode.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="assemble_sequence.py",
        description="Validate a rendered image sequence and encode a trailer master via FFmpeg.",
    )
    parser.add_argument(
        "--frames-dir",
        type=Path,
        required=True,
        help="Directory containing numbered frame files (e.g., frame_0001.png).",
    )
    parser.add_argument(
        "--prefix",
        default="frame_",
        help="Frame filename prefix before 4-digit frame number (default: 'frame_').",
    )
    parser.add_argument(
        "--ext",
        choices=["png", "exr"],
        default="png",
        help="Frame file extension without dot (default: 'png').",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Start frame number (default: 1).",
    )
    parser.add_argument(
        "--end",
        type=int,
        required=True,
        help="End frame number (inclusive).",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=24,
        help="Timeline frame rate (default: 24).",
    )
    parser.add_argument(
        "--audio",
        type=Path,
        default=None,
        help="Optional WAV/FLAC audio file to mux and normalize to -14 LUFS.",
    )
    parser.add_argument(
        "--profile",
        choices=["web_h264", "prores_hq", "review_tc"],
        default="web_h264",
        help="Encoding profile: web_h264 (default), prores_hq (.mov), or review_tc (burned frame numbers).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output video path (.mp4 or .mov).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate frame sequence and print the FFmpeg command without running it.",
    )
    return parser.parse_args(argv)


def verify_frame_continuity(frames_dir: Path, prefix: str, ext: str, start: int, end: int) -> list[int]:
    missing: list[int] = []
    for fno in range(start, end + 1):
        candidate = frames_dir / f"{prefix}{fno:04d}.{ext}"
        if not candidate.is_file() or candidate.stat().st_size == 0:
            missing.append(fno)
    return missing


def build_ffmpeg_command(args: argparse.Namespace) -> list[str]:
    input_pattern = str(args.frames_dir.resolve() / f"{args.prefix}%04d.{args.ext}")
    total_frames = args.end - args.start + 1

    cmd = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(args.fps),
        "-start_number",
        str(args.start),
        "-i",
        input_pattern,
    ]

    if args.audio is not None:
        cmd.extend(["-i", str(args.audio.resolve())])

    cmd.extend(["-frames:v", str(total_frames)])

    if args.profile == "prores_hq":
        cmd.extend(
            [
                "-c:v",
                "prores_ks",
                "-profile:v",
                "3",
                "-pix_fmt",
                "yuv422p10le",
                "-colorspace",
                "bt709",
            ]
        )
    elif args.profile == "review_tc":
        drawtext = (
            f"drawtext=text='FRAME %{{frame_num}}':start_number={args.start}:"
            "x=40:y=40:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.65"
        )
        cmd.extend(
            [
                "-vf",
                drawtext,
                "-c:v",
                "libx264",
                "-crf",
                "20",
                "-preset",
                "fast",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
            ]
        )
    else:
        cmd.extend(
            [
                "-c:v",
                "libx264",
                "-crf",
                "16",
                "-preset",
                "slow",
                "-profile:v",
                "high",
                "-pix_fmt",
                "yuv420p",
                "-colorspace",
                "bt709",
                "-color_primaries",
                "bt709",
                "-color_trc",
                "bt709",
                "-movflags",
                "+faststart",
            ]
        )

    if args.audio is not None:
        cmd.extend(["-af", "loudnorm=I=-14:TP=-1.0:LRA=11"])
        if args.profile == "prores_hq":
            cmd.extend(["-c:a", "pcm_s24le", "-ar", "48000"])
        else:
            cmd.extend(["-c:a", "aac", "-b:a", "320k", "-ar", "48000"])
        cmd.append("-shortest")

    cmd.append(str(args.output.resolve()))
    return cmd


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.end < args.start:
        print("[ERROR] --end must be >= --start.", file=sys.stderr)
        return 2

    frames_dir = args.frames_dir.resolve()
    if not frames_dir.is_dir():
        print(f"[ERROR] Frames directory not found: {frames_dir}", file=sys.stderr)
        return 1

    if args.audio is not None and not args.audio.is_file():
        print(f"[ERROR] Audio file not found: {args.audio}", file=sys.stderr)
        return 1

    missing = verify_frame_continuity(frames_dir, args.prefix, args.ext, args.start, args.end)
    if missing:
        print(
            f"[FAIL] Cannot assemble sequence: {len(missing)} missing/empty frames "
            f"(first missing: {missing[:10]}).",
            file=sys.stderr,
        )
        return 1

    cmd = build_ffmpeg_command(args)
    print(f"[INFO] Verified {args.end - args.start + 1} contiguous frames ({args.start}..{args.end}).")
    print(f"[CMD]  {' '.join(cmd)}")

    if args.dry_run:
        print("[OK] Dry-run validation complete.")
        return 0

    if shutil.which("ffmpeg") is None:
        print("[ERROR] 'ffmpeg' binary not found in PATH.", file=sys.stderr)
        return 1

    args.output.resolve().parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(cmd, check=False)
    if proc.returncode != 0:
        print(f"[FAIL] FFmpeg exited with code {proc.returncode}.", file=sys.stderr)
        return proc.returncode

    print(f"[OK] Encoded trailer master -> {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
