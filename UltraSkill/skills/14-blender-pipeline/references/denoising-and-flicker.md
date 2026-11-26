# Denoising, High-Sample Reference Crops & Temporal Flicker

## 1. The Denoiser Trap

AI denoisers (`OPTIX` and `OPENIMAGEDENOISE`) reconstruct clean gradients from low sample counts, but when starved of samples they wipe out pore displacement, brushed-metal anisotropy, fabric weave, and fine dust—producing the plastic "waxy CG" look. In animation, frame-independent spatial denoising causes low-frequency blotches to swim ("boil") across dark walls.

## 2. Mandatory High-Sample Crop Verification

Before approving any `REVIEW` or `FINAL` preset on a new scene:

1. Render 1 full frame with your candidate preset (`REVIEW` at `256` samples, denoiser `ON`).
2. Render a 20% center border crop (`384x216` px at 1080p) at `2048` samples with denoiser `OFF` using:
   ```bash
   blender -b scene.blend -P skills/14-blender-pipeline/scripts/apply_preset.py -- \
     --preset REVIEW --crop-ref --save scene_crop_ref.blend
   ```
3. Compare the two crops at `200%` zoom in `QUALITY.md`:
   - **Pass**: Micro-scratches, normal map bump, and contact shadow sharpness match within perceptual tolerance.
   - **Fail (Waxiness)**: Roughness breakup disappeared in the denoised frame. *Fix*: Enable `RGB_ALBEDO_NORMAL` passes on the denoiser, raise `adaptive_min_samples` from `64` to `128`, or lower `adaptive_threshold` from `0.015` to `0.008` (starting values).

## 3. OptiX vs OpenImageDenoise (OIDN)

| Denoiser | Execution Hardware | Best Use Case | Trade-offs |
|---|---|---|---|
| **OptiX Denoiser** | NVIDIA Tensor Cores (T4 GPU) | `PREVIEW` and `REVIEW` stills, fast lookdev (`< 0.15 s` overhead per 1080p frame) | Can slightly smear sub-pixel hair or high-frequency bump below `128` samples. |
| **OpenImageDenoise (OIDN)** | GPU (Blender 4.1+ on supported NVIDIA GPUs) or CPU | `FINAL` hero frames and dark volumetric shots with `Albedo + Normal` prefilter set to `ACCURATE` | Preserves sharper micro-texture edges at `512–1024` samples; `~0.5–1.5 s` overhead per frame. |

## 4. Eliminating Temporal Flicker in Moving Sequences

Never render a 1440-frame trailer before testing a **24-frame motion strip** (`1.0 second`) on the shot with the fastest camera move or darkest shadows:

1. **Lock Adaptive Min Samples**: Adaptive sampling causes flicker if adjacent frames stop sampling a shadow pixel at `16` vs `64` samples. Keep `adaptive_min_samples >= 64` for `REVIEW` and `>= 128` for `FINAL` animations (starting values).
2. **Animated Noise Seed**: Enable animated seed (`scene.cycles.use_animated_seed = True`) so residual fine noise behaves like natural organic film grain rather than a static screen-door pattern stuck to the monitor.
3. **Clamp Indirect Fireflies**: Set `scene.cycles.sample_clamp_indirect = 10.0` (starting value) so single-frame caustic fireflies do not cause the denoiser to bloom a bright patch for one frame.
4. **Multi-Frame EXR Temporal Denoising**: For extreme low-light interiors, write `Noisy Image`, `Denoising Albedo`, `Denoising Normal`, `Vector`, and `Depth` into Multi-Layer OpenEXR and run Blender's command-line sequence denoiser or compositing pass before final grain application.
