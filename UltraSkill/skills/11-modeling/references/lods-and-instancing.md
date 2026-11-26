# Level of Detail (LODs) & Hardware Instancing

## 1. Instancing: The Secret to Fitting Massive Worlds in T4 15 GB VRAM

In Blender Cycles with OptiX, an **instanced mesh** builds its bounding volume hierarchy (BVH) once in GPU memory. Each additional instance adds only a transform matrix and object header (`< 256 bytes`).

### Three Ways to Instance Correctly in Blender
1. **Linked Duplicate Objects (`Alt+D` / Shared `obj.data`)**:
   ```python
   instance_obj = bpy.data.objects.new("Bolt_Instance_042", master_bolt_obj.data)
   bpy.context.collection.objects.link(instance_obj)
   ```
2. **Collection Instances (`instance_type = 'COLLECTION'`)**:
   Group a complex multi-material asset (e.g., a streetlamp with glass, bulb, and weathered iron pole) into a collection `Asset_Streetlamp`, move it to a hidden master layer, and spawn Empty objects with `empty.instance_type = 'COLLECTION'` and `empty.instance_collection = col`.
3. **Geometry Nodes `Instance on Points`**:
   Keep the `Instance on Points` output wired directly to `Group Output`. **Never append a `Realize Instances` node** unless you specifically need per-vertex deformation on a small foreground patch—realizing 50,000 grass clumps converts 1 instanced BVH into 50 million unique triangles and triggers `CUDA_ERROR_OUT_OF_MEMORY`.

## 2. Level of Detail (LOD) Reduction Ratios

For both large offline environment scenes and realtime Three.js / Godot levels, generate a 4-tier LOD chain:

| LOD Tier | Screen Height Coverage | Triangle Ratio vs `LOD0` | Shader Simplification |
|---|---|---|---|
| `LOD0` | `>= 25%` of screen height | `100%` (Full bevels, bolts, interior detail) | Full PBR + micro-normal + cavity dirt |
| `LOD1` | `10% – 25%` | `50%` (Remove 1-mm fasteners, collapse 3-segment bevels to 1 segment) | Standard PBR (Albedo, Roughness, Normal) |
| `LOD2` | `3% – 10%` | `20%` (Merge sub-parts, bake bevels into normal map) | Albedo + Roughness only (drop tangent normal map) |
| `LOD3` | `< 3%` | `5% – 8%` (Convex hull or crossed billboard planes) | Baked vertex color or single shared atlas |

## 3. Automated Decimation in Python

```python
import bpy

def create_lod_copy(src_obj: bpy.types.Object, lod_index: int, ratio: float) -> bpy.types.Object:
    lod_obj = src_obj.copy()
    lod_obj.data = src_obj.data.copy()
    lod_obj.name = f"{src_obj.name}_LOD{lod_index}"
    bpy.context.collection.objects.link(lod_obj)
    dec = lod_obj.modifiers.new(name=f"Decimate_LOD{lod_index}", type="DECIMATE")
    dec.decimate_type = "COLLAPSE"
    dec.ratio = ratio
    dec.use_collapse_triangulate = True
    return lod_obj
```
