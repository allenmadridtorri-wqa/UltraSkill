# Shader and Overdraw Optimization

Integrated GPUs (such as the 1 GB Intel UHD baseline) share slow DDR4 system memory with the CPU. Their primary bottleneck is **memory bandwidth and fragment fill-rate (overdraw)**.

---

## 1. Channel Packing (`ORM` Texture Standard)

Never sample 3 separate textures for Ambient Occlusion, Roughness, and Metallic in a fragment shader (`3` separate texture fetches destroy GPU texture cache hit rates). Pack them into a single linear RGB texture (**`ORM`**):
- **R Channel**: Ambient Occlusion (`0.0 = occluded, 1.0 = open`)
- **G Channel**: Roughness (`0.0 = mirror, 1.0 = matte`)
- **B Channel**: Metallic (`0.0 = dielectric, 1.0 = metal`)

One texture fetch (`vec3 orm = texture(orm_map, uv).rgb;`) retrieves all three surface properties in a single cache line.

---

## 2. Fragment Shader Arithmetic Discipline

1. **Move Math from Fragment to Vertex Shader**:
   - At `1280x720` with `2x` overdraw, the fragment shader executes **`1,843,200` times per frame**, whereas a 50,000-vertex scene executes the vertex shader only `50,000` times (`36x` fewer executions). Compute world directions, fog factors, and UV scrolling offsets in `vertex()` and pass them via `varying`.
2. **Ban 3D Procedural Noise in Realtime Fragment Shaders**:
   - Multi-octave 3D Simplex/Voronoi noise in a fragment shader costs `40–120` ALU instructions per pixel. Bake procedural Blender noises into a tiling `512x512` texture lookup instead.
3. **Avoid Dynamic Branching on Non-Uniform Values**:
   - Prefer branchless `mix(a, b, step(edge, x))` and `clamp()` over divergent `if/else` chains inside fragment loops.

---

## 3. Taming Transparent Overdraw

Opaque geometry benefits from the GPU's **Early-Z depth rejection** (front-to-back sorting skips shading occluded background pixels). Transparent (`ALPHA_BLEND`) and carelessly configured `ALPHA_SCISSOR` materials disable or complicate Early-Z:

1. **Trim Particle Quad Dead-Space**:
   - A round smoke puff drawn on a square quad where 55% of the corners have `alpha = 0.0` still pays fragment fill-rate across those invisible corner pixels. Use an 8-vertex octagon cutout mesh tightly hugging the sprite's non-zero alpha boundary.
2. **Prefer `Alpha Scissor` (`alpha_Hash` / `alpha_Clip`) over `Alpha Blend` for Foliage**:
   - Alpha blend (`depth_draw = disabled`) causes sorting artifacts and full overdraw. Use `Alpha Scissor (threshold = 0.5)` for leaves and chain-link fences so they write to the depth buffer.
3. **Screen-Space Particle Size Cap**:
   - Fade out particles when the camera walks within `0.8 m` of an emitter so a single particle quad never covers `100%` of the viewport ten times over.
