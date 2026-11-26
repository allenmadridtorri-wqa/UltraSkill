---
name: 12-materials-lighting
description: >-
  Physically based materials, surface imperfections, physical lighting rigs,
  volumetric atmosphere, AgX color management, and film-finish compositing for
  Blender Cycles OptiX. Follows the Section 4 Render Standard.
---

# 12-Materials-Lighting: PBR Shading, Motivated Light & AgX

Photorealistic rendering comes from energy-conserving materials with believable surface history lit by motivated physical light sources under the **AgX** view transform—never from flat ambient fill or constant-roughness shaders.

## When to use

Load this skill whenever building Cycles Principled BSDF materials, layering wear/dirt/fingerprints, configuring subsurface scattering or refractive glass/water, setting up studio or architectural lighting, adding volumetric haze, or configuring AgX color management and film-finish compositing.

## Inputs

- Clean metric-scale geometry from `11-modeling` (`mesh_linter.py` passing).
- `SHOT_LIST.md` camera angles and lighting ratios from `10-art-direction`.

## Steps

1. **Build Energy-Conserving PBR Shaders**:
   - Follow [`references/pbr-energy-conservation.md`](references/pbr-energy-conservation.md): keep dielectric base color luminance inside `[0.04, 0.80]`, keep metallic binary (`0.0` or `1.0`), set physical IOR values, and ensure all Roughness/Metallic/Normal textures use `Non-Color`.
2. **Layer Surface Imperfections Into Roughness & Micro-Normals**:
   - Follow [`references/roughness-and-imperfections.md`](references/roughness-and-imperfections.md): modulate every visible surface's roughness across at least a `+-0.06` range using fingerprints, wipe streaks, cavity dust (`Ambient Occlusion`), and edge wear (`Bevel` / `Pointiness`).
3. **Configure Translucent & Refractive Materials Correctly**:
   - **Skin, wax, marble, foliage**: Use `Random Walk` subsurface scattering scaled to meters; see [`references/subsurface-scattering.md`](references/subsurface-scattering.md).
   - **Glass, lenses, liquids**: Model wall thickness and liquid meniscus overlap, and enable shadow caustics or architectural glass ray switches where appropriate; see [`references/glass-water-and-caustics.md`](references/glass-water-and-caustics.md).
4. **Place Motivated Physical Lights (Zero Flat Fill)**:
   - Follow [`references/physical-lighting-rigs.md`](references/physical-lighting-rigs.md) and [`references/hdri-and-sun-sky.md`](references/hdri-and-sun-sky.md) (or run [`scripts/setup_studio_lighting.py`](scripts/setup_studio_lighting.py)).
   - Turn off unmotivated uniform gray world light. Every light must have physical area dimensions (`>= 0.05 m`), a Blackbody Kelvin temperature (`2700 K–9000 K`), and a clear motivation (window, sun, softbox, practical lamp). Use bounce cards or indirect GI for fill and dark flags for negative fill.
5. **Add Restrained Volumetric Atmosphere (When Motivated)**:
   - Follow [`references/atmosphere-and-volumetrics.md`](references/atmosphere-and-volumetrics.md): bound `Principled Volume` (`density 0.001–0.015`, `anisotropy 0.5–0.7`) to a domain box rather than infinite world space.
6. **Verify Exposure Under AgX & Apply Film Finish in Compositing**:
   - Follow [`references/agx-and-color-pipeline.md`](references/agx-and-color-pipeline.md) and [`references/film-finish-compositing.md`](references/film-finish-compositing.md).
   - Run `blender -b scene.blend -P skills/12-materials-lighting/scripts/audit_materials.py` to confirm zero illegal albedos, zero constant-roughness hero materials, and `AgX` active before rendering via `14-blender-pipeline`.

## Numbers and defaults

All values below are **starting values**:

| Parameter | Starting Value | Verification Method |
|---|---|---|
| **Dielectric Albedo Range** | `0.04` (fresh charcoal/tire rubber) to `0.80` (fresh snow/matte paper) | `audit_materials.py` |
| **Metal Albedo Range (`Metallic = 1.0`)** | `0.55 – 0.98` specular tint (Iron `0.56`, Aluminum `0.91`, Gold `[1.0, 0.77, 0.34]`) | `audit_materials.py` |
| **Dielectric IOR** | Water `1.333`, Glass `1.50 – 1.52`, Plastic/Lacquer `1.46`, Skin `1.40` | Principled BSDF `IOR` socket |
| **Roughness Variation Span** | `>= 0.06` spread between min and max roughness on hero surfaces | `audit_materials.py` |
| **Key-to-Fill Luminance Ratio** | `3:1` (natural daylight), `6:1` (dramatic portrait/product), `12:1` (noir/thriller) | AgX False Color check |
| **Color Temperatures (Blackbody)** | Candle `1900 K`, Tungsten `2800 K`, Noon Sun `5400 K`, Overcast/Shade `7000–8500 K` | Light Blackbody node |
| **View Transform** | `AgX` (`AgX - Medium High Contrast` or `None`) | `scene.view_settings.view_transform` |

## Failure modes and fixes

- **White walls or snow blow out into radioactive glowing bounce light**: Albedo is set to `1.0`. Lower white paint albedo to `0.72 – 0.78` and fresh snow to `0.80`.
- **Metal looks like dark gray plastic**: `Metallic` is `0.0` or `0.5`, or the metal has nothing to reflect behind the camera. Set `Metallic = 1.0`, `Roughness = 0.12–0.35`, and place an HDRI or studio softboxes/flags around the object.
- **Shadows are flat milky gray**: World shader has a uniform gray background at strength `1.0`. Set world strength to `0.0` for interiors or use a high-dynamic-range `.exr` HDRI (`12+ EV` dynamic range).

## Done check

- `audit_materials.py` exits with code `0`.
- `scene.view_settings.view_transform == 'AgX'` and zero unmotivated ambient fill exists.
- Rendered `REVIEW` frame passes items 7–20 of `FAKE_3D_CHECKLIST.md`.

## Related files

- [`references/pbr-energy-conservation.md`](references/pbr-energy-conservation.md)
- [`references/roughness-and-imperfections.md`](references/roughness-and-imperfections.md)
- [`references/subsurface-scattering.md`](references/subsurface-scattering.md)
- [`references/glass-water-and-caustics.md`](references/glass-water-and-caustics.md)
- [`references/physical-lighting-rigs.md`](references/physical-lighting-rigs.md)
- [`references/hdri-and-sun-sky.md`](references/hdri-and-sun-sky.md)
- [`references/atmosphere-and-volumetrics.md`](references/atmosphere-and-volumetrics.md)
- [`references/agx-and-color-pipeline.md`](references/agx-and-color-pipeline.md)
- [`references/film-finish-compositing.md`](references/film-finish-compositing.md)
- [`scripts/setup_studio_lighting.py`](scripts/setup_studio_lighting.py)
- [`scripts/audit_materials.py`](scripts/audit_materials.py)
