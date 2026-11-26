#!/usr/bin/env python3
"""
OpenVDB & Mantaflow Simulation Voxel, RAM & Disk Budget Estimator (`sim_budget_estimator.py`).

Pure standard-library Python calculator that estimates:
  1. Grid dimensions (Nx, Ny, Nz) and total active voxels from domain size (meters),
     resolution divisions, and wavelet noise upres factor.
  2. Peak solver system RAM in megabytes.
  3. Per-frame and total sequence OpenVDB disk cache footprint (MB / GB) for 16-bit
     Half-Float ZIP/BLOSC compressed caches with Adaptive Domain sparsity.
  4. Halts with exit code 1 if peak RAM exceeds `--max-ram-gb` (default: 10.0 GB Colab safe ceiling)
     or total cache exceeds `--max-disk-gb` (default: 8.0 GB Google Drive safe ceiling).
"""

from __future__ import annotations

import argparse
import json
import math
import sys


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="sim_budget_estimator.py",
        description="Estimate Mantaflow OpenVDB voxel count, peak solver RAM, and Google Drive cache size before baking.",
    )
    parser.add_argument(
        "--domain-size",
        default="4.0,4.0,6.0",
        help="Domain bounding box dimensions (Lx,Ly,Lz) in meters (default: '4.0,4.0,6.0').",
    )
    parser.add_argument(
        "--divisions",
        type=int,
        required=True,
        help="Base resolution divisions along the longest domain edge (e.g., 192).",
    )
    parser.add_argument(
        "--noise-upres",
        type=int,
        default=1,
        choices=[1, 2, 4],
        help="Wavelet noise upres factor (1 = off, 2 = 2x per axis / 8x voxels; default: 1).",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=120,
        help="Number of simulation frames to bake (default: 120).",
    )
    parser.add_argument(
        "--adaptive-occupancy",
        type=float,
        default=0.35,
        help="Expected average fraction of domain occupied by active smoke/fluid voxels (0.1 to 1.0; default: 0.35).",
    )
    parser.add_argument(
        "--max-ram-gb",
        type=float,
        default=10.0,
        help="Maximum allowed peak solver RAM in GB (default: 10.0 GB Colab safe ceiling).",
    )
    parser.add_argument(
        "--max-disk-gb",
        type=float,
        default=8.0,
        help="Maximum allowed total OpenVDB sequence cache in GB on Google Drive (default: 8.0 GB).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        dims = [float(x.strip()) for x in args.domain_size.split(",")]
        if len(dims) != 3 or any(d <= 0 for d in dims):
            raise ValueError
    except ValueError:
        print(f"[ERROR] Invalid --domain-size '{args.domain_size}' (expected 3 positive floats).", file=sys.stderr)
        return 2

    if args.divisions < 16 or args.frames < 1:
        print("[ERROR] --divisions must be >= 16 and --frames >= 1.", file=sys.stderr)
        return 2

    l_max = max(dims)
    nx = max(1, math.ceil(args.divisions * (dims[0] / l_max)))
    ny = max(1, math.ceil(args.divisions * (dims[1] / l_max)))
    nz = max(1, math.ceil(args.divisions * (dims[2] / l_max)))
    voxel_size_mm = (l_max / args.divisions) * 1000.0

    base_voxels = nx * ny * nz
    upres_mult = args.noise_upres**3
    effective_voxels = base_voxels * upres_mult

    # Mantaflow solver holds ~10 float32 grids (vx, vy, vz, density, heat, fuel, flame, pressure, etc.) = ~44 bytes/base voxel
    # plus ~12 bytes per upres wavelet voxel
    solver_ram_bytes = (base_voxels * 44) + ((effective_voxels - base_voxels) * 12)
    peak_ram_gb = solver_ram_bytes / (1024.0**3)

    # 16-bit Half-Float ZIP-compressed OpenVDB averages ~5.5 bytes per active occupied voxel across grids
    occupancy = max(0.05, min(1.0, args.adaptive_occupancy))
    per_frame_vdb_mb = (effective_voxels * occupancy * 5.5) / (1024.0**2)
    total_disk_gb = (per_frame_vdb_mb * args.frames) / 1024.0

    report = {
        "domain_meters": dims,
        "base_grid": [nx, ny, nz],
        "voxel_size_mm": round(voxel_size_mm, 2),
        "base_voxels": base_voxels,
        "noise_upres_factor": args.noise_upres,
        "effective_voxels": effective_voxels,
        "estimated_peak_ram_gb": round(peak_ram_gb, 3),
        "estimated_frame_vdb_mb": round(per_frame_vdb_mb, 2),
        "estimated_total_disk_gb": round(total_disk_gb, 3),
        "frames": args.frames,
        "status": "PASS" if (peak_ram_gb <= args.max_ram_gb and total_disk_gb <= args.max_disk_gb) else "OVER_BUDGET",
    }

    print(json.dumps(report, indent=2))

    errors: list[str] = []
    if peak_ram_gb > args.max_ram_gb:
        errors.append(
            f"Estimated peak RAM ({peak_ram_gb:.2f} GB) exceeds limit ({args.max_ram_gb:.2f} GB). "
            "Lower --divisions or tighten domain bounds."
        )
    if total_disk_gb > args.max_disk_gb:
        errors.append(
            f"Estimated OpenVDB cache size ({total_disk_gb:.2f} GB) exceeds Drive limit ({args.max_disk_gb:.2f} GB)."
        )

    if errors:
        for e in errors:
            print(f"[FAIL] {e}", file=sys.stderr)
        return 1

    print("[OK] Simulation fits within Colab RAM and Google Drive storage budget.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
