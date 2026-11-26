#!/usr/bin/env python3
"""
Calibrated 3-Point Physical Studio Lighting & AgX Builder (`setup_studio_lighting.py`).

Constructs a physically motivated Cycles lighting setup around a target object or
origin point:
  1. Disables flat ambient world fill (`World Background Strength = 0.0`).
  2. Sets Color Management to `AgX` (`AgX - Medium High Contrast`).
  3. Builds a warm Key Area Light (`4800 K`), a cool Fill Area/Bounce Light (`6800 K`),
     and a crisp Rim/Kicker Strip Light (`5400 K`) scaled proportionally to `--radius`.
  4. Places a physical Camera with real sensor width (`36 mm`), focal length (`--lens-mm`),
     and Depth of Field focused on a target empty (`Studio_Focus_Target`).
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path


def extract_script_args(argv: list[str]) -> list[str]:
    if "--" in argv:
        return argv[argv.index("--") + 1 :]
    return argv[1:]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    raw_args = extract_script_args(sys.argv if argv is None else ["setup_studio_lighting.py", *argv])
    parser = argparse.ArgumentParser(
        prog="setup_studio_lighting.py",
        description="Build a calibrated 3-point physical Cycles lighting rig, AgX view transform, and physical DOF camera.",
    )
    parser.add_argument(
        "--radius",
        type=float,
        default=1.0,
        help="Characteristic radius of the subject in meters (default: 1.0 m starting value).",
    )
    parser.add_argument(
        "--key-ev",
        type=float,
        default=0.0,
        help="Exposure offset in stops (EV) for the key light (default: 0.0).",
    )
    parser.add_argument(
        "--ratio",
        type=float,
        default=4.0,
        help="Key-to-fill luminance ratio (default: 4.0 for 4:1 contrast starting value).",
    )
    parser.add_argument(
        "--lens-mm",
        type=float,
        default=85.0,
        help="Physical camera focal length in millimeters on a 36mm full-frame sensor (default: 85.0).",
    )
    parser.add_argument(
        "--fstop",
        type=float,
        default=4.0,
        help="Physical camera aperture f-stop for Depth of Field (default: 4.0).",
    )
    parser.add_argument(
        "--save",
        type=Path,
        default=None,
        help="Optional path to save the updated .blend file.",
    )
    return parser.parse_args(raw_args)


def kelvin_to_linear_rgb(kelvin: float) -> tuple[float, float, float]:
    """Approximate Planckian locus Blackbody Kelvin (1900K..10000K) to linear RGB."""
    temp = max(1000.0, min(40000.0, kelvin)) / 100.0
    if temp <= 66.0:
        r = 1.0
        g = max(0.0, min(1.0, (99.4708025861 * math.log(temp) - 161.1195681661) / 255.0))
        b = (
            0.0
            if temp <= 19.0
            else max(0.0, min(1.0, (138.5177312231 * math.log(temp - 10.0) - 305.0447927307) / 255.0))
        )
    else:
        r = max(0.0, min(1.0, (329.698727446 * ((temp - 60.0) ** -0.1332047592)) / 255.0))
        g = max(0.0, min(1.0, (288.1221695283 * ((temp - 60.0) ** -0.0755148492)) / 255.0))
        b = 1.0
    return (r**2.2, g**2.2, b**2.2)


def create_area_light(
    name: str,
    location: tuple[float, float, float],
    energy_watts: float,
    size_x: float,
    size_y: float,
    kelvin: float,
    spread_deg: float,
    target_obj,
):
    import bpy  # type: ignore

    light_data = bpy.data.lights.new(name=name, type="AREA")
    light_data.shape = "RECTANGLE"
    light_data.size = size_x
    light_data.size_y = size_y
    light_data.energy = energy_watts
    light_data.color = kelvin_to_linear_rgb(kelvin)
    light_data.spread = math.radians(spread_deg)

    light_obj = bpy.data.objects.new(name=name, object_data=light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location = location

    track = light_obj.constraints.new(type="TRACK_TO")
    track.target = target_obj
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"
    return light_obj


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.radius <= 0 or args.ratio < 1.0:
        print("[ERROR] --radius must be > 0 and --ratio must be >= 1.0.", file=sys.stderr)
        return 2

    try:
        import bpy  # type: ignore
    except ImportError:
        print(
            "[ERROR] 'bpy' not available. Run inside headless Blender:\n"
            "  blender -b -P skills/12-materials-lighting/scripts/setup_studio_lighting.py -- --radius 0.5",
            file=sys.stderr,
        )
        return 2

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0

    # Enforce AgX color management
    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        scene.view_settings.view_transform = "Filmic"

    # Zero out unmotivated flat ambient world fill
    if scene.world is None:
        scene.world = bpy.data.worlds.new("Studio_World_Dark")
    scene.world.use_nodes = True
    bg_node = scene.world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Strength"].default_value = 0.0

    r = args.radius
    focus_target = bpy.data.objects.get("Studio_Focus_Target")
    if focus_target is None:
        focus_target = bpy.data.objects.new("Studio_Focus_Target", None)
        bpy.context.collection.objects.link(focus_target)
        focus_target.location = (0.0, 0.0, r * 0.45)

    # Base key power scales with distance squared (inverse-square law)
    base_key_watts = 65.0 * (r**2) * (2.0**args.key_ev)
    fill_watts = base_key_watts / args.ratio
    rim_watts = base_key_watts * 0.55

    create_area_light(
        name="Studio_Key_Light",
        location=(r * 1.8, -r * 1.9, r * 2.1),
        energy_watts=base_key_watts,
        size_x=r * 1.2,
        size_y=r * 0.9,
        kelvin=4900.0,
        spread_deg=90.0,
        target_obj=focus_target,
    )
    create_area_light(
        name="Studio_Fill_Light",
        location=(-r * 2.4, -r * 1.6, r * 1.1),
        energy_watts=fill_watts,
        size_x=r * 2.0,
        size_y=r * 1.5,
        kelvin=6800.0,
        spread_deg=130.0,
        target_obj=focus_target,
    )
    create_area_light(
        name="Studio_Rim_Light",
        location=(-r * 1.2, r * 2.0, r * 2.2),
        energy_watts=rim_watts,
        size_x=r * 0.35,
        size_y=r * 1.4,
        kelvin=5500.0,
        spread_deg=65.0,
        target_obj=focus_target,
    )

    # Physical Camera setup
    cam_data = bpy.data.cameras.new("Studio_Physical_Camera")
    cam_data.sensor_fit = "HORIZONTAL"
    cam_data.sensor_width = 36.0
    cam_data.lens = args.lens_mm
    cam_data.dof.use_dof = True
    cam_data.dof.focus_object = focus_target
    cam_data.dof.aperture_fstop = args.fstop
    cam_data.dof.aperture_blades = 7

    cam_obj = bpy.data.objects.new("Studio_Physical_Camera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_dist = r * (args.lens_mm / 24.0)
    cam_obj.location = (0.0, -cam_dist, r * 0.75)

    cam_track = cam_obj.constraints.new(type="TRACK_TO")
    cam_track.target = focus_target
    cam_track.track_axis = "TRACK_NEGATIVE_Z"
    cam_track.up_axis = "UP_Y"
    scene.camera = cam_obj

    if args.save:
        save_path = args.save.resolve()
        save_path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(save_path))
        print(f"[OK] Saved studio lighting rig and AgX camera setup to {save_path}")
    else:
        print(
            f"[OK] Configured 3-point physical studio lighting (Key={base_key_watts:.1f}W, "
            f"Fill={fill_watts:.1f}W, Rim={rim_watts:.1f}W, {args.lens_mm}mm f/{args.fstop}, AgX)."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
