# Cycles OptiX Quality Presets (PREVIEW, REVIEW, FINAL)

All numeric parameters below are **starting values**. Apply them via [`../scripts/apply_preset.py`](../scripts/apply_preset.py) and verify noise/detail retention against a `2048-sample` un-denoised reference crop.

## 1. Preset Parameter Matrix

| Parameter | `PREVIEW` (Starting Value) | `REVIEW` (Starting Value) | `FINAL` (Starting Value) | How to Verify |
|---|---|---|---|---|
| **Primary Use** | Layout, camera blocking, key-to-fill ratios | Look approval, Fake-3D audit, 24-frame flicker check | Delivery master | Check stage in `ROUNDS.md` |
| **Resolution** | `960 x 540` | `1920 x 1080` | `1920 x 1080` (`3840 x 2160` only if benchmark `<= 3.0 h`) | Inspect output image dimensions |
| **Max Samples** | `64` | `256` | `1024` | `scene.cycles.samples` |
| **Min Adaptive Samples** | `16` | `64` | `128` | `scene.cycles.adaptive_min_samples` |
| **Adaptive Noise Threshold** | `0.050` | `0.015` | `0.005` | `scene.cycles.adaptive_threshold` |
| **Total Max Bounces** | `4` | `8` | `12` | `scene.cycles.max_bounces` |
| **Diffuse Bounces** | `2` | `3` | `4` | `scene.cycles.diffuse_bounces` |
| **Glossy Bounces** | `2` | `4` | `6` | `scene.cycles.glossy_bounces` |
| **Transmission Bounces** | `4` | `8` | `12` | `scene.cycles.transmission_bounces` |
| **Volume Bounces** | `0` | `2` | `4` | `scene.cycles.volume_bounces` |
| **Transparent Max Bounces** | `4` | `8` | `16` | `scene.cycles.transparent_max_bounces` |
| **Denoiser** | `OPTIX` (Albedo + Normal) | `OPTIX` (Albedo + Normal) | `OPENIMAGEDENOISE` or `OPTIX` (Albedo + Normal) | Compare against `--crop-ref` |
| **Motion Blur** | `Off` | `On` (`shutter = 0.5`) | `On` (`shutter = 0.5`, center on frame) | Inspect moving edge smear |
| **Filter Glossy / Clamp Indirect** | `0.5` / `10.0` | `0.2` / `10.0` | `0.1` / `10.0` (`0.0` if fireflies are absent) | Check specular highlight energy |
| **Output Format** | `PNG 8-bit` | `PNG 16-bit` | `OPEN_EXR_MULTILAYER` (16-bit float, DWAA/ZIP) or `PNG 16-bit` | `verify_frames.py` magic header |

## 2. When to Raise or Lower Starting Values

- **Interior scenes lit through small windows**: Raise `Diffuse Bounces` to `6` and `Min Adaptive Samples` to `256` on `FINAL` so shadow corners do not starve of rays before the adaptive sampler terminates.
- **Layered glass or liquid vials**: Raise `Transmission Bounces` and `Total Max Bounces` to `16–24`; otherwise total internal reflection turns black.
- **Dense foliage with alpha cards**: Raise `Transparent Max Bounces` to `24–32`; otherwise overlapping leaf cards cast solid black rectangular shadows.
- **4K (`3840 x 2160`) evaluation**: Because 4K has 4x the pixel density of 1080p, fine film grain and denoiser artifacts are smaller on screen; `512–768` max samples at `0.008` noise threshold often matches 1080p `1024` samples, provided the 3-frame benchmark proves total time `<= 3.0 hours`.
