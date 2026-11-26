---
name: 17-realtime-web-scenes
description: >-
  Three.js and WebGL realtime 3D scene engineering skill. Covers honest accounting
  of the offline-to-realtime fidelity gap, mandatory LOW preset for 4 GB RAM /
  1 GB Intel UHD laptops, Cycles-to-glTF lightmap baking, instancing, PMREM lighting,
  resource disposal, and glTF budget auditing.
---

# 17-Realtime-Web-Scenes: Three.js, Baked Cycles Lightmaps & LOW Laptop Preset

Realtime WebGL cannot trace multi-bounce path-traced rays like offline Blender Cycles OptiX on a Colab T4. A veteran realtime technical director bridges that gap by baking static global illumination from Cycles into glTF lightmaps and shipping an automatic **LOW preset** that runs smoothly on the user's 4 GB RAM / 1 GB Intel UHD laptop.

## When to use

Load this skill whenever building Three.js or WebGL 3D web experiences, exporting `.glb`/`.gltf` assets from Blender, baking Cycles lightmaps for web viewers, optimizing draw calls and GPU memory, or configuring runtime hardware presets.

## Inputs

- Optimized 3D assets from `11-modeling` (`LOD1/LOD2` topology, secondary `UVMap_Lightmap`).
- Target hardware baseline: **4 GB RAM laptop with 1 GB Intel UHD integrated graphics**.

## Steps

1. **State the Offline-vs-Realtime Contract Plainly**:
   - Follow [`references/offline-vs-realtime-gap.md`](references/offline-vs-realtime-gap.md): record in `BRIEF.md` and `DECISIONS.md` which effects are baked from Cycles (static diffuse GI, ambient occlusion, soft area shadows) and which effects are approximated or disabled in WebGL (caustics, multi-bounce glass, volumetric path tracing).
2. **Implement Hardware Presets (`LOW`, `MEDIUM`, `HIGH`) First**:
   - Load [`templates/quality_presets.json`](templates/quality_presets.json) and [`templates/scene_bootstrap.js`](templates/scene_bootstrap.js) following [`references/hardware-presets-low-to-high.md`](references/hardware-presets-low-to-high.md).
   - Automatically select **`LOW`** whenever `WEBGL_debug_renderer_info` matches `Intel`, `UHD`, `HD Graphics`, `SwiftShader`, `llvmpipe`, or `navigator.deviceMemory <= 4`.
3. **Bake Static Lighting from Blender Cycles to glTF**:
   - Run `blender -b scene.blend -P skills/17-realtime-web-scenes/scripts/bake_lightmap_blender.py` following [`references/cycles-to-gltf-baking.md`](references/cycles-to-gltf-baking.md) so the `LOW` preset displays photorealistic Cycles soft shadows at **zero runtime shadow-map cost**.
4. **Architect Leak-Free Three.js Lifecycle & Instancing**:
   - Follow [`references/threejs-scene-architecture.md`](references/threejs-scene-architecture.md), [`references/instancing-and-draw-calls.md`](references/instancing-and-draw-calls.md), and [`references/lighting-and-pmrem.md`](references/lighting-and-pmrem.md).
   - Use `THREE.InstancedMesh` for repeated props, dispose every geometry/material/texture on scene teardown, handle `webglcontextlost`, and use `THREE.AgXToneMapping` (or `ACESFilmicToneMapping`).
5. **Audit Custom Shaders, Controls & glTF Asset Budgets**:
   - Follow [`references/custom-shaders-and-materials.md`](references/custom-shaders-and-materials.md), [`references/camera-controls-and-raycasting.md`](references/camera-controls-and-raycasting.md), and [`references/loading-and-memory-limits.md`](references/loading-and-memory-limits.md).
   - Run `python3 skills/17-realtime-web-scenes/scripts/gltf_budget_check.py --input scene.glb --preset LOW` to verify triangle, draw-call, and texture byte budgets before shipping.

## Numbers and defaults

All values below are **starting values**:

| Budget Metric | `LOW` Preset (4 GB RAM / 1 GB Intel UHD) | `MEDIUM` Preset (Entry dGPU / M1) | `HIGH` Preset (Desktop RTX / Apple Pro) |
|---|---|---|---|
| **Target Frame Time / FPS** | `<= 33.33 ms` (`>= 30 FPS`) | `<= 16.67 ms` (`60 FPS`) | `<= 16.67 ms` (`60 FPS`) |
| **Device Pixel Ratio (`dpr`)** | `1.0` (hard cap!) | `Math.min(window.devicePixelRatio, 1.5)` | `Math.min(window.devicePixelRatio, 2.0)` |
| **Antialiasing & Post-FX** | `antialias: false`, `0` post-processing passes | `antialias: true`, optional bloom | `antialias: true`, bloom + vignette |
| **Dynamic Shadow Maps** | `0` (`renderer.shadowMap.enabled = false`; use baked Cycles lightmap) | `1` directional shadow map (`1024x1024`) | `1–2` shadow maps (`2048x2048`, PCFSoft) |
| **Max Draw Calls (`renderer.info.render.calls`)** | `<= 50` (`<= 100` hard ceiling) | `<= 150` | `<= 350` |
| **Max Scene Triangles** | `<= 150,000` | `<= 450,000` | `<= 1,200,000` |
| **Max GPU Texture Memory** | `<= 128 MB` (`256 MB` hard ceiling; max `1024px` maps) | `<= 384 MB` (max `2048px`) | `<= 768 MB` |

## Failure modes and fixes

- **Intel UHD laptop runs at 9 FPS on a 2560x1600 HiDPI screen**: `renderer.setPixelRatio(window.devicePixelRatio)` rendered `5120x3200` (`16.3 million` pixels per frame!). Lock `pixelRatio = 1.0` on the `LOW` preset.
- **Browser tab crashes after switching scenes 3 times**: Old `BufferGeometry`, `Material`, and `Texture` allocations were orphaned in GPU VRAM without calling `.dispose()`. Always run recursive disposal on scene unload.
- **Raycast on `pointermove` freezes frame rate**: Raycasting against a 150,000-triangle mesh at 120 Hz mouse-move events stalls the main thread. Raycast only against low-poly invisible bounding-box proxies on a dedicated Three.js Layer (`layer 2`), throttled to `<= 30 Hz`.

## Done check

- `gltf_budget_check.py --preset LOW` exits with code `0`.
- `LOW` preset is automatically selected on integrated GPUs and accessible via a visible UI preset selector.
- `renderer.info.render.calls <= 50` and `renderer.info.memory.textures` stays constant across scene reloads.

## Related files

- [`references/offline-vs-realtime-gap.md`](references/offline-vs-realtime-gap.md)
- [`references/hardware-presets-low-to-high.md`](references/hardware-presets-low-to-high.md)
- [`references/cycles-to-gltf-baking.md`](references/cycles-to-gltf-baking.md)
- [`references/threejs-scene-architecture.md`](references/threejs-scene-architecture.md)
- [`references/instancing-and-draw-calls.md`](references/instancing-and-draw-calls.md)
- [`references/lighting-and-pmrem.md`](references/lighting-and-pmrem.md)
- [`references/custom-shaders-and-materials.md`](references/custom-shaders-and-materials.md)
- [`references/camera-controls-and-raycasting.md`](references/camera-controls-and-raycasting.md)
- [`references/loading-and-memory-limits.md`](references/loading-and-memory-limits.md)
- [`templates/quality_presets.json`](templates/quality_presets.json)
- [`templates/scene_bootstrap.js`](templates/scene_bootstrap.js)
- [`scripts/bake_lightmap_blender.py`](scripts/bake_lightmap_blender.py)
- [`scripts/gltf_budget_check.py`](scripts/gltf_budget_check.py)
