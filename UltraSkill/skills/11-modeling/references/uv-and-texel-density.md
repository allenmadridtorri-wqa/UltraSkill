# UV Unwrapping, Seam Placement & Texel Density

## 1. Seam Placement Discipline

Every UV seam is a potential discontinuity in normal maps, displacement, and anisotropic grain direction. Place UV seams in natural physical breaks:
- Inside `1.0 mm` recessed panel shadow gaps on hard-surface machinery.
- Along actual fabric stitching lines (inner inseam, underarm seam, shoulder yoke) on clothing.
- Along the back/underside away from the primary camera vector in `SHOT_LIST.md`.
- **Anisotropy alignment**: For brushed steel, wood planks, and fabric weave, orient UV islands strictly parallel to the `U` (horizontal) or `V` (vertical) texture axis. Diagonal UV islands cause stair-stepped wood grain and broken anisotropic metal highlights.

## 2. Target Texel Density by Shot Distance (Starting Values)

Texel density measures texture pixels per meter of real-world 3D surface (`px/m`). Mismatched texel density—a crisp `4096 px/m` crate sitting on a blurry `128 px/m` floor—immediately breaks photographic cohesion.

| Asset Role & Camera Distance | Target Texel Density (`px/m`) | Map Size for a `1 m x 1 m` Surface |
|---|---:|---|
| **Macro / Close-up Hero (`< 0.8 m`)** | `4096 – 8192 px/m` | `4096x4096` (or `2x2` 4K UDIM tiles `1001–1004` in Cycles) |
| **First-Person / Hero Midground (`0.8 – 3.0 m`)** | `1024 – 2048 px/m` | `2048x2048` |
| **Environment Architecture (`3.0 – 15.0 m`)** | `512 – 1024 px/m` | `2048x2048` tilable trim sheet + vertex/AO dirt blend |
| **Background / Realtime LOW Preset (`> 15.0 m`)** | `128 – 256 px/m` | `1024x1024` shared atlas |

## 3. Padding & Secondary Lightmap UVs (`UV2`)

- **Island Margin Padding**: Maintain at least `8 px` padding on `2048x2048` maps (`16 px` on `4096x4096`, `4 px` on `1024x1024`) so mipmapping does not bleed background pixels across UV borders at grazing angles.
- **Secondary Lightmap UV (`UVMap_Lightmap`) for Three.js / Godot**:
  - Tiled or overlapping diffuse UVs (`UV0`) cannot store unique baked shadows.
  - When baking Cycles global illumination via `skills/17-realtime-web-scenes/scripts/bake_lightmap_blender.py`, create a second UV layer (`UV1`), pack all islands strictly inside `[0.0, 1.0]` with zero overlaps and `0.008` margin, and bind the baked lightmap texture to `TEXCOORD_1`.
