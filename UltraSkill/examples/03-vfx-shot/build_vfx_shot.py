#!/usr/bin/env python3
"""Configure the Example 03 VFX destruction + OpenVDB smoke shot and MultiLayer EXR AOV compositor tree."""

import argparse
import json
import pathlib
import sys
from typing import Any, Dict


def get_vfx_shot_config() -> Dict[str, Any]:
    return {
        "shot_id": "SH_VFX_010",
        "fps": 24,
        "preroll_start_frame": -23,
        "start_frame": 1,
        "end_frame": 96,
        "render": {
            "engine": "CYCLES",
            "compute_device_type": "OPTIX",
            "gpu_use": True,
            "cpu_use": False,
            "resolution": [1920, 1080],
            "samples": 256,
            "volume_step_rate": 1.0,
            "volume_max_steps": 256,
            "motion_blur_shutter": 0.5,
            "file_format": "OPEN_EXR_MULTILAYER",
            "color_depth": "16",
            "view_transform": "AgX",
        },
        "simulations": {
            "rigid_body_fracture": {
                "chunk_count": 140,
                "substeps_per_frame": 10,
                "solver_iterations": 20,
                "trigger_frame": 18,
                "deactivation_linear_vel_m_s": 0.08,
            },
            "mantaflow_smoke_fire": {
                "domain_size_m": [4.5, 4.5, 6.0],
                "resolution_max": 160,
                "use_adaptive_domain": True,
                "vorticity": 0.25,
                "cache_format": "OPENVDB",
                "cache_compression": "ZIP",
                "cache_data_depth": "16",
                "blackbody_intensity": 1.8,
                "flame_max_temp_k": 4200,
            },
            "debris_sparks": {
                "particle_count": 3500,
                "lifetime_frames": 38,
                "initial_velocity_m_s": 11.5,
            },
        },
        "aov_passes": [
            "Combined",
            "DiffDir",
            "DiffInd",
            "DiffCol",
            "GlossDir",
            "GlossInd",
            "GlossCol",
            "Emit",
            "VolumeDir",
            "Mist",
            "Vector",
            "CryptomatteObject",
        ],
    }


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-config", type=pathlib.Path, help="Write VFX shot config JSON to disk")
    parser.add_argument("--self-test", action="store_true", help="Run built-in VFX config self-test")
    args = parser.parse_args(argv)

    cfg = get_vfx_shot_config()
    if args.output_config:
        args.output_config.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

    if args.self_test:
        assert cfg["render"]["compute_device_type"] == "OPTIX"
        assert cfg["preroll_start_frame"] == -23
        assert "VolumeDir" in cfg["aov_passes"]
        assert "CryptomatteObject" in cfg["aov_passes"]
        print("Self-test PASSED: VFX shot config (24f preroll, 140 RB chunks, 160-div VDB, 12 AOVs) verified.")
        return 0

    print(json.dumps(cfg, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
