# Roughness Variation, Edge Wear & Surface Imperfection Layering

## 1. Why Roughness Carries 80% of Photorealism

In real life, even a brand-new smartphone screen or machined steel block has invisible skin-oil fingerprints, microfiber wipe streaks, settled airborne dust, and oxidized handling marks. Under flat diffuse light these marks are invisible; when a specular highlight rolls across the surface at a grazing angle, those micro-roughness differences immediately appear.

**Rule**: No hero or midground material in UltraSkill may have a single constant float wired into `Principled BSDF -> Roughness`.

## 2. The 4-Layer Imperfection Stack

Build every hero shader's roughness and bump from four physically motivated layers:

| Layer | Physical Cause | Procedural / Texture Driver in Cycles | Effect on Base Shader (Starting Values) |
|---|---|---|---|
| **1. Base Manufacturing Grain** | Machining marks, mold texture, fabric weave, wood pores. | High-frequency tileable map or 3D `Noise Texture` (`Scale = 250 – 1200`, `Detail = 8`). | Sets base roughness (`e.g., 0.22`) and micro-bump (`Bump Distance = 0.00015 m`). |
| **2. Handling & Wipe Smudges** | Human fingers, cleaning rags, rain streaks. | Medium-scale smudge texture or domain-warped `Noise Texture` (`Scale = 12 – 45`, `Roughness = 0.75`). | Shifts roughness upward by `+0.06 to +0.16` in smudged patches. |
| **3. Cavity Dust & Oxidation** | Gravity settles dust onto upward surfaces (`+Z`) and cleaning rags cannot reach deep inside corners. | `Ambient Occlusion` node (`Distance = 0.03 m`, `Inside = False`) blended with `Geometry -> Normal dot (0,0,1)`. | Raises roughness in crevices to `0.55 – 0.75`, lowers metallic to `0.0` where thick dust sits, and shifts base color toward neutral dust `[0.28, 0.26, 0.24]`. |
| **4. Exposed Edge Wear** | Friction scrapes paint/anodization off sharp outer corners first. | `Bevel` node (`Radius = 0.003 m`) dot-producted with `Geometry -> Normal`, multiplied by a breakup `Noise Texture` so wear is intermittent, not a uniform white outline. | Reveals underlying raw metal (`Metallic = 1.0`, `Roughness = 0.15 – 0.25`) or chipped primer on `15% – 35%` of exposed corners. |

## 3. Keep Bump Distances Microscopic

The single most common beginner mistake with the Cycles `Bump` node is leaving `Distance = 1.0` (1 full meter of virtual relief!) and lowering `Strength` to `0.05`. That still produces ugly black normal-termination bands at grazing angles.

- **Correct setup**: Set `Bump -> Distance` to the real physical depth of the scratch in meters (`0.0001 m` = `0.1 mm` for brushed metal or skin pores; `0.001 m` = `1.0 mm` for rough concrete) and keep `Strength` between `0.3` and `0.8` (starting values).
