# Compositing & Plate Integration: Black Levels, Light Wrap & Grain

## 1. The Four Integration Checks for Composited VFX Elements

Whether combining separate Cycles ViewLayers (e.g., foreground rigid-body debris over a background room plate) or integrating an OpenVDB smoke plume over a live-action/prerendered still, run four quantitative integration checks in the Compositor:

| Check | What Fails When Ignored | Fix & Starting Values |
|---|---|---|
| **1. Black-Level (Toe) & White-Point Match** | An explosion or smoke element with `0.000` black shadows pasted over a hazy room plate whose deepest black is `[0.018, 0.022, 0.028]` looks like a dark cardboard sticker. | Sample the plate's darkest ambient shadow next to the VFX element and lift the element's black floor (`ASC-CDL Offset` or `Mix Max/Add`) to match `[R, G, B]` within `+-0.002`. |
| **2. Optical Defocus & Edge Softness Match** | Razor-sharp 1-pixel CG debris edges sitting over a lens-softened background (`1.2 px` optical point spread). | Pass CG render layers through a subtle `0.4 – 0.8 px` Gaussian soften (`Defocus` node driven by the `Z` depth buffer matching camera f-stop). |
| **3. Exponential Light Wrap** | Bright background sky or fire stops abruptly at the dark silhouette border of a foreground character or pillar instead of scattering around the lens/edge. | Blur the bright background (`Threshold > 1.0`, dual blur `8 px` + `32 px`), mask it by the inverted eroded foreground alpha (`Dilate/Erode = -4 px`, `Blur = 6 px`), and `Add` (`Factor = 0.08 – 0.20`) over the foreground edge. |
| **4. Unified Sensor Grain & Chromatic Dispersion** | Background plate has grain while the CG element on top is denoiser-smooth (or has different grain size). | Denoise all CG layers clean first, composite everything together in scene-linear space, and apply a **single unified 35mm sensor grain pass (`0.015 – 0.025`)** as the very last node before output (`build_compositor_tree.py`). |

## 2. Alpha Premultiplication Discipline

- All Blender Cycles render passes and OpenEXR layers use **Premultiplied (Associated) Alpha** (`alpha_mode = 'TRANSPARENT'`).
- When performing color grading (`ColorBalance`, `Exposure`, `Curves`) on an isolated foreground pass before `Alpha Over`, enable **`Convert Premultiplied`** (unpremultiply -> grade RGB -> re-premultiply by Alpha); otherwise grading darkens or creates glowing white halos along semi-transparent motion-blurred edges.
