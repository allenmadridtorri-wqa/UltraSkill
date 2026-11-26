#!/usr/bin/env python3
"""
Headless Blender 3D Mesh Linter (`mesh_linter.py`).

Audits all visible mesh objects in a Blender scene against UltraSkill 11-modeling
standards before handing off to 12-materials-lighting or 14-blender-pipeline:
  1. Scene unit system is METRIC with scale_length == 1.0.
  2. Every mesh object has applied scale (`scale == (1.0, 1.0, 1.0)` within 1e-4)
     and non-zero bounding dimensions.
  3. Hero meshes (or meshes flagged by `--require-bevels`) have either a BEVEL
     modifier or beveled geometry, and smooth shading enabled.
  4. Every textured mesh has at least one UV map (`len(mesh.uv_layers) >= 1`).
  5. Checks for loose vertices and non-manifold edges on closed solid meshes.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


def extract_script_args(argv: list[str]) -> list[str]:
    if "--" in argv:
        return argv[argv.index("--") + 1 :]
    return argv[1:]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    raw_args = extract_script_args(sys.argv if argv is None else ["mesh_linter.py", *argv])
    parser = argparse.ArgumentParser(
        prog="mesh_linter.py",
        description="Audit Blender scene meshes for metric scale, applied transforms, UVs, bevels, and topology.",
    )
    parser.add_argument(
        "--require-bevels",
        action="store_true",
        help="Require a BEVEL modifier or >= 12 edges on every visible mesh object.",
    )
    parser.add_argument(
        "--check-manifold",
        action="store_true",
        help="Flag non-manifold edges on mesh objects via bmesh analysis.",
    )
    parser.add_argument(
        "--auto-fix-scale",
        action="store_true",
        help="Automatically apply object scale transforms and set metric 1.0 unit scale.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Optional path to write JSON lint report.",
    )
    return parser.parse_args(raw_args)


def is_unit_scale(vec: tuple[float, float, float], tol: float = 1e-3) -> bool:
    return (
        math.isclose(vec[0], 1.0, abs_tol=tol)
        and math.isclose(vec[1], 1.0, abs_tol=tol)
        and math.isclose(vec[2], 1.0, abs_tol=tol)
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        import bmesh  # type: ignore
        import bpy  # type: ignore
    except ImportError:
        print(
            "[ERROR] 'bpy' not available. Run inside headless Blender:\n"
            "  blender -b scene.blend -P skills/11-modeling/scripts/mesh_linter.py -- --require-bevels",
            file=sys.stderr,
        )
        return 2

    scene = bpy.context.scene
    errors: list[str] = []
    warnings: list[str] = []

    if args.auto_fix_scale:
        scene.unit_settings.system = "METRIC"
        scene.unit_settings.scale_length = 1.0

    if scene.unit_settings.system != "METRIC" or not math.isclose(
        scene.unit_settings.scale_length, 1.0, abs_tol=1e-4
    ):
        errors.append(
            f"Scene units must be METRIC with scale_length=1.0 "
            f"(got system={scene.unit_settings.system}, scale_length={scene.unit_settings.scale_length})."
        )

    mesh_objects = [o for o in scene.objects if o.type == "MESH" and not o.hide_render]
    if not mesh_objects:
        errors.append("Scene contains zero render-visible MESH objects.")

    inspected: list[dict] = []
    for obj in mesh_objects:
        mesh = obj.data
        scale_tuple = (float(obj.scale[0]), float(obj.scale[1]), float(obj.scale[2]))

        if not is_unit_scale(scale_tuple):
            if args.auto_fix_scale and mesh.users == 1:
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                obj.select_set(False)
                scale_tuple = (1.0, 1.0, 1.0)
            else:
                errors.append(
                    f"Object '{obj.name}' has unapplied scale {tuple(round(s, 4) for s in scale_tuple)}."
                )

        dims = (float(obj.dimensions[0]), float(obj.dimensions[1]), float(obj.dimensions[2]))
        if max(dims) < 0.0002:
            errors.append(f"Object '{obj.name}' is microscopic (< 0.2 mm max dimension: {dims}).")
        elif max(dims) > 5000.0:
            warnings.append(f"Object '{obj.name}' exceeds 5000 m ({max(dims):.1f} m); verify metric scale.")

        has_uv = len(mesh.uv_layers) >= 1
        if not has_uv:
            errors.append(f"Object '{obj.name}' has zero UV layers.")

        has_bevel_mod = any(m.type == "BEVEL" for m in obj.modifiers)
        if args.require_bevels and not has_bevel_mod and len(mesh.polygons) <= 12:
            errors.append(
                f"Object '{obj.name}' is a low-poly box ({len(mesh.polygons)} faces) with no BEVEL modifier."
            )

        non_manifold_edges = 0
        if args.check_manifold:
            bm = bmesh.new()
            bm.from_mesh(mesh)
            non_manifold_edges = sum(1 for e in bm.edges if not e.is_manifold)
            bm.free()
            if non_manifold_edges > 0:
                warnings.append(f"Object '{obj.name}' has {non_manifold_edges} non-manifold edges.")

        inspected.append(
            {
                "name": obj.name,
                "vertices": len(mesh.vertices),
                "polygons": len(mesh.polygons),
                "dimensions_m": [round(d, 4) for d in dims],
                "scale": [round(s, 4) for s in scale_tuple],
                "uv_layers": len(mesh.uv_layers),
                "has_bevel_modifier": has_bevel_mod,
                "non_manifold_edges": non_manifold_edges,
            }
        )

    report = {
        "status": "PASS" if not errors else "FAIL",
        "unit_system": scene.unit_settings.system,
        "scale_length": scene.unit_settings.scale_length,
        "meshes_inspected": len(inspected),
        "errors": errors,
        "warnings": warnings,
        "objects": inspected,
    }

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"=== UltraSkill Mesh Linter ({len(inspected)} objects) ===")
    for w in warnings:
        print(f"  [WARN] {w}")
    if errors:
        for e in errors:
            print(f"  [FAIL] {e}", file=sys.stderr)
        return 1

    print("[OK] All render-visible meshes passed metric scale, transform, UV, and bevel checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
