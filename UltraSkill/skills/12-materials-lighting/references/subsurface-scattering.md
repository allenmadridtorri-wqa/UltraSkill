# Subsurface Scattering (SSS) for Skin, Wax, Marble & Foliage

## 1. Random Walk SSS & Metric Scale Dependency

Cycles `Random Walk` (and `Random Walk (Skin)`) traces actual volumetric scattering paths inside a closed mesh. Unlike old screen-space approximations, `Random Walk` produces accurate red light bleed through thin earlobes, nostrils, wax candle rims, and jade carvings—**provided the mesh is closed manifold and modeled at `1.0 unit = 1.0 meter`**.

In Blender 4.x `Principled BSDF`:
- **`Subsurface Weight`**: Blending factor (`0.0` to `1.0`). Set to `1.0` on skin, wax, and marble, and control the actual scattering distance exclusively via **`Subsurface Scale`** (in meters).
- **`Subsurface Radius` (`[R, G, B]`)**: Relative scattering multiplier per RGB wavelength channel.
- **Effective scatter distance (m)** = `Subsurface Scale * Subsurface Radius`.

## 2. Calibrated SSS Starting Values (Metric Scene `1.0 = 1.0 m`)

| Material | Method | `Subsurface Weight` | `Subsurface Scale` (`m`) | `Subsurface Radius` (`[R, G, B]`) | Roughness & IOR |
|---|---|---:|---:|---|---|
| **Human Facial Skin** | `Random Walk (Skin)` | `1.0` | `0.008 – 0.012` (`8–12 mm` max red path) | `[1.00, 0.35, 0.20]` | `Roughness = 0.28–0.45` (dual-lobe via `Coat Weight = 0.15, Coat Roughness = 0.18`), `IOR = 1.40` |
| **Beeswax / Paraffin Candle** | `Random Walk` | `1.0` | `0.015 – 0.025` | `[1.00, 0.65, 0.32]` | `Roughness = 0.22–0.35`, `IOR = 1.44` |
| **Carrara White Marble / Jade** | `Random Walk` | `1.0` | `0.006 – 0.015` | Marble `[0.85, 0.80, 0.72]` / Jade `[0.35, 0.95, 0.55]` | `Roughness = 0.08–0.20`, `IOR = 1.52` |
| **Whole Milk / Cream** | `Random Walk` | `1.0` | `0.004 – 0.007` | `[1.00, 0.88, 0.70]` | `Roughness = 0.03`, `IOR = 1.35` |
| **Silicone / Soft Rubber** | `Random Walk` | `0.6 – 1.0` | `0.003 – 0.006` | `[0.90, 0.55, 0.45]` | `Roughness = 0.35–0.55`, `IOR = 1.42` |

## 3. Thin Foliage & Paper Translucency

Tree leaves, flower petals, lampshades, and paper sheets are often modeled as thin single-sided shells (`0.2 mm` thick) where volumetric `Random Walk` cannot trace an internal volume:
- For **thin single-sided leaves/petals**: Mix `Principled BSDF` (`75%`) with a `Translucent BSDF` (`25%`) using `Add Shader` or `Mix Shader` driven by leaf vein thickness (veins block transmitted backlight; thin blade tissue transmits warm yellow-green light when backlit by the sun).
- For **thick succulent leaves, aloe, or fruit slices**: Model real thickness (`2–8 mm` closed mesh) and use `Random Walk` SSS (`Scale = 0.005 m`, `Radius = [0.60, 1.00, 0.25]`).

## 4. Diagnosing Common SSS Artifacts

- **Glowing radioactive ears/fingers (wax doll look)**: `Subsurface Scale` is 10x too large (`0.1 m` instead of `0.01 m`) or object scale was not applied (`Ctrl+A`).
- **Dark green/blue fringes along shadow terminators**: `Subsurface Radius` has `G` or `B` higher than `R` on human skin. Human blood hemoglobin absorbs blue/green and scatters red longest (`R > G > B` always on skin).
