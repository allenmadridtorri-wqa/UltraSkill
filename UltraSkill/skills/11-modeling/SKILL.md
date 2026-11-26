---
name: 11-modeling
description: >-
  3D modeling and geometry engineering skill for Blender Cycles and realtime
  engines. Covers real-world metric scale, bevel standards, hard-surface and
  organic topology, character forms, retopology, UVs and texel density, LODs
  and T4 VRAM instancing, Geometry Nodes scattering, and automated mesh linting.
---

# 11-Modeling: Metric Scale, Bevels, Topology & Instancing

Photorealistic lighting fails on mathematically sharp, out-of-scale geometry. Every mesh in UltraSkill is built in real-world meters, carries physical edge bevels to catch specular highlights, and uses instancing to fit inside Tesla T4 15 GB VRAM or 1 GB Intel UHD web/game budgets.

## When to use

Load this skill whenever blocking environments, modeling hard-surface props, sculpting organic or character forms, unwrapping UVs, generating LODs, building Geometry Nodes scatter setups, or auditing meshes before texturing.

## Inputs

- `SHOT_LIST.md` from `10-art-direction` (camera distances and focal lengths dictate subdivision and bevel density).
- Target runtime (`Offline Cycles OptiX on Colab T4` vs `Realtime Three.js / Godot LOW preset`).

## Steps

1. **Enforce Metric Scale & Applied Transforms**:
   - Follow [`references/scale-and-bevels.md`](references/scale-and-bevels.md): set `scene.unit_settings.system = 'METRIC'` and `scale_length = 1.0`.
   - Apply all object scale and rotation transforms (`Ctrl+A` / `obj.data.transform()`) so `obj.scale == (1.0, 1.0, 1.0)`. Unapplied scale distorts bevel widths and UV unwraps.
2. **Apply Physical Edge Bevels to Every Hard Edge**:
   - No manufactured edge has a `0.0 mm` radius. Add a Bevel modifier (`width = 0.0005 m` to `0.005 m`, `segments = 2` or `3`, `harden_normals = True`) or use the Cycles `Bevel` shader node (`radius = 0.001 m`, `samples = 4`) on distant static background architecture.
3. **Build Clean Topology by Asset Type**:
   - **Hard surface**: Use support loops, quad bevel transitions, and `0.5 mm – 2.0 mm` recessed panel shadow gaps; see [`references/hard-surface-topology.md`](references/hard-surface-topology.md).
   - **Organic & foliage**: Break symmetry and layer macro/meso/micro silhouettes; see [`references/organic-and-foliage.md`](references/organic-and-foliage.md).
   - **Characters & deforming meshes**: Follow anatomical bony landmarks and concentric joint/facial quad loops; see [`references/character-forms.md`](references/character-forms.md) and [`references/retopology-and-deformation.md`](references/retopology-and-deformation.md).
4. **Unwrap UVs to Target Texel Density**:
   - Follow [`references/uv-and-texel-density.md`](references/uv-and-texel-density.md): hide seams along hard back edges, maintain uniform texel density, and pack a second non-overlapping UV map (`UVMap_Lightmap`) when baking Cycles lighting for Three.js/Godot.
5. **Instance Repeated Geometry & Build LODs**:
   - Follow [`references/lods-and-instancing.md`](references/lods-and-instancing.md) and [`references/procedural-geometry-nodes.md`](references/procedural-geometry-nodes.md). Share `obj.data` datablocks or use Geometry Nodes `Instance on Points` with Poisson Disk spacing and rotation/scale jitter.
6. **Run the Headless Mesh Linter**:
   - Execute `blender -b scene.blend -P skills/11-modeling/scripts/mesh_linter.py` and fix every reported scale, normal, manifold, UV, or missing-bevel violation before handing off to `12-materials-lighting`.

## Numbers and defaults

All values below are **starting values**:

| Metric / Parameter | Offline Cycles Hero | Offline Mid/Background | Realtime LOW Preset (4 GB Laptop) |
|---|---|---|---|
| **Scene Unit Scale** | `1.0` (`1 Blender Unit = 1.0 m`) | `1.0 m` | `1.0 m` |
| **Bevel Width (Machined Metal)** | `0.5 mm – 1.5 mm` (`3` segments) | `1.0 mm – 2.0 mm` (`2` segments) | `1.5 mm` (`1` segment + weighted normals) |
| **Bevel Width (Wood / Plastic)** | `1.5 mm – 3.5 mm` (`3` segments) | `2.0 mm – 4.0 mm` (`2` segments) | `2.5 mm` (`1` segment) |
| **Bevel Width (Concrete / Stone)** | `4.0 mm – 12.0 mm` (`3–4` segments + noise) | `5.0 mm – 10.0 mm` (`2` segments) | `6.0 mm` (`1` segment) |
| **Panel Seam Gap / Depth** | `1.0 mm` wide, `2.0 mm` deep | `1.5 mm` wide | Normal map baked from high-poly |
| **Texel Density** | `2048 – 4096 px/m` | `512 – 1024 px/m` | `256 – 512 px/m` |
| **Triangle Budget (per Hero Asset)** | `100k – 800k` tris | `10k – 50k` tris | `1.5k – 8k` tris (`<= 150k` whole scene) |

## Failure modes and fixes

- **Bevel modifier pinches or creates overlapping dark shading spikes**: Object scale is unapplied (`scale != 1,1,1`) or duplicate vertices exist. Apply scale, run Merge by Distance (`0.0001 m`), set Bevel `Limit Method = 'ANGLE'` (`30 deg`), and enable `Clamp Overlap` only during diagnosis.
- **T4 GPU runs out of VRAM on a forest or city scene**: Scatter system realized instances into unique mesh geometry (`Realize Instances` node left connected). Remove `Realize Instances` so Cycles traces true hardware instances.
- **Realtime export drops below 30 FPS on 1 GB Intel UHD laptop**: High-poly Cycles meshes were exported directly to glTF without decimation/normal-map baking. Decimate or retopologize to `< 150,000` total scene triangles and merge static draw calls.

## Done check

- `mesh_linter.py` exits with code `0` (`0` unapplied scales, `0` zero-bevel hero meshes, `0` missing UV maps).
- Repeated props use shared mesh datablocks or collection instances (`vram_audit.py` passes).

## Related files

- [`references/scale-and-bevels.md`](references/scale-and-bevels.md)
- [`references/hard-surface-topology.md`](references/hard-surface-topology.md)
- [`references/organic-and-foliage.md`](references/organic-and-foliage.md)
- [`references/character-forms.md`](references/character-forms.md)
- [`references/retopology-and-deformation.md`](references/retopology-and-deformation.md)
- [`references/uv-and-texel-density.md`](references/uv-and-texel-density.md)
- [`references/lods-and-instancing.md`](references/lods-and-instancing.md)
- [`references/procedural-geometry-nodes.md`](references/procedural-geometry-nodes.md)
- [`scripts/mesh_linter.py`](scripts/mesh_linter.py)
