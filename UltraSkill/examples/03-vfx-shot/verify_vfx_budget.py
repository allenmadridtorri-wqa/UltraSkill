#!/usr/bin/env python3
"""Verify that Example 03 VFX simulation cache size and peak VRAM stay within Colab Tesla T4 limits."""

import argparse
import json
import pathlib
import sys
from typing import Any, Dict, List, Tuple

from build_vfx_shot import get_vfx_shot_config


T4_SAFE_VRAM_MB = 12500.0
COLAB_SAFE_CACHE_GB = 15.0
MAX_SAFE_VOXELS = 8_000_000


def estimate_vfx_budgets(cfg: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
    errors: List[str] = []
    sim = cfg["simulations"]
    smoke = sim["mantaflow_smoke_fire"]
    rb = sim["rigid_body_fracture"]
    sparks = sim["debris_sparks"]

    total_sim_frames = cfg["end_frame"] - cfg["preroll_start_frame"] + 1
    dx, dy, dz = smoke["domain_size_m"]
    max_dim = max(dx, dy, dz)
    res_max = smoke["resolution_max"]

    nx = int(round(res_max * (dx / max_dim)))
    ny = int(round(res_max * (dy / max_dim)))
    nz = int(round(res_max * (dz / max_dim)))
    peak_voxels = nx * ny * nz
    # Adaptive domain typically occupies ~55% of full bounding box across the sequence
    avg_active_voxels = int(peak_voxels * (0.55 if smoke.get("use_adaptive_domain") else 1.0))

    # Half-float ZIP OpenVDB stores ~6 bytes/active voxel across density/flame/heat/vel grids
    vdb_bytes_per_frame = avg_active_voxels * 6.0
    total_cache_gb = round((vdb_bytes_per_frame * total_sim_frames) / (1024**3), 3)

    # VRAM estimation: Base OptiX kernel (1,100 MB) + VDB GPU volume grids + geometry + AOV buffers
    vdb_vram_mb = round((peak_voxels * 16.0) / (1024**2), 1)
    aov_vram_mb = round(len(cfg["aov_passes"]) * 18.5, 1)
    geo_tex_vram_mb = 1850.0 + (rb["chunk_count"] * 1.2) + (sparks["particle_count"] * 0.02)
    peak_vram_mb = round(1100.0 + vdb_vram_mb + aov_vram_mb + geo_tex_vram_mb, 1)

    if peak_voxels > MAX_SAFE_VOXELS:
        errors.append(f"Peak voxel count {peak_voxels} exceeds T4 safe limit {MAX_SAFE_VOXELS}")
    if total_cache_gb > COLAB_SAFE_CACHE_GB:
        errors.append(f"Estimated VDB cache {total_cache_gb} GB exceeds {COLAB_SAFE_CACHE_GB} GB budget")
    if peak_vram_mb > T4_SAFE_VRAM_MB:
        errors.append(f"Estimated peak VRAM {peak_vram_mb} MB exceeds T4 ceiling {T4_SAFE_VRAM_MB} MB")

    report = {
        "shot_id": cfg["shot_id"],
        "total_sim_frames_with_preroll": total_sim_frames,
        "voxel_grid_dimensions": [nx, ny, nz],
        "peak_voxels": peak_voxels,
        "estimated_vdb_cache_gb": total_cache_gb,
        "estimated_peak_vram_mb": peak_vram_mb,
        "t4_vram_headroom_mb": round(T4_SAFE_VRAM_MB - peak_vram_mb, 1),
        "passes_t4_budget": len(errors) == 0,
    }
    return len(errors) == 0, errors, report


def run_self_test() -> int:
    cfg = get_vfx_shot_config()
    ok, errs, rep = estimate_vfx_budgets(cfg)
    if not ok:
        for e in errs:
            print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    print(
        f"Self-test PASSED: VFX shot uses {rep['estimated_peak_vram_mb']} MB VRAM "
        f"and {rep['estimated_vdb_cache_gb']} GB disk cache on Colab T4."
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=pathlib.Path, help="Optional VFX config JSON path")
    parser.add_argument("--self-test", action="store_true", help="Run built-in VFX budget self-test")
    args = parser.parse_args()

    if args.self_test and args.config is None:
        return run_self_test()

    cfg = (
        json.loads(args.config.read_text(encoding="utf-8"))
        if args.config
        else get_vfx_shot_config()
    )
    ok, errs, rep = estimate_vfx_budgets(cfg)
    if not ok:
        for e in errs:
            print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    print(json.dumps(rep, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
