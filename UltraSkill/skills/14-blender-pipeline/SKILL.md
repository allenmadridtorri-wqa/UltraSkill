---
name: 14-blender-pipeline
description: >-
  Headless Blender Cycles rendering pipeline using NVIDIA OptiX on Google Colab
  GPUs (Tesla T4 or better). Covers mandatory GPU hardware proof, PREVIEW/REVIEW/FINAL
  presets, 3-frame benchmarks (>3h approval gate), Google Drive per-frame
  manifest persistence and resume, and T4 15 GB VRAM auditing.
---

# 14-Blender-Pipeline: Cycles OptiX on Google Colab GPU

Never render Cycles on the user's 4 GB RAM / 1 GB Intel UHD laptop. All offline Cycles renders execute headlessly on a Google Colab GPU (Tesla T4 or better) with **OptiX** verified before any sequence starts.

## When to use

Load this skill whenever configuring Blender render settings, proving GPU acceleration on Colab, benchmarking frame times, auditing scene VRAM, or rendering stills and animation sequences to Google Drive.

## Inputs

- `.blend` scene file or procedural scene builder script.
- Target preset (`PREVIEW`, `REVIEW`, or `FINAL`).
- Google Drive output directory and `render_manifest.json` path.

## Steps

1. **Prove OptiX Hardware Engagement (Mandatory First Step)**:
   - Run `blender -b -P skills/14-blender-pipeline/scripts/optix_verify.py -- --output /tmp/optix_proof.png`.
   - The script sets `compute_device_type = 'OPTIX'`, calls `get_devices()`, enables only hardware OptiX GPU devices, sets `scene.cycles.device = 'GPU'`, prints Blender version, GPU name, and driver version via `nvidia-smi`, and renders 1 proof frame.
   - If OptiX initialization fails or zero OptiX GPUs are found, **STOP immediately**, report the exact error, and ask the user whether to approve `--allow-cuda-fallback`. Never fall back to CPU silently.
2. **Audit T4 VRAM Footprint**:
   - Run `blender -b scene.blend -P skills/14-blender-pipeline/scripts/vram_audit.py -- --max-texture-px 4096`.
   - Ensure peak geometry, instancing, and texture budgets stay under `12.5 GB` (starting value) on a 15 GB Tesla T4; see [`references/t4-vram-budgeting.md`](references/t4-vram-budgeting.md).
3. **Apply Quality Preset**:
   - Run `blender -b scene.blend -P skills/14-blender-pipeline/scripts/apply_preset.py -- --preset REVIEW --save scene_review.blend`.
   - Compare denoised output against a `2048-sample` small reference crop (`--crop-ref`) and check a 24-frame strip for temporal denoiser flicker; see [`references/denoising-and-flicker.md`](references/denoising-and-flicker.md).
4. **Benchmark 3 Representative Frames**:
   - Run `blender -b scene_review.blend -P skills/14-blender-pipeline/scripts/benchmark_scene.py -- --frames 1,720,1200 --total-frames 1440`.
   - If estimated total hours exceed `3.0 hours`, halt and request explicit user approval before passing `--approve-over-3h`.
5. **Execute Resumable Drive Render & Verify**:
   - Run `render_sequence.py` to write each finished 16-bit PNG or OpenEXR directly to Google Drive and update `render_manifest.json`.
   - On reconnect or completion, run `python3 skills/14-blender-pipeline/scripts/verify_frames.py --manifest <path>` to flag missing or corrupt frames.

## Numbers and defaults

All preset numbers below are **starting values** to verify against a high-sample crop:

| Preset | Resolution | Max Samples | Min Samples | Noise Threshold | Bounces (Total/Diff/Gloss/Trans/Vol) | Motion Blur | Output Format |
|---|---|---:|---:|---:|---|---|---|
| `PREVIEW` | `960x540` | `64` | `16` | `0.050` | `4 / 2 / 2 / 4 / 0` | Off | `PNG 8-bit` |
| `REVIEW` | `1920x1080` | `256` | `64` | `0.015` | `8 / 3 / 4 / 8 / 2` | On (`0.5` shutter) | `PNG 16-bit` |
| `FINAL` | `1920x1080` (`3840x2160` if benchmark `<= 3h`) | `1024` | `128` | `0.005` | `12 / 4 / 6 / 12 / 4` | On (`0.5` shutter) | `OPEN_EXR_MULTILAYER` (DWAA/ZIP, 16-bit float) or `PNG 16-bit` |

- **View Transform**: `AgX` (Look: `None` or `AgX - Medium High Contrast` starting value).
- **Approval gate**: `3.0 hours` estimated total render time.
- **T4 safe VRAM ceiling**: `12.5 GB` peak out of `15.0 GB` physical T4 VRAM (starting value).

## Failure modes and fixes

- **`OPTIX` compute device type raises `TypeError` or finds 0 GPUs**: Colab runtime has no GPU attached or driver is incompatible. Stop, report the exact exception and `nvidia-smi` output, and ask the user whether to switch runtime or approve CUDA.
- **Colab disconnects mid-sequence**: Never render to ephemeral `/tmp` without syncing. Point `--output-dir` and `--manifest` directly at `/content/drive/MyDrive/...`; `render_sequence.py` resumes automatically from the last verified frame.
- **Out-of-memory (`CUDA_ERROR_OUT_OF_MEMORY`) on T4**: Run `vram_audit.py`, convert duplicate meshes to collection instances, cap subdivision at render level `2`, and downscale non-hero 8K textures to 2K/4K.

## Done check

- `optix_verify.py` log confirms `OPTIX` GPU device active and `nvidia-smi` shows Blender process on GPU.
- `benchmark_scene.py` estimate is `<= 3.0 hours` (or user approval is logged in `DECISIONS.md`).
- `verify_frames.py` reports 0 missing, 0 zero-byte, and 0 corrupt frames on Google Drive.

## Related files

- [`references/optix-setup-and-proof.md`](references/optix-setup-and-proof.md)
- [`references/quality-presets.md`](references/quality-presets.md)
- [`references/denoising-and-flicker.md`](references/denoising-and-flicker.md)
- [`references/colab-resilience.md`](references/colab-resilience.md)
- [`references/t4-vram-budgeting.md`](references/t4-vram-budgeting.md)
- [`references/exr-and-color-pipeline.md`](references/exr-and-color-pipeline.md)
- [`references/eevee-headless-preview.md`](references/eevee-headless-preview.md)
- [`templates/colab_optix_runner.py`](templates/colab_optix_runner.py)
- [`templates/render_manifest.json`](templates/render_manifest.json)
- [`scripts/optix_verify.py`](scripts/optix_verify.py)
- [`scripts/apply_preset.py`](scripts/apply_preset.py)
- [`scripts/benchmark_scene.py`](scripts/benchmark_scene.py)
- [`scripts/render_sequence.py`](scripts/render_sequence.py)
- [`scripts/verify_frames.py`](scripts/verify_frames.py)
- [`scripts/vram_audit.py`](scripts/vram_audit.py)
