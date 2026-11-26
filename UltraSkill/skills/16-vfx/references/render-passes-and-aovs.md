# Multi-Layer OpenEXR Render Passes, Light Groups & AOVs

## 1. Why Multi-Pass EXR Saves Re-Renders

When a `FINAL` frame takes `60 seconds` on a Colab Tesla T4, re-rendering 200 frames because the client or director wants the rim light `+0.5 stops` brighter or the volumetric fog `20%` softer wastes hours. By enabling Multi-Layer OpenEXR passes via [`../scripts/setup_vfx_passes.py`](../scripts/setup_vfx_passes.py), you can relight and re-balance components in the Compositor in `0.2 seconds` per frame.

## 2. Standard VFX Pass Stack (`setup_vfx_passes.py`)

| Pass Category | Cycles ViewLayer Property | Reconstruction / Compositing Equation |
|---|---|---|
| **Diffuse (`Dir + Ind + Col`)** | `use_pass_diffuse_direct/indirect/color = True` | $\text{Diffuse} = (\text{DiffDir} + \text{DiffInd}) \times \text{DiffCol}$ |
| **Glossy (`Dir + Ind + Col`)** | `use_pass_glossy_direct/indirect/color = True` | $\text{Glossy} = (\text{GlossDir} + \text{GlossInd}) \times \text{GlossCol}$ |
| **Transmission (`Dir + Ind + Col`)** | `use_pass_transmission_direct/indirect/color = True` | $\text{Trans} = (\text{TransDir} + \text{TransInd}) \times \text{TransCol}$ |
| **Volume (`Dir + Ind`)** | `cycles.use_pass_volume_direct/indirect = True` | $\text{Volume} = \text{VolDir} + \text{VolInd}$ |
| **Emission & Environment** | `use_pass_emit = True`, `use_pass_environment = True` | Added linearly: $\text{Beauty} = \text{Diffuse} + \text{Glossy} + \text{Trans} + \text{Volume} + \text{Emit} + \text{Env}$ |
| **Cryptomatte (`Object + Material + Asset`)** | `use_pass_cryptomatte_object/material/asset = True` (`levels = 6`) | Pixel-perfect anti-aliased ID mattes for isolating any prop or shader in post. |
| **Utility (`Z`, `Mist`, `Normal`, `Vector`)** | `use_pass_z`, `use_pass_mist`, `use_pass_normal`, `use_pass_vector` | Atmosphere depth grading (`Mist`), post-relighting (`Normal`), 2D motion blur (`Vector`, requires Cycles Motion Blur off if applying in 2D). |

## 3. Light Groups (Zero-Cost Relighting in Post)

Assign each major light tier to a **Light Group** (`Key_Group`, `Fill_Group`, `Rim_Group`, `Practicals_Group`, `VFX_Plasma_Group`):
- Cycles outputs a separate `Combined_<LightGroup>` pass for each group during a single path-traced render.
- Because light transport is linear, adding all Light Group passes together in the Compositor (`Add`) reproduces the exact Beauty render—and multiplying `Combined_VFX_Plasma_Group` by `1.4` or shifting its Kelvin tint adjusts the energy glow on the walls instantaneously without re-rendering!
