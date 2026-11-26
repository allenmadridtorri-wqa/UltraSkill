#!/usr/bin/env python3
"""
Tesla T4 15 GB VRAM Scene Auditor (`vram_audit.py`).

Inspects a Blender scene headlessly before rendering on Google Colab to estimate
memory risks and flag:
  1. Uncompressed texture memory footprint and any textures exceeding `--max-texture-px`
     (default: 4096 px starting value).
  2. Duplicate mesh datablocks that share identical vertex/polygon counts and should
     be converted to linked instances (`Alt+D` / collection instances).
  3. Subdivision Surface modifiers with render levels > `--max-subdiv` (default: 2).
  4. Estimated total VRAM against the 12.5 GB safe ceiling on a 15 GB Tesla T4.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


T4_SAFE_CEILING_MB = 12800.0  # 12.5 GB starting value


def extract_script_args(argv: list[str]) -> list[str]:
    if "--" in argv:
        return argv[argv.index("--") + 1 :]
    return argv[1:]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    raw_args = extract_script_args(sys.argv if argv is None else ["vram_audit.py", *argv])
    parser = argparse.ArgumentParser(
        prog="vram_audit.py",
        description="Audit a Blender scene for texture sizes, un-instanced meshes, and subdivision spikes against T4 15 GB VRAM.",
    )
    parser.add_argument(
        "--max-texture-px",
        type=int,
        default=4096,
        help="Maximum allowed texture width or height in pixels (default: 4096 starting value).",
    )
    parser.add_argument(
        "--max-subdiv",
        type=int,
        default=2,
        help="Maximum allowed Subdivision Surface render levels (default: 2 starting value).",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Optional path to save JSON audit report.",
    )
    return parser.parse_args(raw_args)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        import bpy  # type: ignore
    except ImportError:
        print(
            "[ERROR] 'bpy' not available. Run inside headless Blender:\n"
            "  blender -b scene.blend -P skills/14-blender-pipeline/scripts/vram_audit.py -- --max-texture-px 4096",
            file=sys.stderr,
        )
        return 2

    warnings: list[str] = []
    total_tex_mb = 0.0
    oversized_textures: list[str] = []

    for img in bpy.data.images:
        w, h = img.size[0], img.size[1]
        if w == 0 or h == 0:
            continue
        bytes_per_channel = 4 if img.is_float else 1
        channels = img.channels or 4
        est_mb = (w * h * channels * bytes_per_channel) / (1024.0 * 1024.0)
        total_tex_mb += est_mb
        if w > args.max_texture_px or h > args.max_texture_px:
            msg = f"{img.name} ({w}x{h}, ~{est_mb:.1f} MB)"
            oversized_textures.append(msg)
            warnings.append(f"Oversized texture > {args.max_texture_px}px: {msg}")

    total_verts = 0
    total_polys = 0
    high_subdiv_objects: list[str] = []
    mesh_signatures: dict[tuple[int, int], list[str]] = defaultdict(list)

    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or obj.data is None:
            continue
        mesh = obj.data
        v_count = len(mesh.vertices)
        p_count = len(mesh.polygons)

        subdiv_mult = 1
        for mod in obj.modifiers:
            if mod.type == "SUBSURF":
                if mod.render_levels > args.max_subdiv:
                    high_subdiv_objects.append(f"{obj.name} (render_levels={mod.render_levels})")
                    warnings.append(
                        f"Object '{obj.name}' has Subsurf render_levels={mod.render_levels} (> {args.max_subdiv})."
                    )
                subdiv_mult *= 4 ** max(0, mod.render_levels)

        total_verts += v_count * subdiv_mult
        total_polys += p_count * subdiv_mult

        if mesh.users == 1 and v_count >= 500:
            mesh_signatures[(v_count, p_count)].append(obj.name)

    uninstanced_groups: list[dict] = []
    for (v_count, p_count), names in mesh_signatures.items():
        if len(names) >= 3:
            uninstanced_groups.append(
                {"verts": v_count, "polys": p_count, "count": len(names), "examples": names[:5]}
            )
            warnings.append(
                f"{len(names)} objects share identical topology ({v_count} verts, {p_count} polys) "
                f"without mesh instancing (e.g., {names[:3]})."
            )

    # Rough conservative BVH + geometry buffer estimate (~120 bytes/vert + ~64 bytes/poly + 900 MB Cycles base kernel)
    est_geom_mb = ((total_verts * 120) + (total_polys * 64)) / (1024.0 * 1024.0)
    est_base_kernel_mb = 900.0
    est_total_vram_mb = est_base_kernel_mb + total_tex_mb + est_geom_mb

    report = {
        "estimated_total_vram_mb": round(est_total_vram_mb, 1),
        "t4_safe_ceiling_mb": T4_SAFE_CEILING_MB,
        "estimated_texture_vram_mb": round(total_tex_mb, 1),
        "estimated_geometry_bvh_mb": round(est_geom_mb, 1),
        "subdivided_vertex_estimate": total_verts,
        "subdivided_polygon_estimate": total_polys,
        "oversized_textures": oversized_textures,
        "high_subdiv_objects": high_subdiv_objects,
        "uninstanced_duplicate_groups": uninstanced_groups,
        "warnings": warnings,
        "status": "PASS" if est_total_vram_mb <= T4_SAFE_CEILING_MB and not oversized_textures else "WARN",
    }

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("=== Tesla T4 VRAM Scene Audit ===")
    print(f"Estimated Total VRAM : {report['estimated_total_vram_mb']} MB / {T4_SAFE_CEILING_MB} MB ceiling")
    print(f"  - Textures         : {report['estimated_texture_vram_mb']} MB")
    print(f"  - Geometry & BVH   : {report['estimated_geometry_bvh_mb']} MB ({total_polys:,} effective polys)")
    for w in warnings:
        print(f"  [WARN] {w}")

    if est_total_vram_mb > T4_SAFE_CEILING_MB:
        print(
            f"[FAIL] Estimated VRAM ({est_total_vram_mb:.1f} MB) exceeds T4 safe ceiling ({T4_SAFE_CEILING_MB} MB).",
            file=sys.stderr,
        )
        return 1

    print("[OK] Scene fits within Tesla T4 VRAM safety budget.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
