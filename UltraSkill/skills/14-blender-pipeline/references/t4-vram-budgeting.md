# Tesla T4 15 GB VRAM Budgeting & Memory Optimization

## 1. The Hard Memory Envelope

A standard Google Colab Tesla T4 GPU provides **15,360 MiB (~15.0 GB)** of physical GDDR6 VRAM. Once Cycles allocates its OptiX BVH acceleration structure, kernel buffers, and render passes (~900 MB to 1.5 GB base overhead), your scene geometry, textures, volumes, and denoiser buffers must stay below **12.5 GB (`12,800 MB` starting value)** to avoid `CUDA_ERROR_OUT_OF_MEMORY`.

## 2. Memory Cost Breakdown & Starting Caps

| Resource Type | Starting Cap per Scene | Unit Cost Formula | How to Verify |
|---|---|---|---|
| **Hero Asset Textures** | Max `4096 x 4096` (`4K`) | 4K RGBA 8-bit = `64 MB` uncompressed in VRAM; 4K RGBA 32-bit float HDRI = `256 MB` | Run [`../scripts/vram_audit.py`](../scripts/vram_audit.py) |
| **Midground Props** | Max `2048 x 2048` (`2K`) | 2K RGBA 8-bit = `16 MB` | `vram_audit.py` |
| **Background / Scatter Props** | Max `1024 x 1024` (`1K`) | 1K RGBA 8-bit = `4 MB` | `vram_audit.py` |
| **Single-Channel Masks (Roughness/Metallic/Bump)** | Pack into R/G/B channels of one image or set to 8-bit Single Channel | Saves `66–75%` texture VRAM compared to separate 4-channel RGBA files | Inspect `bpy.data.images` channels |
| **Subdivision Surface Render Level** | Max level `2` (`<= 3` only for macro displacement hero) | Each Subsurf level multiplies polygon count by `4x` | `vram_audit.py --max-subdiv 2` |
| **Total Unique (Un-instanced) Polygons** | `<= 8,000,000` effective triangles (starting value) | ~180–250 MB per 1M unique triangles in OptiX BVH | `vram_audit.py` |

## 3. High-Leverage VRAM Fixes

1. **Convert Duplicate Objects to Linked Mesh / Collection Instances**:
   - In Python, assign the same `obj.data` datablock (`new_obj.data = master_obj.data`) or use Geometry Nodes `Instance on Points` / Collection Instances.
   - 10,000 instanced trees cost the BVH memory of **1 tree** plus 10,000 4x4 transform matrices (`~640 KB`). 10,000 un-instanced realized trees will crash a T4 immediately.
2. **Cull Out-of-Frustum Scatter**:
   - Configure Geometry Nodes scatter systems to delete points outside the active camera frustum (plus a `1.5 m` shadow/reflection margin, starting value).
3. **Limit Texture Size via Cycles Simplify**:
   - During `PREVIEW` and `REVIEW` passes—or if a third-party scene exceeds 12.5 GB—enable Simplify Texture Limit:
     ```python
     bpy.context.scene.render.use_simplify = True
     bpy.context.scene.cycles.texture_limit_render = "2048"  # or "4096"
     ```
4. **Tighten Volumetric Domain Bounds**:
   - OpenVDB smoke/fire domains allocate memory proportional to $N_x \times N_y \times N_z$. Enable **Adaptive Domain** so empty air voxels are not allocated in VRAM.
