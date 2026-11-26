#!/usr/bin/env python3
"""
Cycles-to-glTF Secondary UV Lightmap Baker (`bake_lightmap_blender.py`).

Bridges the offline Cycles OptiX -> realtime Three.js/Godot fidelity gap:
  1. Creates a non-overlapping secondary UV layer (`UVMap_Lightmap`) across all
     static render-visible meshes via Smart UV Project.
  2. Allocates a single shared lightmap image (`--size`, default `1024x1024` for LOW preset).
  3. Bakes Cycles Diffuse Direct + Indirect lighting (`use_pass_color = False`) so
     soft area-light shadows, multi-bounce GI, and contact occlusion are captured.
  4. Saves the baked lightmap PNG/EXR and exports a `.glb` ready for Three.js.
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
    raw_args = extract_script_args(sys.argv if argv is None else ["bake_lightmap_blender.py", *argv])
    parser = argparse.ArgumentParser(
        prog="bake_lightmap_blender.py",
        description="Bake Cycles GI diffuse lighting onto a secondary UV layer and export glTF (.glb).",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=1024,
        choices=[512, 1024, 2048, 4096],
        help="Baked lightmap resolution in pixels (default: 1024 for LOW laptop preset).",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=128,
        help="Cycles bake sample count (default: 128 starting value).",
    )
    parser.add_argument(
        "--lightmap-out",
        type=Path,
        required=True,
        help="Output filepath for the baked lightmap PNG (e.g., ./baked_lightmap.png).",
    )
    parser.add_argument(
        "--glb-out",
        type=Path,
        default=None,
        help="Optional output filepath to export the UV2-equipped scene as .glb.",
    )
    return parser.parse_args(raw_args)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        import bpy  # type: ignore
    except ImportError:
        print(
            "[ERROR] 'bpy' not available. Run inside headless Blender:\n"
            "  blender -b scene.blend -P skills/17-realtime-web-scenes/scripts/bake_lightmap_blender.py -- "
            "--lightmap-out /tmp/lightmap.png --glb-out /tmp/scene.glb",
            file=sys.stderr,
        )
        return 2

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = args.samples
    scene.cycles.use_adaptive_sampling = True

    meshes = [o for o in scene.objects if o.type == "MESH" and not o.hide_render]
    if not meshes:
        print("[ERROR] Scene contains zero render-visible MESH objects to bake.", file=sys.stderr)
        return 1

    lightmap_img = bpy.data.images.new(
        name="Cycles_Baked_Lightmap",
        width=args.size,
        height=args.size,
        alpha=False,
        float_buffer=True,
    )

    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes:
        obj.select_set(True)
        mesh = obj.data
        if "UVMap_Lightmap" not in mesh.uv_layers:
            mesh.uv_layers.new(name="UVMap_Lightmap")
        mesh.uv_layers.active = mesh.uv_layers["UVMap_Lightmap"]

        if not obj.data.materials:
            mat = bpy.data.materials.new(name=f"{obj.name}_BakeMat")
            mat.use_nodes = True
            obj.data.materials.append(mat)

        for mat in obj.data.materials:
            if not mat:
                continue
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            tex_node = nodes.new(type="ShaderNodeTexImage")
            tex_node.name = "UltraSkill_Bake_Target"
            tex_node.image = lightmap_img
            for n in nodes:
                n.select = False
            tex_node.select = True
            nodes.active = tex_node

    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(
        angle_limit=math.radians(66.0),
        island_margin=0.015,
        correct_aspect=True,
        scale_to_bounds=True,
    )
    bpy.ops.object.mode_set(mode="OBJECT")

    scene.render.bake.use_pass_direct = True
    scene.render.bake.use_pass_indirect = True
    scene.render.bake.use_pass_color = False
    scene.render.bake.margin = max(4, args.size // 256)

    print(f"[INFO] Baking Cycles DIFFUSE lightmap ({args.size}x{args.size}, {args.samples} spp) ...")
    bpy.ops.object.bake(type="DIFFUSE")

    out_img_path = args.lightmap_out.resolve()
    out_img_path.parent.mkdir(parents=True, exist_ok=True)
    lightmap_img.filepath_raw = str(out_img_path)
    lightmap_img.file_format = "PNG"
    lightmap_img.save()
    print(f"[OK] Saved baked Cycles lightmap -> {out_img_path}")

    if args.glb_out is not None:
        glb_path = args.glb_out.resolve()
        glb_path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.export_scene.gltf(
            filepath=str(glb_path),
            export_format="GLB",
            export_apply=True,
        )
        print(f"[OK] Exported glTF binary with UVMap_Lightmap -> {glb_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
