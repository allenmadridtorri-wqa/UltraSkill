#!/usr/bin/env python3
"""
Verify Rendered Frame Sequences Against `render_manifest.json` (`verify_frames.py`).

Checks every expected frame in `[start_frame, end_frame]` (step `frame_step`):
  1. Exists in the manifest with status == 'COMPLETED'.
  2. Exists on disk in `output_dir`.
  3. Has byte size >= 128 bytes and matches manifest byte count.
  4. Matches PNG (`89 50 4E 47`) or OpenEXR (`76 2F 31 01`) magic header bytes.
  5. Optionally verifies full SHA-256 checksums (`--verify-sha256`).
Outputs a clear list of missing or corrupt frame numbers so `render_sequence.py`
can re-render only the defective frames.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
EXR_MAGIC = b"\x76\x2f\x31\x01"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="verify_frames.py",
        description="Audit rendered frames on Google Drive against render_manifest.json.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
        help="Path to render_manifest.json.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional override for the rendered frames directory (defaults to output_dir in manifest).",
    )
    parser.add_argument(
        "--verify-sha256",
        action="store_true",
        help="Recompute SHA-256 hash of every frame file to detect silent bit-rot or partial Drive sync.",
    )
    return parser.parse_args(argv)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while chunk := fh.read(65536):
            digest.update(chunk)
    return digest.hexdigest()


def check_header_magic(path: Path) -> bool:
    try:
        with path.open("rb") as fh:
            header = fh.read(8)
    except OSError:
        return False

    if path.suffix.lower() == ".png":
        return header == PNG_MAGIC
    if path.suffix.lower() == ".exr":
        return header[:4] == EXR_MAGIC
    return len(header) >= 4


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    manifest_path: Path = args.manifest.resolve()

    if not manifest_path.is_file():
        print(f"[ERROR] Manifest not found: {manifest_path}", file=sys.stderr)
        return 1

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[ERROR] Invalid JSON in manifest {manifest_path}: {exc}", file=sys.stderr)
        return 1

    start_frame = int(manifest.get("start_frame", 1))
    end_frame = int(manifest.get("end_frame", 1))
    step = int(manifest.get("frame_step", 1))
    frames_map: dict = manifest.get("frames", {})

    output_dir = (
        args.output_dir.resolve()
        if args.output_dir is not None
        else Path(manifest.get("output_dir", manifest_path.parent)).resolve()
    )

    missing_frames: list[int] = []
    corrupt_frames: list[str] = []
    verified_count = 0

    expected_range = list(range(start_frame, end_frame + 1, step))
    for frame_no in expected_range:
        key = str(frame_no)
        rec = frames_map.get(key)
        if not rec or rec.get("status") != "COMPLETED":
            missing_frames.append(frame_no)
            continue

        filename = rec.get("file", f"frame_{frame_no:04d}.png")
        fpath = output_dir / filename
        if not fpath.is_file():
            missing_frames.append(frame_no)
            continue

        actual_size = fpath.stat().st_size
        expected_size = rec.get("bytes", 0)
        if actual_size < 128 or (expected_size and actual_size != expected_size):
            corrupt_frames.append(f"Frame {frame_no:04d} ({filename}): size {actual_size} != expected {expected_size}")
            continue

        if not check_header_magic(fpath):
            corrupt_frames.append(f"Frame {frame_no:04d} ({filename}): invalid magic header bytes")
            continue

        if args.verify_sha256 and rec.get("sha256"):
            actual_sha = sha256_file(fpath)
            if actual_sha != rec["sha256"]:
                corrupt_frames.append(f"Frame {frame_no:04d} ({filename}): SHA-256 mismatch")
                continue

        verified_count += 1

    print(
        f"=== Frame Sequence Verification ({start_frame}..{end_frame}, step {step}) ===\n"
        f"Expected Frames : {len(expected_range)}\n"
        f"Verified Clean  : {verified_count}\n"
        f"Missing Frames  : {len(missing_frames)}\n"
        f"Corrupt Frames  : {len(corrupt_frames)}"
    )

    if missing_frames or corrupt_frames:
        if missing_frames:
            print(f"[FAIL] Missing frame numbers: {missing_frames}", file=sys.stderr)
        for item in corrupt_frames:
            print(f"[FAIL] Corrupt frame: {item}", file=sys.stderr)
        return 1

    print("[OK] All frames verified intact on disk.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
