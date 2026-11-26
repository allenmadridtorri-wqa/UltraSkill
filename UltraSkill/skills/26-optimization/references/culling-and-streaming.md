# Culling and Visibility Ranges

The fastest polygon is the one never submitted to the GPU. Combine four layers of culling so only visible, in-range geometry is drawn each frame.

---

## 1. The Four Culling Layers

| Layer | How It Works | Cost | Typical Reduction |
|---|---|---|---|
| **1. View Frustum Culling** | Engine tests each mesh's Axis-Aligned Bounding Box (AABB) against the 6 camera frustum planes | Automatic, very cheap (`O(N)` AABB checks) | `60–75%` of world |
| **2. Distance Culling (`visibility_range`)** | Hides small props beyond a designer-specified distance threshold | Near zero | `30–50%` of remaining draw calls |
| **3. Occlusion / Portal Culling** | Skips rooms and corridors blocked by solid walls (`OccluderInstance3D`) | Low (`0.3–0.8 ms` CPU rasterizer) | `50–85%` in indoor/urban levels |
| **4. Animation / Tick Culling (`VisibleOnScreenEnabler3D`)** | Disables `AnimationPlayer` skinning and visual particle ticks when off-screen | Zero | Saves `1.0–3.0 ms` CPU skinning |

---

## 2. Distance Culling Tiers & Hysteresis Margins

Never let a small mug or bolt on a table stay in the draw-call queue when the player is `80 meters` away (where it occupies `< 0.5 pixels`):

| Prop Category | Physical Size | `visibility_range_end` (`LOW` / `HIGH`) | Hysteresis Margin (`end_margin`) |
|---|---|---|---|
| **Micro Detail** (Debris, cups, cables, decals) | `< 0.35 m` | `15 m` / `28 m` | `2.0 m` |
| **Medium Props** (Crates, chairs, barrels, lamps) | `0.35 – 1.5 m` | `35 m` / `65 m` | `4.0 m` |
| **Structural Modules** (Walls, pillars, vehicles) | `1.5 – 8.0 m` | `90 m` / `180 m` | `8.0 m` |
| **Landmarks & Terrain** | `> 8.0 m` | Never distance-culled (switches to `LOD2/LOD3`) | `12.0 m` |

- **Why Hysteresis (`end_margin`) is Mandatory**: Without a `2.0–4.0 m` hysteresis band (`fade_in_dist < fade_out_dist`), a player standing right on the `35.0 m` boundary and breathing/bobbing their camera by `±0.05 m` causes the prop to flicker on and off every frame.

---

## 3. Occluder Placement Rules

1. Place simple low-poly box/quad occluders (`OccluderInstance3D` with `<= 24` triangles) **inside** thick opaque walls, hills, and building shells.
2. Never use high-poly render meshes or grates with holes as occluders.
3. Ensure the occluder mesh is slightly *smaller* (`-0.05 m` inset) than the visual wall mesh so the wall never accidentally self-occludes.
