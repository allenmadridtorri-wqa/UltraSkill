---
name: 16-vfx
description: >-
  Visual effects and compositing skill for Blender Cycles OptiX: particles,
  debris, Mantaflow smoke/fire/fluids, Voronoi rigid-body destruction,
  volumetric holograms, Multi-Layer EXR AOV passes, and OpenVDB cache budgeting.
---

# 16-VFX: Simulations, Destruction, Volumetrics & Multi-Pass Compositing

Photorealistic VFX fail when low-resolution simulation grids, weightless particles, or un-integrated glowing elements are slapped onto a scene without lighting interaction or disk cache budgeting.

## When to use

Load this skill whenever building particle systems (sparks, rain, dust motes), Mantaflow smoke/fire/fluid simulations, rigid-body fracture/destruction, procedural volumetric holograms, or multi-layer OpenEXR compositing graphs.

## Inputs

- Lit and scaled 3D scene from `11-modeling` and `12-materials-lighting` (`1.0 unit = 1.0 m`, `AgX` active).
- Google Drive cache path and Tesla T4 15 GB VRAM budget (`14-blender-pipeline`).

## Steps

1. **Estimate Voxel & Cache Footprint Before Baking**:
   - Never click Bake on the 4 GB local laptop or an un-budgeted Colab session.
   - Run `python3 skills/16-vfx/scripts/sim_budget_estimator.py` and follow [`references/simulation-cache-management.md`](references/simulation-cache-management.md) to verify OpenVDB voxel counts, RAM requirements, and Google Drive disk usage.
2. **Author Physical Particle Systems & Debris**:
   - Follow [`references/particles-and-debris.md`](references/particles-and-debris.md): instance real 3D bevelled debris chunks (`Instance on Points`), enable air drag (`0.15 – 0.40`), vary particle mass/scale across a power-law distribution, and enable Cycles Motion Blur (`shutter = 0.5`) so fast sparks render as natural exposure streaks.
3. **Simulate Smoke, Fire & Liquids (When Budgeted)**:
   - Remember from `10-art-direction` that **close-up fire and open water are among the hardest CG subjects**.
   - Follow [`references/smoke-and-fire.md`](references/smoke-and-fire.md) and [`references/fluids-and-splashes.md`](references/fluids-and-splashes.md): use Adaptive Domains, temperature-driven Blackbody volume emission under AgX, and FLIP whitewater secondary particles; bake `.vdb` caches directly to Google Drive before rendering.
4. **Fracture & Simulate Rigid-Body Destruction**:
   - Follow [`references/destruction-and-rigid-bodies.md`](references/destruction-and-rigid-bodies.md): use clustered Voronoi fracture with a distinct inner-face material, keep fractures deactivated (`Start Deactivated = True`) until impact frame, and emit micro-debris and dust at breaking constraints.
5. **Build Physical Holograms & Energy Emitters**:
   - Follow [`references/holograms-and-energy.md`](references/holograms-and-energy.md): use volumetric and Fresnel-attenuated shaders that actually cast interactive bounce light onto nearby hands, visors, and tables.
6. **Configure Multi-Layer EXR AOVs & Compositor Integration**:
   - Run `blender -b scene.blend -P skills/16-vfx/scripts/setup_vfx_passes.py` and `build_compositor_tree.py` following [`references/render-passes-and-aovs.md`](references/render-passes-and-aovs.md) and [`references/deep-compositing-and-integration.md`](references/deep-compositing-and-integration.md).

## Numbers and defaults

All values below are **starting values**:

| VFX System | Starting Parameter Values | Verification Method |
|---|---|---|
| **Mantaflow Smoke/Fire Resolution** | `64 – 96` (blocking), `192 – 256` (`FINAL` hero plume, Adaptive Domain ON) | `sim_budget_estimator.py` |
| **Fire Blackbody Temperature** | `1600 K` (outer soot rim) to `3800 K` (hot core), `Blackbody Intensity = 1.0 – 3.5` under AgX | AgX False Color check |
| **Volume Step Rate (Render)** | `1.0` (`0.5` for dense detailed hero smoke; `2.0` for distant haze) | `scene.cycles.volume_step_rate` |
| **FLIP Fluid Resolution** | `96` (blocking), `180 – 256` (`FINAL`, `time_scale = 1.0`, substeps `2–6`) | `sim_budget_estimator.py` |
| **Rigid-Body Solver Steps** | `120 – 240` substeps per second, `20 – 40` constraint solver iterations | `scene.rigidbody_world.substeps_per_frame` |
| **Spark / Ember Motion Streak** | Velocity `4.0 – 14.0 m/s`, `shutter = 0.5` (`1/48 s`), Blackbody `2200 K – 3400 K` | 1-frame `REVIEW` render with motion blur |

## Failure modes and fixes

- **CG fire looks like a neon yellow-orange cartoon blob**: View transform is `Standard sRGB` or emission is a flat orange RGB color. Switch view transform to **AgX** and drive `Principled Volume -> Blackbody Intensity` and `Temperature` from the `flame` / `temperature` attribute so hot cores desaturate naturally while edges cool to deep crimson and dark soot.
- **Fractured wall explodes on Frame 1 before the projectile hits**: Rigid bodies overlap by `0.5 mm` or lack deactivation. Set collision shape to `CONVEX_HULL` with `Margin = 0.0005 m` (`0.5 mm`) and enable `Deactivation -> Start Deactivated`.
- **Colab disk fills up during OpenVDB bake**: Uncompressed 320-division fluid cache exceeds `25 GB`. Run `sim_budget_estimator.py` first, enable Adaptive Domain, and set OpenVDB compression to `BLOSC` or `ZIP` (`16-bit Half Float`).

## Done check

- `sim_budget_estimator.py` confirms cache disk size `< 8.0 GB` (starting value) and RAM `< 10.0 GB`.
- All physics/VDB caches are baked to Google Drive before `render_sequence.py` starts.
- `setup_vfx_passes.py` and `build_compositor_tree.py` execute cleanly (`exit code 0`).

## Related files

- [`references/particles-and-debris.md`](references/particles-and-debris.md)
- [`references/smoke-and-fire.md`](references/smoke-and-fire.md)
- [`references/fluids-and-splashes.md`](references/fluids-and-splashes.md)
- [`references/destruction-and-rigid-bodies.md`](references/destruction-and-rigid-bodies.md)
- [`references/holograms-and-energy.md`](references/holograms-and-energy.md)
- [`references/render-passes-and-aovs.md`](references/render-passes-and-aovs.md)
- [`references/deep-compositing-and-integration.md`](references/deep-compositing-and-integration.md)
- [`references/simulation-cache-management.md`](references/simulation-cache-management.md)
- [`scripts/setup_vfx_passes.py`](scripts/setup_vfx_passes.py)
- [`scripts/build_compositor_tree.py`](scripts/build_compositor_tree.py)
- [`scripts/sim_budget_estimator.py`](scripts/sim_budget_estimator.py)
