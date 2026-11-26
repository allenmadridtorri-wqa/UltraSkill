# CPU vs GPU Bound Diagnosis

Optimizing C#/GDScript loops when your frame is 100% GPU fill-rate bound yields **0.0 ms** improvement. Always run the 4-step bottleneck isolation decision tree first.

---

## 1. The 4-Step Isolation Decision Tree

### Test 1: The Resolution Halving Test (`1280x720 -> 640x360`)
Drop internal render scaling (`scaling_3d_scale` in Godot or `renderer.setPixelRatio(0.5)` in Three.js) to `0.5x` (which cuts pixel count to **25%**):
- **Result A — Frame time drops by `>= 25%`**: You are **GPU Pixel / Fill-Rate Bound** (fragment shader complexity, transparent particle overdraw, post-processing, or memory bandwidth on integrated Intel UHD graphics).
- **Result B — Frame time changes `< 5%`**: Proceed to Test 2.

### Test 2: The Shadow & Geometry Toggle Test
Keep resolution at `0.5x`, disable directional shadows (`shadow_enabled = false`), and hide high-poly meshes:
- **Result A — Frame time drops sharply**: You are **GPU Vertex / Geometry Bound** or **Draw-Call Submission Bound**. Check total visible triangles (`> 150k` on iGPU) and draw calls (`> 150` on LOW).
- **Result B — Frame time remains high**: You are **CPU Game-Thread Bound**. Proceed to Test 3.

### Test 3: Physics vs Script Logic Split
Inspect engine monitors (`TIME_PHYSICS_PROCESS` vs `TIME_PROCESS`):
- **High `TIME_PHYSICS_PROCESS`**: Check active rigid bodies/ragdolls, unmasked `Area3D` overlap queries (`collision_mask = 0xFFFFFFFF`), or un-throttled AI NavMesh/raycast queries.
- **High `TIME_PROCESS`**: Check per-frame allocations, un-pooled `instantiate()`/`queue_free()`, or O(N²) distance loops across entities.

### Test 4: Spike / Hitch Pattern Analysis (`p99 >> p95`)
If `p50` is `11.0 ms` (smooth) but `p99` is `48.0 ms` (stutter):
- **Single-frame spike on first effect spawn**: Shader compilation or synchronous disk load (`load()`).
- **Periodic spike every `3–10 seconds`**: Garbage Collector (GC) sweep triggered by per-frame heap object allocations.
