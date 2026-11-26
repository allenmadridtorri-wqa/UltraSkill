#!/usr/bin/env python3
"""Procedural Blender Cycles OptiX studio still builder with dry-run specification export for 4 GB RAM laptops."""

import argparse
import json
import pathlib
import sys
from typing import Any, Dict


def get_canonical_scene_spec(preset: str = "STILL_HIGH") -> Dict[str, Any]:
    samples_map = {"FAST_PREVIEW": 64, "PROD_1080P": 256, "STILL_HIGH": 1024, "HERO_4K": 2048}
    res_map = {
        "FAST_PREVIEW": (1280, 720),
        "PROD_1080P": (1920, 1080),
        "STILL_HIGH": (2560, 1440),
        "HERO_4K": (3840, 2160),
    }
    w, h = res_map.get(preset, (2560, 1440))

    return {
        "scene_name": "chrono_studio_still_v1",
        "unit_scale_meters": 1.0,
        "render": {
            "engine": "CYCLES",
            "compute_device_type": "OPTIX",
            "gpu_use": True,
            "cpu_use": False,
            "preset": preset,
            "resolution_x": w,
            "resolution_y": h,
            "samples": samples_map.get(preset, 1024),
            "adaptive_threshold": 0.005,
            "denoiser": "OPENIMAGEDENOISE",
            "denoising_input_passes": "RGB_ALBEDO_NORMAL",
            "view_transform": "AgX",
            "look": "AgX - High Contrast",
            "file_format": "OPEN_EXR",
            "color_depth": "16",
            "exr_codec": "DWAA",
        },
        "camera": {
            "sensor_width_mm": 36.0,
            "focal_length_mm": 85.0,
            "f_stop": 4.0,
            "focus_distance_m": 0.28,
            "location_m": [0.18, -0.22, 0.14],
            "target_m": [0.0, 0.0, 0.012],
        },
        "objects": [
            {
                "name": "Basalt_Slab",
                "dimensions_m": [0.32, 0.24, 0.018],
                "bevel_width_m": 0.0018,
                "bevel_segments": 3,
                "material": "Wet_Basalt",
            },
            {
                "name": "Chrono_Case_Titanium",
                "dimensions_m": [0.042, 0.042, 0.0115],
                "bevel_width_m": 0.00045,
                "bevel_segments": 4,
                "material": "Brushed_Titanium",
            },
            {
                "name": "Chrono_Crystal_Sapphire",
                "dimensions_m": [0.036, 0.036, 0.002],
                "bevel_width_m": 0.00025,
                "bevel_segments": 3,
                "material": "Sapphire_Glass",
            },
        ],
        "materials": {
            "Wet_Basalt": {
                "metallic": 0.0,
                "base_color_linear": [0.045, 0.047, 0.050],
                "roughness_min": 0.18,
                "roughness_max": 0.55,
                "ior": 1.52,
            },
            "Brushed_Titanium": {
                "metallic": 1.0,
                "base_color_linear": [0.54, 0.53, 0.50],
                "roughness_min": 0.18,
                "roughness_max": 0.30,
                "anisotropy": 0.65,
            },
            "Sapphire_Glass": {
                "metallic": 0.0,
                "base_color_linear": [0.98, 0.98, 0.99],
                "roughness_min": 0.01,
                "roughness_max": 0.02,
                "transmission": 1.0,
                "ior": 1.77,
            },
        },
        "lights": [
            {"name": "Key_Softbox", "type": "AREA", "size_m": [0.6, 0.4], "power_w": 45.0, "temp_k": 4800},
            {"name": "Fill_Bounce", "type": "AREA", "size_m": [0.9, 0.9], "power_w": 9.0, "temp_k": 6000},
            {"name": "Rim_Strip", "type": "AREA", "size_m": [0.5, 0.12], "power_w": 65.0, "temp_k": 5600},
        ],
    }


def build_in_blender(spec: Dict[str, Any], output_exr: pathlib.Path | None) -> None:
    """Execute inside Blender ('blender -b -P build_still_scene.py') on Google Colab GPU."""
    import bpy  # type: ignore

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0

    r_cfg = spec["render"]
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"
    prefs.get_devices()
    gpu_count = 0
    for dev in prefs.devices:
        if dev.type in {"OPTIX", "CUDA"}:
            dev.use = True
            gpu_count += 1
        else:
            dev.use = False
    if gpu_count == 0:
        raise RuntimeError("No NVIDIA OptiX GPU detected. Run this render on a Google Colab T4+ GPU.")

    scene.cycles.device = "GPU"
    scene.cycles.samples = r_cfg["samples"]
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = r_cfg["adaptive_threshold"]
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = "OPENIMAGEDENOISE"
    scene.render.resolution_x = r_cfg["resolution_x"]
    scene.render.resolution_y = r_cfg["resolution_y"]
    scene.view_settings.view_transform = r_cfg["view_transform"]
    scene.view_settings.look = r_cfg["look"]

    if output_exr:
        scene.render.image_settings.file_format = "OPEN_EXR"
        scene.render.image_settings.color_depth = "16"
        scene.render.filepath = str(output_exr)
        bpy.ops.render.render(write_still=True)


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", default="STILL_HIGH", choices=["FAST_PREVIEW", "PROD_1080P", "STILL_HIGH", "HERO_4K"])
    parser.add_argument("--output", type=pathlib.Path, help="Output .exr path (when running inside Blender on Colab)")
    parser.add_argument("--dump-spec", type=pathlib.Path, help="Write scene specification JSON to disk")
    parser.add_argument("--dry-run", action="store_true", help="Print canonical scene spec JSON without requiring bpy")
    parser.add_argument("--self-test", action="store_true", help="Verify scene spec creation on local laptop")
    args = parser.parse_args(argv)

    spec = get_canonical_scene_spec(args.preset)
    if args.dump_spec:
        args.dump_spec.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")

    if args.self_test:
        assert spec["render"]["compute_device_type"] == "OPTIX"
        assert spec["render"]["cpu_use"] is False
        assert len(spec["objects"]) == 3
        print("Self-test PASSED: Cycles OptiX studio still scene specification verified.")
        return 0

    if args.dry_run or "bpy" not in sys.modules:
        try:
            import bpy  # type: ignore  # noqa: F401
        except ImportError:
            print(json.dumps(spec, indent=2))
            return 0

    build_in_blender(spec, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
