#!/usr/bin/env python3
"""
Apply UltraSkill Cycles OptiX Quality Presets (`PREVIEW`, `REVIEW`, `FINAL`).

Usage inside headless Blender:
  blender -b scene.blend -P skills/14-blender-pipeline/scripts/apply_preset.py -- --preset REVIEW --save scene_review.blend

Usage for standalone CLI help or preset table inspection:
  python3 skills/14-blender-pipeline/scripts/apply_preset.py --help
  python3 skills/14-blender-pipeline/scripts/apply_preset.py --preset FINAL --print-only

All numerical sample counts, noise thresholds, and light path limits are
documented as starting values to be verified against a high-sample reference crop.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


# Starting values per Section 4 Render Standard
PRESET_CONFIGS: dict[str, dict[str, Any]] = {
    "PREVIEW": {
        "purpose": "Layout, camera blocking, and primary lighting ratio checks",
        "resolution_x": 960,
        "resolution_y": 540,
        "samples": 64,
        "min_samples": 16,
        "adaptive_threshold": 0.050,
        "max_bounces": 4,
        "diffuse_bounces": 2,
        "glossy_bounces": 2,
        "transmission_bounces": 4,
        "volume_bounces": 0,
        "transparent_max_bounces": 4,
        "caustics_reflective": False,
        "caustics_refractive": False,
        "use_denoising": True,
        "denoiser": "OPTIX",
        "denoising_input_passes": "RGB_ALBEDO_NORMAL",
        "use_motion_blur": False,
        "shutter": 0.5,
        "file_format": "PNG",
        "color_depth": "8",
        "view_transform": "AgX",
    },
    "REVIEW": {
        "purpose": "Look approval, Fake-3D checklist audit, and motion flicker strip tests",
        "resolution_x": 1920,
        "resolution_y": 1080,
        "samples": 256,
        "min_samples": 64,
        "adaptive_threshold": 0.015,
        "max_bounces": 8,
        "diffuse_bounces": 3,
        "glossy_bounces": 4,
        "transmission_bounces": 8,
        "volume_bounces": 2,
        "transparent_max_bounces": 8,
        "caustics_reflective": False,
        "caustics_refractive": True,
        "use_denoising": True,
        "denoiser": "OPTIX",
        "denoising_input_passes": "RGB_ALBEDO_NORMAL",
        "use_motion_blur": True,
        "shutter": 0.5,
        "file_format": "PNG",
        "color_depth": "16",
        "view_transform": "AgX",
    },
    "FINAL": {
        "purpose": "Final delivery master (1080p default; 4K 3840x2160 only if 3-frame benchmark <= 3h)",
        "resolution_x": 1920,
        "resolution_y": 1080,
        "samples": 1024,
        "min_samples": 128,
        "adaptive_threshold": 0.005,
        "max_bounces": 12,
        "diffuse_bounces": 4,
        "glossy_bounces": 6,
        "transmission_bounces": 12,
        "volume_bounces": 4,
        "transparent_max_bounces": 16,
        "caustics_reflective": True,
        "caustics_refractive": True,
        "use_denoising": True,
        "denoiser": "OPENIMAGEDENOISE",
        "denoising_input_passes": "RGB_ALBEDO_NORMAL",
        "use_motion_blur": True,
        "shutter": 0.5,
        "file_format": "OPEN_EXR_MULTILAYER",
        "exr_codec": "DWAA",
        "color_depth": "16",
        "view_transform": "AgX",
    },
}


def extract_script_args(argv: list[str]) -> list[str]:
    if "--" in argv:
        return argv[argv.index("--") + 1 :]
    return argv[1:]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    raw_args = extract_script_args(sys.argv if argv is None else ["apply_preset.py", *argv])
    parser = argparse.ArgumentParser(
        prog="apply_preset.py",
        description="Apply PREVIEW, REVIEW, or FINAL Cycles OptiX render preset to a Blender scene.",
    )
    parser.add_argument(
        "--preset",
        choices=["PREVIEW", "REVIEW", "FINAL"],
        required=True,
        help="Quality preset to apply.",
    )
    parser.add_argument(
        "--uhd-4k",
        action="store_true",
        help="For FINAL preset only: use 3840x2160 instead of 1920x1080 (requires benchmark proof <= 3 hours).",
    )
    parser.add_argument(
        "--png-16",
        action="store_true",
        help="Use 16-bit PNG output instead of Multi-Layer EXR on FINAL preset.",
    )
    parser.add_argument(
        "--crop-ref",
        action="store_true",
        help=(
            "Configure a small 20% center border crop at 2048 samples with denoiser OFF "
            "to compare against denoised output."
        ),
    )
    parser.add_argument(
        "--save",
        type=Path,
        default=None,
        help="Optional path to save the updated .blend file.",
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Print the starting values for the chosen preset as JSON and exit without launching Blender.",
    )
    return parser.parse_args(raw_args)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    cfg = dict(PRESET_CONFIGS[args.preset])

    if args.uhd_4k:
        if args.preset != "FINAL":
            print("[ERROR] --uhd-4k is only permitted with --preset FINAL.", file=sys.stderr)
            return 2
        cfg["resolution_x"] = 3840
        cfg["resolution_y"] = 2160

    if args.png_16:
        cfg["file_format"] = "PNG"
        cfg["color_depth"] = "16"

    if args.crop_ref:
        cfg["samples"] = 2048
        cfg["min_samples"] = 512
        cfg["adaptive_threshold"] = 0.002
        cfg["use_denoising"] = False
        cfg["border_crop"] = [0.4, 0.6, 0.4, 0.6]

    if args.print_only:
        print(json.dumps({"preset": args.preset, "starting_values": cfg}, indent=2))
        return 0

    try:
        import bpy  # type: ignore
    except ImportError:
        print(
            "[ERROR] 'bpy' not available. Pass --print-only outside Blender or run via `blender -b -P`.",
            file=sys.stderr,
        )
        return 2

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "GPU"

    scene.render.resolution_x = cfg["resolution_x"]
    scene.render.resolution_y = cfg["resolution_y"]
    scene.render.resolution_percentage = 100

    scene.cycles.samples = cfg["samples"]
    scene.cycles.adaptive_min_samples = cfg["min_samples"]
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = cfg["adaptive_threshold"]

    scene.cycles.max_bounces = cfg["max_bounces"]
    scene.cycles.diffuse_bounces = cfg["diffuse_bounces"]
    scene.cycles.glossy_bounces = cfg["glossy_bounces"]
    scene.cycles.transmission_bounces = cfg["transmission_bounces"]
    scene.cycles.volume_bounces = cfg["volume_bounces"]
    scene.cycles.transparent_max_bounces = cfg["transparent_max_bounces"]
    scene.cycles.caustics_reflective = cfg["caustics_reflective"]
    scene.cycles.caustics_refractive = cfg["caustics_refractive"]

    scene.cycles.use_denoising = cfg["use_denoising"]
    if cfg["use_denoising"]:
        try:
            scene.cycles.denoiser = cfg["denoiser"]
        except Exception:
            scene.cycles.denoiser = "OPENIMAGEDENOISE"
        scene.cycles.denoising_input_passes = cfg["denoising_input_passes"]

    scene.render.use_motion_blur = cfg["use_motion_blur"]
    scene.render.motion_blur_shutter = cfg["shutter"]

    # Color management: AgX standard
    try:
        scene.view_settings.view_transform = cfg["view_transform"]
    except Exception:
        print("[WARN] AgX not found in this Blender build; falling back to Filmic.", file=sys.stderr)
        scene.view_settings.view_transform = "Filmic"

    if args.crop_ref:
        scene.render.use_border = True
        scene.render.use_crop_to_border = True
        scene.render.border_min_x = 0.4
        scene.render.border_max_x = 0.6
        scene.render.border_min_y = 0.4
        scene.render.border_max_y = 0.6
    else:
        scene.render.use_border = False
        scene.render.use_crop_to_border = False

    scene.render.image_settings.file_format = cfg["file_format"]
    scene.render.image_settings.color_depth = cfg["color_depth"]
    if cfg["file_format"] == "OPEN_EXR_MULTILAYER" and "exr_codec" in cfg:
        scene.render.image_settings.exr_codec = cfg["exr_codec"]

    if args.save:
        save_path = args.save.resolve()
        save_path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(save_path))
        print(f"[OK] Saved preset '{args.preset}' to {save_path}")
    else:
        print(f"[OK] Applied preset '{args.preset}' in active Blender session.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
