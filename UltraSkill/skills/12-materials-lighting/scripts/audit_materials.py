#!/usr/bin/env python3
"""
PBR Material, Color-Space & AgX Lighting Auditor (`audit_materials.py`).

Inspects a Blender scene headlessly to enforce `12-materials-lighting` quality gates:
  1. Scene view transform is set to `AgX`.
  2. Dielectric materials (`Metallic < 0.5`) have Base Color luminance within `[0.03, 0.82]`.
  3. Metallic value on Principled BSDF is binary (`<= 0.05` or `>= 0.95`) unless driven
     by a linked texture mask.
  4. Hero materials (or all materials when `--require-roughness-variation` is set) have a
     linked node driving the `Roughness` input rather than a static flat float.
  5. Image textures wired into `Roughness`, `Metallic`, or `Normal Map` nodes use
     `colorspace_settings.name == 'Non-Color'`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def extract_script_args(argv: list[str]) -> list[str]:
    if "--" in argv:
        return argv[argv.index("--") + 1 :]
    return argv[1:]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    raw_args = extract_script_args(sys.argv if argv is None else ["audit_materials.py", *argv])
    parser = argparse.ArgumentParser(
        prog="audit_materials.py",
        description="Audit Blender scene materials for PBR energy bounds, Non-Color maps, roughness variation, and AgX.",
    )
    parser.add_argument(
        "--require-roughness-variation",
        action="store_true",
        help="Flag any Principled BSDF material whose Roughness socket is not driven by a node link.",
    )
    parser.add_argument(
        "--min-albedo",
        type=float,
        default=0.03,
        help="Minimum allowed linear luminance for dielectric Base Color (default: 0.03).",
    )
    parser.add_argument(
        "--max-albedo",
        type=float,
        default=0.82,
        help="Maximum allowed linear luminance for dielectric Base Color (default: 0.82).",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Optional path to write JSON material audit report.",
    )
    return parser.parse_args(raw_args)


def linear_luminance(rgb: tuple[float, float, float]) -> float:
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def find_upstream_images(socket, visited: set | None = None) -> list:
    if visited is None:
        visited = set()
    images = []
    for link in socket.links:
        node = link.from_node
        if node in visited:
            continue
        visited.add(node)
        if node.type == "TEX_IMAGE" and getattr(node, "image", None) is not None:
            images.append(node.image)
        for inp in node.inputs:
            images.extend(find_upstream_images(inp, visited))
    return images


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        import bpy  # type: ignore
    except ImportError:
        print(
            "[ERROR] 'bpy' not available. Run inside headless Blender:\n"
            "  blender -b scene.blend -P skills/12-materials-lighting/scripts/audit_materials.py",
            file=sys.stderr,
        )
        return 2

    scene = bpy.context.scene
    errors: list[str] = []
    warnings: list[str] = []

    view_tx = scene.view_settings.view_transform
    if view_tx != "AgX":
        errors.append(f"Scene view_transform is '{view_tx}' (must be 'AgX').")

    audited_materials: list[dict] = []
    for mat in bpy.data.materials:
        if mat.name == "Dots Stroke" or not mat.use_nodes or mat.node_tree is None:
            continue
        if mat.users == 0:
            continue

        for node in mat.node_tree.nodes:
            if node.type != "BSDF_PRINCIPLED":
                continue

            base_sock = node.inputs.get("Base Color")
            metal_sock = node.inputs.get("Metallic")
            rough_sock = node.inputs.get("Roughness")
            normal_sock = node.inputs.get("Normal")
            trans_sock = node.inputs.get("Transmission Weight") or node.inputs.get("Transmission")

            metal_val = float(metal_sock.default_value) if metal_sock else 0.0
            metal_linked = bool(metal_sock and metal_sock.is_linked)
            trans_val = float(trans_sock.default_value) if trans_sock else 0.0

            if not metal_linked and 0.05 < metal_val < 0.95:
                errors.append(
                    f"Material '{mat.name}': non-binary Metallic default_value={metal_val:.2f} without a texture mask."
                )

            base_linked = bool(base_sock and base_sock.is_linked)
            lum = 0.5
            if base_sock and not base_linked:
                c = base_sock.default_value
                lum = linear_luminance((float(c[0]), float(c[1]), float(c[2])))
                if metal_val < 0.5 and trans_val < 0.5:
                    if lum < args.min_albedo or lum > args.max_albedo:
                        errors.append(
                            f"Material '{mat.name}': dielectric Base Color luminance {lum:.3f} "
                            f"is outside [{args.min_albedo}, {args.max_albedo}]."
                        )

            rough_linked = bool(rough_sock and rough_sock.is_linked)
            if not rough_linked and trans_val < 0.5:
                msg = f"Material '{mat.name}': constant un-modulated Roughness ({float(rough_sock.default_value):.2f})."
                if args.require_roughness_variation:
                    errors.append(msg)
                else:
                    warnings.append(msg)

            for label, sock in [("Roughness", rough_sock), ("Metallic", metal_sock), ("Normal", normal_sock)]:
                if not sock:
                    continue
                for img in find_upstream_images(sock):
                    cs = img.colorspace_settings.name
                    if cs not in ("Non-Color", "Raw"):
                        errors.append(
                            f"Material '{mat.name}' ({label}): image '{img.name}' uses colorspace '{cs}' (must be 'Non-Color')."
                        )

            audited_materials.append(
                {
                    "material": mat.name,
                    "base_color_luminance": round(lum, 4),
                    "metallic": round(metal_val, 3),
                    "metallic_linked": metal_linked,
                    "roughness_linked": rough_linked,
                }
            )

    report = {
        "status": "PASS" if not errors else "FAIL",
        "view_transform": view_tx,
        "materials_audited": len(audited_materials),
        "errors": errors,
        "warnings": warnings,
        "details": audited_materials,
    }

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"=== UltraSkill PBR Material & AgX Audit ({len(audited_materials)} materials) ===")
    for w in warnings:
        print(f"  [WARN] {w}")
    if errors:
        for e in errors:
            print(f"  [FAIL] {e}", file=sys.stderr)
        return 1

    print("[OK] All materials and color management settings passed PBR audit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
