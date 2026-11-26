#!/usr/bin/env python3
"""Generate the 20-shot, 1440-frame (60s @ 24fps) Colab OptiX render manifest for Example 02."""

import argparse
import json
import pathlib
import sys
from typing import Any, Dict, List


FPS = 24
TOTAL_FRAMES = 1440


def build_trailer_manifest() -> Dict[str, Any]:
    shot_specs = [
        # Act I: Establish (432 frames across 4 shots)
        ("SH010", 1, 120, 24.0, 5.6, "Wide canyon mist establish"),
        ("SH020", 121, 228, 35.0, 4.0, "Expedition rover tracks in wet basalt"),
        ("SH030", 229, 336, 50.0, 2.8, "Protagonist visor reflection of monolith"),
        ("SH040", 337, 432, 35.0, 4.0, "Monolith seam begins pulsing amber"),
        # Act II: Escalation (576 frames across 8 shots)
        ("SH050", 433, 516, 50.0, 2.8, "Low-angle dolly push toward monolith base"),
        ("SH060", 517, 588, 85.0, 2.0, "Macro dust pebbles levitating off ground"),
        ("SH070", 589, 660, 35.0, 2.8, "Energy ring expands through volumetric fog"),
        ("SH080", 661, 732, 50.0, 2.8, "Protagonist reaches for resonance beacon"),
        ("SH090", 733, 804, 85.0, 2.0, "Extreme close-up on iris dilation"),
        ("SH100", 805, 876, 24.0, 4.0, "Sky clouds part around vertical light beam"),
        ("SH110", 877, 948, 50.0, 2.8, "Shockwave scatters basalt debris toward lens"),
        ("SH120", 949, 1008, 85.0, 2.0, "Hand gripped on cliff edge as gravity shifts"),
        # Act III: Climax Montage & Title Card (432 frames across 8 shots)
        ("SH130", 1009, 1044, 35.0, 2.8, "Rapid cut 1: Monolith plates separate"),
        ("SH140", 1045, 1080, 50.0, 2.8, "Rapid cut 2: Beacon arc discharge"),
        ("SH150", 1081, 1116, 85.0, 2.0, "Rapid cut 3: Visor shatters in slow motion"),
        ("SH160", 1117, 1152, 24.0, 4.0, "Rapid cut 4: Orbital view of canyon pulse"),
        ("SH170", 1153, 1200, 50.0, 2.8, "Hero silhouette stepping into core portal"),
        ("SH180", 1201, 1260, 85.0, 2.0, "Whiteout flash into 1.5s audio vacuum cut"),
        ("SH190", 1261, 1380, 50.0, 4.0, "Title Card: OBELISK - AWAKENING (metallic reveal)"),
        ("SH200", 1381, 1440, 85.0, 2.8, "Post-title stinger: single glowing glyph in dark"),
    ]

    shots: List[Dict[str, Any]] = []
    for shot_id, f_start, f_end, lens_mm, f_stop, desc in shot_specs:
        shots.append({
            "shot_id": shot_id,
            "start_frame": f_start,
            "end_frame": f_end,
            "duration_frames": f_end - f_start + 1,
            "focal_length_mm": lens_mm,
            "f_stop": f_stop,
            "description": desc,
            "output_pattern": f"renders/{shot_id}/frame_####.exr",
            "estimated_vram_mb": 3400,
        })

    return {
        "project": "obelisk_awakening_60s_trailer",
        "fps": FPS,
        "total_frames": TOTAL_FRAMES,
        "duration_seconds": TOTAL_FRAMES / FPS,
        "render_engine": "CYCLES",
        "compute_device": "OPTIX",
        "preset": "PROD_1080P",
        "resolution": [1920, 1080],
        "samples": 192,
        "view_transform": "AgX",
        "shots": shots,
    }


def validate_manifest(manifest: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    shots = manifest.get("shots", [])
    if not shots:
        return ["Manifest contains no shots."]

    expected_next = 1
    for s in shots:
        if s["start_frame"] != expected_next:
            errors.append(
                f"Frame gap/overlap at {s['shot_id']}: expected start_frame={expected_next}, got {s['start_frame']}"
            )
        if s["end_frame"] < s["start_frame"]:
            errors.append(f"Invalid frame range in {s['shot_id']}")
        if s["estimated_vram_mb"] > 12500:
            errors.append(f"Shot {s['shot_id']} exceeds Colab T4 12,500 MB safe VRAM budget")
        expected_next = s["end_frame"] + 1

    if expected_next - 1 != TOTAL_FRAMES:
        errors.append(f"Total frames {expected_next - 1} does not equal 1440 (60s @ 24fps).")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=pathlib.Path, help="Output JSON manifest path")
    parser.add_argument("--self-test", action="store_true", help="Run built-in 1440-frame trailer manifest test")
    args = parser.parse_args()

    manifest = build_trailer_manifest()
    errs = validate_manifest(manifest)
    if errs:
        for e in errs:
            print(f"[ERROR] {e}", file=sys.stderr)
        return 1

    if args.output:
        args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    if args.self_test:
        print(
            f"Self-test PASSED: {len(manifest['shots'])} shots verified across contiguous frames 1..{TOTAL_FRAMES}."
        )
        return 0

    if not args.output:
        print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
