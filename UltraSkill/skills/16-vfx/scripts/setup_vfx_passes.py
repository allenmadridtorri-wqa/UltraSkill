#!/usr/bin/env python3
"""
Multi-Layer EXR Render Pass & Cryptomatte Configurator (`setup_vfx_passes.py`).

Configures the active ViewLayer in a Blender Cycles scene for VFX compositing:
  1. Enables Diffuse, Glossy, Transmission, and Volume (Direct/Indirect/Color) passes.
  2. Enables Emission, Environment, Z-Depth, Mist, Normal, and Vector (if Motion Blur is off) passes.
  3. Enables Cryptomatte (Object, Material, Asset) at 6 levels with Accurate mode.
  4. Sets output format to `OPEN_EXR_MULTILAYER` with `DWAA` or `ZIP` compression (`16-bit Half Float`).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def extract_script_args(argv: list[str]) -> list[str]:
    if "--" in argv:
        return argv[argv.index("--") + 1 :]
    return argv[1:]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    raw_args = extract_script_args(sys.argv if argv is None else ["setup_vfx_passes.py", *argv])
    parser = argparse.ArgumentParser(
        prog="setup_vfx_passes.py",
        description="Enable Multi-Layer EXR AOV passes, Cryptomatte, and Mist depth in a Blender Cycles scene.",
    )
    parser.add_argument(
        "--codec",
        choices=["DWAA", "ZIP", "PIZ"],
        default="DWAA",
        help="OpenEXR compression codec (default: DWAA starting value).",
    )
    parser.add_argument(
        "--mist-start",
        type=float,
        default=1.0,
        help="Mist pass near start distance in meters (default: 1.0 m).",
    )
    parser.add_argument(
        "--mist-depth",
        type=float,
        default=35.0,
        help="Mist pass falloff depth in meters (default: 35.0 m).",
    )
    parser.add_argument(
        "--save",
        type=Path,
        default=None,
        help="Optional path to save the updated .blend file.",
    )
    return parser.parse_args(raw_args)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        import bpy  # type: ignore
    except ImportError:
        print(
            "[ERROR] 'bpy' not available. Run inside headless Blender:\n"
            "  blender -b scene.blend -P skills/16-vfx/scripts/setup_vfx_passes.py -- --codec ZIP",
            file=sys.stderr,
        )
        return 2

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    vl = bpy.context.view_layer

    # Beauty component decomposition passes
    vl.use_pass_combined = True
    vl.use_pass_z = True
    vl.use_pass_mist = True
    vl.use_pass_normal = True
    vl.use_pass_emit = True
    vl.use_pass_environment = True
    vl.use_pass_ambient_occlusion = True

    vl.use_pass_diffuse_direct = True
    vl.use_pass_diffuse_indirect = True
    vl.use_pass_diffuse_color = True

    vl.use_pass_glossy_direct = True
    vl.use_pass_glossy_indirect = True
    vl.use_pass_glossy_color = True

    vl.use_pass_transmission_direct = True
    vl.use_pass_transmission_indirect = True
    vl.use_pass_transmission_color = True

    if hasattr(vl, "cycles"):
        vl.cycles.use_pass_volume_direct = True
        vl.cycles.use_pass_volume_indirect = True
        vl.cycles.denoising_store_passes = True

    # Cryptomatte ID mattes
    vl.use_pass_cryptomatte_object = True
    vl.use_pass_cryptomatte_material = True
    vl.use_pass_cryptomatte_asset = True
    vl.pass_cryptomatte_depth = 6
    vl.use_pass_cryptomatte_accurate = True

    # Configure Mist distances on the World datablock
    if scene.world is not None:
        scene.world.mist_settings.start = args.mist_start
        scene.world.mist_settings.depth = args.mist_depth
        scene.world.mist_settings.falloff = "QUADRATIC"

    # Multi-Layer OpenEXR output configuration
    img_settings = scene.render.image_settings
    img_settings.file_format = "OPEN_EXR_MULTILAYER"
    img_settings.color_depth = "16"
    img_settings.exr_codec = args.codec

    if args.save:
        save_path = args.save.resolve()
        save_path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(save_path))
        print(f"[OK] Saved Multi-Layer EXR VFX passes ({args.codec}) to {save_path}")
    else:
        print(f"[OK] Configured Multi-Layer EXR VFX passes and Cryptomatte (codec={args.codec}).")

    return 0


if __name__ == "__main__":
    sys.exit(main())
