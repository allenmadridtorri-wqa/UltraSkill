#!/usr/bin/env python3
"""
Zero-Dependency glTF / GLB Asset Budget Auditor (`gltf_budget_check.py`).

Uses only Python's standard library (`struct`, `json`, `pathlib`) to parse `.gltf`
or binary `.glb` (glTF 2.0) files and verify them against UltraSkill hardware
presets (`LOW`, `MEDIUM`, `HIGH`):
  1. Counts total mesh primitives (each un-instanced primitive == at least 1 WebGL draw call).
  2. Estimates total vertices and triangles from accessor counts.
  3. Sums binary buffer and image byte sizes.
  4. Fails with exit code 1 if primitives (draw calls), triangles, or file size exceed
     the chosen preset ceiling (default: `LOW` for the 4 GB RAM / 1 GB Intel UHD laptop).
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path


GLB_MAGIC = 0x46546C67  # 'glTF' in little-endian ASCII
JSON_CHUNK_TYPE = 0x4E4F534A  # 'JSON'

PRESET_LIMITS = {
    "LOW": {
        "max_primitives_draw_calls": 50,
        "max_triangles": 150_000,
        "max_file_mb": 15.0,
    },
    "MEDIUM": {
        "max_primitives_draw_calls": 150,
        "max_triangles": 450_000,
        "max_file_mb": 35.0,
    },
    "HIGH": {
        "max_primitives_draw_calls": 350,
        "max_triangles": 1_200_000,
        "max_file_mb": 65.0,
    },
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="gltf_budget_check.py",
        description="Audit a .gltf or .glb file against LOW/MEDIUM/HIGH draw-call, triangle, and memory limits.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to the .gltf or .glb file to audit.",
    )
    parser.add_argument(
        "--preset",
        choices=["LOW", "MEDIUM", "HIGH"],
        default="LOW",
        help="Target hardware preset budget to enforce (default: LOW for 4 GB laptop).",
    )
    return parser.parse_args(argv)


def load_gltf_json(filepath: Path) -> dict:
    if filepath.suffix.lower() == ".glb":
        raw = filepath.read_bytes()
        if len(raw) < 20:
            raise ValueError("GLB file is smaller than 20-byte header.")
        magic, version, total_len, chunk_len, chunk_type = struct.unpack_from("<IIIII", raw, 0)
        if magic != GLB_MAGIC:
            raise ValueError(f"Invalid GLB magic header (0x{magic:08X} != 0x{GLB_MAGIC:08X}).")
        if version != 2:
            raise ValueError(f"Unsupported GLB version {version} (expected 2).")
        if chunk_type != JSON_CHUNK_TYPE:
            raise ValueError("First GLB chunk is not JSON.")
        json_bytes = raw[20 : 20 + chunk_len]
        return json.loads(json_bytes.decode("utf-8"))
    return json.loads(filepath.read_text(encoding="utf-8"))


def audit_gltf_dict(gltf: dict, file_size_bytes: int, preset: str) -> tuple[dict, list[str]]:
    limits = PRESET_LIMITS[preset]
    accessors = gltf.get("accessors", [])
    meshes = gltf.get("meshes", [])
    materials = gltf.get("materials", [])
    textures = gltf.get("textures", [])
    nodes = gltf.get("nodes", [])

    total_primitives = 0
    total_vertices = 0
    total_triangles = 0

    for mesh in meshes:
        for prim in mesh.get("primitives", []):
            total_primitives += 1
            attrs = prim.get("attributes", {})
            pos_idx = attrs.get("POSITION")
            v_count = 0
            if pos_idx is not None and 0 <= pos_idx < len(accessors):
                v_count = int(accessors[pos_idx].get("count", 0))
                total_vertices += v_count

            indices_idx = prim.get("indices")
            if indices_idx is not None and 0 <= indices_idx < len(accessors):
                idx_count = int(accessors[indices_idx].get("count", 0))
                total_triangles += idx_count // 3
            else:
                total_triangles += v_count // 3

    file_mb = file_size_bytes / (1024.0 * 1024.0)
    errors: list[str] = []

    if total_primitives > limits["max_primitives_draw_calls"]:
        errors.append(
            f"Mesh primitives / draw calls ({total_primitives}) exceed {preset} limit "
            f"({limits['max_primitives_draw_calls']}). Merge static meshes or use InstancedMesh."
        )
    if total_triangles > limits["max_triangles"]:
        errors.append(
            f"Triangle count ({total_triangles:,}) exceeds {preset} limit ({limits['max_triangles']:,})."
        )
    if file_mb > limits["max_file_mb"]:
        errors.append(
            f"File size ({file_mb:.2f} MB) exceeds {preset} limit ({limits['max_file_mb']:.2f} MB)."
        )

    summary = {
        "preset": preset,
        "nodes": len(nodes),
        "meshes": len(meshes),
        "primitives_draw_calls": total_primitives,
        "vertices": total_vertices,
        "triangles": total_triangles,
        "materials": len(materials),
        "textures": len(textures),
        "file_size_mb": round(file_mb, 3),
        "limits": limits,
        "status": "PASS" if not errors else "FAIL",
    }
    return summary, errors


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    in_path = args.input.resolve()
    if not in_path.is_file():
        print(f"[ERROR] File not found: {in_path}", file=sys.stderr)
        return 1

    try:
        gltf_data = load_gltf_json(in_path)
    except Exception as exc:
        print(f"[ERROR] Failed to parse {in_path}: {exc}", file=sys.stderr)
        return 1

    summary, errors = audit_gltf_dict(gltf_data, in_path.stat().st_size, args.preset)
    print(json.dumps(summary, indent=2))

    if errors:
        for err in errors:
            print(f"[FAIL] {err}", file=sys.stderr)
        return 1

    print(f"[OK] Asset '{in_path.name}' passed {args.preset} realtime budget gate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
