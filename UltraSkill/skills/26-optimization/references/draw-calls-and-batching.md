# Draw Calls and Batching

Every draw call requires CPU driver validation and GPU state setup. Submitting 2,000 individual 50-triangle rocks takes **`10x` longer** on the CPU than submitting a single 100,000-triangle terrain mesh.

---

## 1. What Breaks Batching?

Even in engines with auto-batching, a new draw call is forced whenever any of these change between two meshes:
1. **Unique Material Instance**:
   - Calling `mesh.material_override = mat.duplicate()` on 100 enemies so each can flash white on hit creates **100 unique material IDs** and breaks batching.
   - **Fix**: Share a **single** `Material` resource across all 100 enemies and use **Per-Instance Shader Uniforms** (`instance uniform vec4 hit_flash_color` in Godot 4 or `InstancedBufferAttribute` in Three.js) for per-enemy tint and hit flashes.
2. **Multiple Materials per Mesh (Sub-Meshes)**:
   - A sword model exported from Blender with 4 material slots (`Blade`, `Guard`, `Grip`, `Pommel`) costs **4 draw calls** (`8` with shadows!).
   - **Fix**: Bake all 4 surfaces into a single UV layout with a single PBR material (`1` draw call).
3. **Real-Time Shadow Casters**:
   - Every shadow-casting directional cascade or omni light re-renders every `cast_shadow = ON` mesh in its range.
   - **Fix**: Set `cast_shadow = OFF` on small clutter props (`< 0.4 m`), decals, grass, and ceiling tiles.

---

## 2. GPU Instancing (`MultiMeshInstance3D` / `THREE.InstancedMesh`)

Any mesh repeated **`>= 5 times`** in a scene (pillars, modular wall tiles, rocks, trees, bullets, coins) must be rendered via hardware GPU instancing:

| Technique | Draw Calls for 500 Props | CPU Transform Update Cost | Best For |
|---|---|---|---|
| `500 x MeshInstance3D` | `500` (`1,000` with shadows) | High (500 scene tree nodes) | Never use for repeated clutter |
| **Static Merged Mesh** | `1` (`2` with shadows) | Zero (immutable) | Immovable small room geometry (raises VRAM if large) |
| **GPU Instancing (`MultiMesh`)** | `1` (`2` with shadows) | Low (single contiguous float buffer upload) | Modular props, foliage, bullet pools, debris |

### Spatial Chunking for `MultiMesh`
Do not put all 5,000 trees across a `1 km x 1 km` map into a single `MultiMeshInstance3D`—because frustum culling tests the bounding box of the entire `MultiMesh`, looking at 1 tree forces the GPU to process all 5,000 instances. Partition `MultiMesh` groups into **`32m x 32m` spatial grid chunks** so chunks behind the camera are frustum-culled completely.
