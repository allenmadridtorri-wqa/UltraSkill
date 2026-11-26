#!/usr/bin/env python3
"""
Deterministic Keyframe Animation Baker (`bake_animation.py`).

Bakes visual transforms (constraints, IK chains, procedural F-curve noise modifiers,
and parent switches) on all armatures, cameras, or specified objects into explicit
per-frame keyframes and clears constraints so:
  1. Google Colab session resumes (`render_sequence.py`) render the exact same pose
     regardless of which frame a job restarts on.
  2. Exported `.glb` / `.gltf` files for Three.js or Godot play identical motion.
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
    raw_args = extract_script_args(sys.argv if argv is None else ["bake_animation.py", *argv])
    parser = argparse.ArgumentParser(
        prog="bake_animation.py",
        description="Bake constraints, IK, and procedural F-curve modifiers to explicit per-frame keyframes.",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=None,
        help="Start frame to bake (defaults to scene.frame_start).",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=None,
        help="End frame to bake (defaults to scene.frame_end).",
    )
    parser.add_argument(
        "--step",
        type=int,
        default=1,
        help="Frame step between baked keys (default: 1).",
    )
    parser.add_argument(
        "--clear-constraints",
        action="store_true",
        help="Remove constraints after baking visual transforms (recommended before glTF export).",
    )
    parser.add_argument(
        "--save",
        type=Path,
        default=None,
        help="Optional path to save the baked .blend file.",
    )
    return parser.parse_args(raw_args)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        import bpy  # type: ignore
    except ImportError:
        print(
            "[ERROR] 'bpy' not available. Run inside headless Blender:\n"
            "  blender -b scene.blend -P skills/13-rigging-animation/scripts/bake_animation.py -- --save baked.blend",
            file=sys.stderr,
        )
        return 2

    scene = bpy.context.scene
    start_frame = args.start if args.start is not None else scene.frame_start
    end_frame = args.end if args.end is not None else scene.frame_end

    if end_frame < start_frame:
        print(f"[ERROR] Invalid frame range: {start_frame}..{end_frame}", file=sys.stderr)
        return 2

    baked_objects: list[str] = []

    for obj in list(scene.objects):
        has_constraints = len(obj.constraints) > 0
        has_anim = obj.animation_data is not None
        is_armature = obj.type == "ARMATURE"
        is_camera = obj.type == "CAMERA"

        if not (has_constraints or has_anim or is_armature or is_camera):
            continue

        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        bake_types = {"OBJECT"}
        if is_armature:
            bake_types.add("POSE")

        bpy.ops.nla.bake(
            frame_start=start_frame,
            frame_end=end_frame,
            step=args.step,
            only_selected=False,
            visual_keying=True,
            clear_constraints=args.clear_constraints,
            clear_parents=False,
            use_current_action=True,
            bake_types=bake_types,
        )

        # Strip F-curve procedural modifiers now that values are baked per frame
        if obj.animation_data and obj.animation_data.action:
            for fc in obj.animation_data.action.fcurves:
                for mod in list(fc.modifiers):
                    fc.modifiers.remove(mod)

        baked_objects.append(obj.name)

    print(
        f"[OK] Baked {len(baked_objects)} objects ({start_frame}..{end_frame}, step={args.step}): "
        f"{', '.join(baked_objects)}"
    )

    if args.save:
        save_path = args.save.resolve()
        save_path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(save_path))
        print(f"[OK] Saved baked scene to {save_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
