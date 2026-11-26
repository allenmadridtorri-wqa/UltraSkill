# Offline Cycles OptiX vs Realtime WebGL / Game Engines: Honest Trade-Offs

## 1. The 10,000x Compute Budget Difference

- **Offline Cycles OptiX Frame (Colab Tesla T4)**: `15 to 60 seconds` (`15,000 – 60,000 ms`) of dedicated RT-core path tracing (`256 – 1024` rays per pixel, `8 – 12` bounces, true area-light penumbras, volumetric scattering, and refractive caustics).
- **Realtime WebGL / Godot LOW Frame (1 GB Intel UHD Laptop)**: **`16.67 to 33.33 milliseconds`** on a shared-memory integrated GPU with zero hardware ray-tracing cores.

**Rule**: State plainly to the user what realtime rendering loses compared to offline Cycles, and bake from Cycles wherever static geometry allows.

## 2. Feature Comparison & Bridge Strategy Table

| Visual Feature | Offline Cycles OptiX (Colab GPU) | What Is Lost in Raw Realtime Rasterization | How We Bridge It in Three.js / Godot |
|---|---|---|---|
| **Multi-Bounce Global Illumination & Color Bleed** | Exact path-traced indirect diffuse bounce (`4+` bounces). | Unlit back sides look flat black or uniform ambient gray. | **Bake Cycles Combined Diffuse + AO** onto a non-overlapping secondary UV (`UV1`, [`../scripts/bake_lightmap_blender.py`](../scripts/bake_lightmap_blender.py)) and bind to `material.lightMap`! |
| **Soft Area-Light Shadow Penumbras** | Contact-hardening shadows that blur physically with distance from the caster. | Realtime shadow maps have uniform filter blur (`PCF`) and severe aliasing/peter-panning on 1 GB iGPUs. | Bake all static architectural shadows into the Cycles lightmap; use a cheap soft blob decal shadow under moving characters on `LOW`. |
| **Glossy Specular Reflections** | True inter-object ray-traced reflections. | Objects only reflect the static skybox, not nearby walls or props. | Render a **360-degree Equirectangular Panorama** from the center of the Cycles room and feed it into Three.js `PMREMGenerator` as `scene.environment`. |
| **Subsurface Scattering & Refractive Caustics** | Random Walk volumetric SSS + Manifold caustics. | Too expensive for 1 GB Intel UHD fragment shaders. | Bake static caustic patterns directly into the table/floor lightmap in Cycles; approximate thin-leaf translucency with a back-face `dot(L, -N)` wrap term. |
| **Camera Depth of Field & Film Grain** | True physical lens circle-of-confusion sampling (`1000+` rays). | Full-screen post-processing bokeh shaders halve frame rate on integrated GPUs. | Disable post-processing DOF on `LOW` preset; on `In-Engine Cutscenes` or `Interactive Story Backdrops` (`18-interactive-story`), project Cycles-rendered stills/loops behind realtime 3D hotspots. |
