#!/usr/bin/env python3
"""
Standardized Film-Finish Blender Compositor Graph Builder (`build_compositor_tree.py`).

Constructs the restrained post-processing compositor pipeline required by
Section 4 Render Standard and `12-materials-lighting/references/film-finish-compositing.md`:
  1. Render Layers -> Denoise (Albedo + Normal accurate prefilter)
  2. Physical Glare / Bloom (`FOG_GLOW`, high threshold `>= 1.8` so only specular peaks bloom)
  3. Subtle Optical Lens Distortion & Dispersion (`Distort = -0.008`, `Dispersion = 0.003`)
  4. ASC-CDL Color Balance (`Offset / Power / Slope`)
  5. Composite Output
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
    raw_args = extract_script_args(sys.argv if argv is None else ["build_compositor_tree.py", *argv])
    parser = argparse.ArgumentParser(
        prog="build_compositor_tree.py",
        description="Build the standardized physical glare, lens dispersion, and color grade compositor tree in Blender.",
    )
    parser.add_argument(
        "--glare-threshold",
        type=float,
        default=1.8,
        help="Luminance threshold for fog-glow bloom (default: 1.8 starting value).",
    )
    parser.add_argument(
        "--distortion",
        type=float,
        default=-0.008,
        help="Subtle optical barrel distortion factor (default: -0.008 starting value).",
    )
    parser.add_argument(
        "--dispersion",
        type=float,
        default=0.003,
        help="Lateral chromatic dispersion factor (default: 0.003, cap <= 0.008).",
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
    if args.dispersion > 0.012:
        print(
            f"[ERROR] --dispersion {args.dispersion} exceeds realism restraint limit (max 0.012).",
            file=sys.stderr,
        )
        return 2

    try:
        import bpy  # type: ignore
    except ImportError:
        print(
            "[ERROR] 'bpy' not available. Run inside headless Blender:\n"
            "  blender -b scene.blend -P skills/16-vfx/scripts/build_compositor_tree.py",
            file=sys.stderr,
        )
        return 2

    scene = bpy.context.scene
    scene.use_nodes = True
    tree = scene.node_tree
    nodes = tree.nodes
    links = tree.links
    nodes.clear()

    rl_node = nodes.new(type="CompositorNodeRLayers")
    rl_node.location = (-600, 0)

    denoise_node = nodes.new(type="CompositorNodeDenoise")
    denoise_node.location = (-350, 0)
    if hasattr(denoise_node, "prefilter"):
        denoise_node.prefilter = "ACCURATE"

    glare_node = nodes.new(type="CompositorNodeGlare")
    glare_node.location = (-100, 0)
    glare_node.glare_type = "FOG_GLOW"
    glare_node.quality = "HIGH"
    glare_node.threshold = args.glare_threshold
    glare_node.size = 7
    glare_node.mix = -0.75

    grade_node = nodes.new(type="CompositorNodeColorBalance")
    grade_node.location = (150, 0)
    grade_node.correction_method = "OFFSET_POWER_SLOPE"
    grade_node.offset = (0.0, 0.0, 0.0015)
    grade_node.power = (1.0, 1.0, 1.0)
    grade_node.slope = (1.01, 1.0, 0.99)

    lens_node = nodes.new(type="CompositorNodeLensdist")
    lens_node.location = (420, 0)
    lens_node.use_fit = True
    lens_node.inputs["Distort"].default_value = args.distortion
    lens_node.inputs["Dispersion"].default_value = args.dispersion

    comp_node = nodes.new(type="CompositorNodeComposite")
    comp_node.location = (680, 0)

    links.new(rl_node.outputs["Image"], denoise_node.inputs["Image"])
    if "Denoising Normal" in rl_node.outputs:
        links.new(rl_node.outputs["Denoising Normal"], denoise_node.inputs["Normal"])
    if "Denoising Albedo" in rl_node.outputs:
        links.new(rl_node.outputs["Denoising Albedo"], denoise_node.inputs["Albedo"])

    links.new(denoise_node.outputs["Image"], glare_node.inputs["Image"])
    links.new(glare_node.outputs["Image"], grade_node.inputs["Image"])
    links.new(grade_node.outputs["Image"], lens_node.inputs["Image"])
    links.new(lens_node.outputs["Image"], comp_node.inputs["Image"])

    if args.save:
        save_path = args.save.resolve()
        save_path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(save_path))
        print(f"[OK] Saved film-finish compositor graph to {save_path}")
    else:
        print(
            f"[OK] Built film-finish compositor graph (glare_threshold={args.glare_threshold}, "
            f"distort={args.distortion}, dispersion={args.dispersion})."
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
