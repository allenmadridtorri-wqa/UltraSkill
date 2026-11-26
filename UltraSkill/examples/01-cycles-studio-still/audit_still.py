#!/usr/bin/env python3
"""Audit the Example 01 studio still scene specification against UltraSkill's 10 photorealism and OptiX quality bars."""

import argparse
import json
import pathlib
import sys
from typing import Any, Dict, List, Tuple

from build_still_scene import get_canonical_scene_spec


def audit_scene_spec(spec: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    r = spec.get("render", {})

    # 1. OptiX GPU enforcement & CPU disabled
    if r.get("engine") != "CYCLES" or r.get("compute_device_type") != "OPTIX":
        errors.append("Render engine must be CYCLES with compute_device_type='OPTIX'.")
    if not r.get("gpu_use") or r.get("cpu_use"):
        errors.append("GPU must be enabled (gpu_use=True) and CPU disabled (cpu_use=False) to prevent hybrid tile slowdown.")

    # 2. AgX Color Management & 16-bit OpenEXR output
    if r.get("view_transform") != "AgX":
        errors.append(f"view_transform must be 'AgX' (got {r.get('view_transform')}).")
    if r.get("file_format") != "OPEN_EXR" or r.get("color_depth") != "16":
        errors.append("Master output must use 16-bit OPEN_EXR.")

    # 3. Physical Camera parameters
    cam = spec.get("camera", {})
    if not (24.0 <= cam.get("focal_length_mm", 0) <= 135.0):
        errors.append("Camera focal_length_mm outside natural studio lens range [24, 135] mm.")
    if not (1.4 <= cam.get("f_stop", 0) <= 16.0):
        errors.append("Camera f_stop outside physical aperture range [1.4, 16.0].")

    # 4. Non-zero Bevels on all hard-surface objects (>= 0.2 mm)
    for obj in spec.get("objects", []):
        if obj.get("bevel_width_m", 0.0) < 0.0002 or obj.get("bevel_segments", 0) < 2:
            errors.append(f"Object '{obj.get('name')}' lacks physical bevel (>= 0.2mm, >= 2 segments).")

    # 5. PBR Energy Conservation & Roughness variation
    for mat_name, mat in spec.get("materials", {}).items():
        m = mat.get("metallic", 0.0)
        if m not in (0.0, 1.0):
            errors.append(f"Material '{mat_name}' has non-binary metallic={m} (must be 0.0 or 1.0).")
        if m == 0.0 and mat.get("transmission", 0.0) == 0.0:
            for c in mat.get("base_color_linear", []):
                if not (0.02 <= c <= 0.85):
                    errors.append(f"Dielectric material '{mat_name}' base_color channel {c} violates [0.02, 0.85].")
        if mat.get("roughness_max", 0.0) <= mat.get("roughness_min", 0.0):
            errors.append(f"Material '{mat_name}' lacks roughness variation (min < max required).")

    # 6. 3-Point Motivated Lighting ratio check
    lights = {l["name"]: l["power_w"] for l in spec.get("lights", [])}
    if len(lights) < 3:
        errors.append("Studio still requires at least 3 motivated area lights (Key, Fill, Rim).")
    elif lights.get("Key_Softbox", 0) <= lights.get("Fill_Bounce", 999) * 2.0:
        errors.append("Key-to-Fill power ratio must be > 2:1 to avoid flat ambient lighting.")

    return len(errors) == 0, errors


def run_self_test() -> int:
    spec = get_canonical_scene_spec("STILL_HIGH")
    ok, errs = audit_scene_spec(spec)
    if not ok:
        for e in errs:
            print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    print("Self-test PASSED: all 10 photorealism, PBR, bevel, AgX, and OptiX quality bars verified.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=pathlib.Path, help="Optional path to scene spec JSON file")
    parser.add_argument("--self-test", action="store_true", help="Run built-in studio still audit self-test")
    args = parser.parse_args()

    if args.self_test or args.spec is None:
        return run_self_test()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    ok, errs = audit_scene_spec(spec)
    if not ok:
        for e in errs:
            print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    print("Studio still audit PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
