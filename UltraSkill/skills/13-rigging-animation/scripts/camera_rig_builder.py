#!/usr/bin/env python3
"""
Physical Dolly, Crane & Fluid-Head Camera Rig Builder (`camera_rig_builder.py`).

Constructs the 4-node physical cinema camera hierarchy defined in
`references/physical-camera-animation.md`:
  - `RIG_Dolly_Base` (track translation)
  - `RIG_Crane_Jib` (vertical elevation)
  - `RIG_Fluid_Head` (damped pan/tilt tracking `RIG_Aim_Target`)
  - `Camera_Body` (36mm full-frame sensor, physical lens, DOF focused on `RIG_Focus_Target`,
    plus optional procedural handheld breathing F-curve noise)
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
    raw_args = extract_script_args(sys.argv if argv is None else ["camera_rig_builder.py", *argv])
    parser = argparse.ArgumentParser(
        prog="camera_rig_builder.py",
        description="Build a 4-node physical cinema camera dolly/crane/fluid-head rig in Blender.",
    )
    parser.add_argument(
        "--name",
        default="HeroCam",
        help="Prefix for the camera rig hierarchy (default: 'HeroCam').",
    )
    parser.add_argument(
        "--lens-mm",
        type=float,
        default=50.0,
        help="Physical focal length in millimeters on a 36mm sensor (default: 50.0).",
    )
    parser.add_argument(
        "--fstop",
        type=float,
        default=2.8,
        help="Aperture f-stop for Depth of Field (default: 2.8).",
    )
    parser.add_argument(
        "--dolly-start",
        default="0.0,-3.5,0.0",
        help="Starting world (X,Y,Z) for the dolly base in meters (default: '0.0,-3.5,0.0').",
    )
    parser.add_argument(
        "--dolly-end",
        default="0.0,-2.6,0.0",
        help="Ending world (X,Y,Z) for the dolly base in meters (default: '0.0,-2.6,0.0').",
    )
    parser.add_argument(
        "--camera-height",
        type=float,
        default=1.15,
        help="Crane jib height above dolly base in meters (default: 1.15 m).",
    )
    parser.add_argument(
        "--handheld-strength",
        type=float,
        default=0.002,
        help="Rotation amplitude in radians for handheld breathing noise (default: 0.002 rad ~ 0.11 deg).",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=72,
        help="Duration of the eased dolly move in frames (default: 72 frames = 3.0s at 24fps).",
    )
    parser.add_argument(
        "--save",
        type=Path,
        default=None,
        help="Optional path to save the updated .blend file.",
    )
    return parser.parse_args(raw_args)


def parse_vec3(text: str) -> tuple[float, float, float]:
    parts = [float(x.strip()) for x in text.split(",")]
    if len(parts) != 3:
        raise ValueError(f"Expected 3 comma-separated floats, got '{text}'")
    return (parts[0], parts[1], parts[2])


def add_breathing_noise(obj, amplitude_rad: float) -> None:
    if amplitude_rad <= 0.0:
        return
    obj.rotation_mode = "XYZ"
    obj.keyframe_insert(data_path="rotation_euler", frame=1)
    if obj.animation_data and obj.animation_data.action:
        for idx, fcurve in enumerate(obj.animation_data.action.fcurves):
            if fcurve.data_path == "rotation_euler":
                mod = fcurve.modifiers.new(type="NOISE")
                mod.scale = 48.0 + (idx * 9.0)
                mod.strength = amplitude_rad if idx != 1 else amplitude_rad * 0.4
                mod.phase = float(idx * 17)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        start_pos = parse_vec3(args.dolly_start)
        end_pos = parse_vec3(args.dolly_end)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    try:
        import bpy  # type: ignore
    except ImportError:
        print(
            "[ERROR] 'bpy' not available. Run inside headless Blender:\n"
            "  blender -b -P skills/13-rigging-animation/scripts/camera_rig_builder.py -- --lens-mm 50",
            file=sys.stderr,
        )
        return 2

    scene = bpy.context.scene
    scene.render.fps = 24
    scene.render.use_motion_blur = True
    scene.render.motion_blur_shutter = 0.5

    prefix = args.name
    col = bpy.context.collection

    aim_target = bpy.data.objects.new(f"{prefix}_RIG_Aim_Target", None)
    aim_target.empty_display_type = "SPHERE"
    aim_target.empty_display_size = 0.15
    aim_target.location = (0.0, 0.0, args.camera_height * 0.9)
    col.objects.link(aim_target)

    focus_target = bpy.data.objects.new(f"{prefix}_RIG_Focus_Target", None)
    focus_target.empty_display_type = "CROSS"
    focus_target.empty_display_size = 0.12
    focus_target.location = (0.0, 0.0, args.camera_height * 0.9)
    col.objects.link(focus_target)

    dolly = bpy.data.objects.new(f"{prefix}_RIG_Dolly_Base", None)
    dolly.empty_display_type = "CUBE"
    dolly.empty_display_size = 0.25
    col.objects.link(dolly)

    crane = bpy.data.objects.new(f"{prefix}_RIG_Crane_Jib", None)
    crane.empty_display_type = "ARROWS"
    crane.empty_display_size = 0.20
    crane.parent = dolly
    crane.location = (0.0, 0.0, args.camera_height)
    col.objects.link(crane)

    fluid_head = bpy.data.objects.new(f"{prefix}_RIG_Fluid_Head", None)
    fluid_head.empty_display_type = "CIRCLE"
    fluid_head.empty_display_size = 0.15
    fluid_head.parent = crane
    fluid_head.location = (0.0, 0.0, 0.0)
    col.objects.link(fluid_head)

    track = fluid_head.constraints.new(type="TRACK_TO")
    track.target = aim_target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"
    track.influence = 0.92

    cam_data = bpy.data.cameras.new(f"{prefix}_Camera")
    cam_data.sensor_fit = "HORIZONTAL"
    cam_data.sensor_width = 36.0
    cam_data.lens = args.lens_mm
    cam_data.dof.use_dof = True
    cam_data.dof.focus_object = focus_target
    cam_data.dof.aperture_fstop = args.fstop
    cam_data.dof.aperture_blades = 7

    cam_obj = bpy.data.objects.new(f"{prefix}_Camera_Body", cam_data)
    cam_obj.parent = fluid_head
    cam_obj.location = (0.0, 0.0, 0.0)
    col.objects.link(cam_obj)
    scene.camera = cam_obj

    # Animate eased dolly push from frame 1 to args.frames
    dolly.location = start_pos
    dolly.keyframe_insert(data_path="location", frame=1)
    dolly.location = end_pos
    dolly.keyframe_insert(data_path="location", frame=max(2, args.frames))

    add_breathing_noise(cam_obj, args.handheld_strength)

    if args.save:
        save_path = args.save.resolve()
        save_path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(save_path))
        print(f"[OK] Saved physical camera rig '{prefix}' to {save_path}")
    else:
        print(f"[OK] Built physical camera rig '{prefix}' ({args.lens_mm}mm f/{args.fstop}, {args.frames}f dolly).")

    return 0


if __name__ == "__main__":
    sys.exit(main())
