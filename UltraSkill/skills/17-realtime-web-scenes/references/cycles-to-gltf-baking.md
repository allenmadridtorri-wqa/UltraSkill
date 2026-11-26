# Baking Cycles Global Illumination to glTF for Three.js

## 1. How Cycles Baking Transfers Offline Realism to a 1 GB Laptop

By baking static direct and indirect lighting in **Blender Cycles OptiX on Google Colab** (`256–512` samples, area light soft shadows, multi-bounce color bleed, and contact ambient occlusion) into a single `1024x1024` or `2048x2048` lightmap texture, the user's 4 GB laptop displays path-traced lighting quality at **60 FPS** using a single texture lookup per fragment.

## 2. Two Baking Architectures

| Method | Best For | Advantages & Trade-Offs |
|---|---|---|
| **1. Separate `UV1` Lightmap + Tiled `UV0` PBR Maps (Recommended)** | Architectural rooms, corridors, interactive story sets. | `UV0` retains crisp tiled 2K wood/concrete albedo, roughness, and normal maps; `UV1` (`UVMap_Lightmap`) holds a single `1024x1024` RGB diffuse GI + AO lightmap applied via `material.lightMap` in Three.js. |
| **2. Combined Full-Bake Atlas (`UV0` Only)** | Self-contained distant props or ultra-low-spec targets. | Bakes Albedo + Direct + Indirect lighting into one `BaseColor` texture applied to `MeshBasicMaterial` (zero runtime lighting math, loses dynamic specular highlights when camera moves). |

## 3. Step-by-Step Cycles Lightmap Bake Pipeline (`bake_lightmap_blender.py`)

1. **Generate Non-Overlapping `UV1` (`UVMap_Lightmap`)**:
   - Keep `UV0` untouched for albedo/normal maps.
   - Add a second UV layer named `UVMap_Lightmap`, set it active, and run `Smart UV Project` (`angle_limit = 66 deg`, `island_margin = 0.015`) across all static architectural meshes packed into a single `[0, 1]` UV square.
2. **Bake Lighting Only (`DIFFUSE` Direct + Indirect, Color OFF)**:
   - Set Cycles Bake Type to `'DIFFUSE'`, enable `use_pass_direct = True`, `use_pass_indirect = True`, and **disable `use_pass_color = False`** so the baked map contains pure incoming irradiance without multiplying the surface's base color twice!
3. **Denoise the Baked Lightmap**:
   - Run the baked image through Blender's `CompositorNodeDenoise` (or `OpenImageDenoise`) so `128-sample` lightmaps become completely noise-free.
4. **Apply in Three.js (`channel = 1`)**:
   ```javascript
   lightmapTexture.channel = 1; // Bind to TEXCOORD_1 (UV1)
   lightmapTexture.flipY = false; // glTF UV convention
   mesh.material.lightMap = lightmapTexture;
   mesh.material.lightMapIntensity = 1.2;
   ```
