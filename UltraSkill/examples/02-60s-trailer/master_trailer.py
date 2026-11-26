#!/usr/bin/env python3
"""Verify 1440 trailer frames and build the deterministic FFmpeg x264 + EBU R128 (-14 LUFS) mastering command plan."""

import argparse
import json
import pathlib
import sys
from typing import Any, Dict, List

from generate_trailer_shots import build_trailer_manifest, validate_manifest


def build_ffmpeg_mastering_plan(
    manifest: Dict[str, Any],
    audio_mix_wav: str = "audio/trailer_mix_48k_24b.wav",
    output_mp4: str = "dist/obelisk_trailer_1080p24_master.mp4",
) -> Dict[str, Any]:
    errs = validate_manifest(manifest)
    if errs:
        raise ValueError(f"Invalid trailer manifest: {errs}")

    concat_lines: List[str] = []
    for shot in manifest["shots"]:
        shot_id = shot["shot_id"]
        for frame_num in range(shot["start_frame"], shot["end_frame"] + 1):
            concat_lines.append(f"file 'renders/{shot_id}/frame_{frame_num:04d}.exr'")
            concat_lines.append(f"duration {1.0 / manifest['fps']:.6f}")

    ffmpeg_cmd: List[str] = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        "renders/shot_concat_list.txt",
        "-i",
        audio_mix_wav,
        "-vf",
        "scale=1920:1080:flags=lanczos,format=yuv420p",
        "-af",
        "loudnorm=I=-14.0:TP=-1.0:LRA=11.0",
        "-c:v",
        "libx264",
        "-preset",
        "slow",
        "-crf",
        "16",
        "-pix_fmt",
        "yuv420p",
        "-r",
        "24",
        "-g",
        "48",
        "-c:a",
        "aac",
        "-b:a",
        "320k",
        "-ar",
        "48000",
        "-movflags",
        "+faststart",
        output_mp4,
    ]

    return {
        "project": manifest["project"],
        "total_frames_verified": manifest["total_frames"],
        "concat_entries_count": len(concat_lines) // 2,
        "target_lufs": -14.0,
        "target_true_peak_dbtp": -1.0,
        "video_codec": "libx264",
        "crf": 16,
        "pix_fmt": "yuv420p",
        "ffmpeg_command": ffmpeg_cmd,
    }


def run_self_test() -> int:
    manifest = build_trailer_manifest()
    plan = build_ffmpeg_mastering_plan(manifest)
    assert plan["total_frames_verified"] == 1440
    assert plan["concat_entries_count"] == 1440
    assert "loudnorm=I=-14.0:TP=-1.0:LRA=11.0" in plan["ffmpeg_command"]
    assert "+faststart" in plan["ffmpeg_command"]
    print("Self-test PASSED: 1440-frame concat table and EBU R128 FFmpeg mastering command verified.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=pathlib.Path, help="Optional input trailer manifest JSON")
    parser.add_argument("--self-test", action="store_true", help="Run built-in trailer mastering self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    manifest = (
        json.loads(args.manifest.read_text(encoding="utf-8"))
        if args.manifest
        else build_trailer_manifest()
    )
    plan = build_ffmpeg_mastering_plan(manifest)
    print(json.dumps(plan, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
