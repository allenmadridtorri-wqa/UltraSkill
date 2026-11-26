---
name: ultraskill-optimization
description: Frame-time budgeting (16.67 ms for 60 FPS), CPU vs GPU bottleneck isolation, draw-call batching and GPU instancing, shader and overdraw optimization, RAM/VRAM footprint reduction, and frustum/occlusion culling.
---

# 26 — Game & Realtime Optimization

This skill profiles, diagnoses, and optimizes 2D/3D games and realtime scenes so they sustain a locked **60 FPS (`p95 <= 16.67 ms`, `p99 <= 20.0 ms`)** even on the user's baseline **4 GB RAM laptop with 1 GB Intel UHD integrated graphics**.

## When to use

- Profiling frame-time spikes, micro-stutters, or low average frame rates (`< 60 FPS`).
- Determining whether a scene is CPU-bound (script logic, physics, draw-call submission) or GPU-bound (fill-rate/overdraw, fragment shaders, bandwidth, vertex count).
- Reducing draw calls (`<= 150` on LOW, `<= 400` on MEDIUM) via static batching, `MultiMesh` / `InstancedMesh`, and texture atlasing.
- Simplifying heavy fragment shaders, transparent particle overdraw, and real-time shadow cascades.
- Trimming system RAM (`<= 1,800 MB`) and GPU VRAM (`<= 512 MB` on LOW) footprints.
- Implementing frustum, distance, and portal/occlusion culling.

## Inputs

- Frame-time telemetry CSV or JSON capture (`frame_ms`, `cpu_ms`, `gpu_ms`, `draw_calls`, `vram_mb`).
- Target hardware tier (`LOW` 1 GB iGPU @ `720p`, `MEDIUM` @ `1080p`, `HIGH` @ `1080p/1440p`).

## Steps

1. **Measure & Establish Baseline Frame Telemetry**:
   - Never optimize blind. Capture at least `300` consecutive frames during worst-case combat and analyze `mean`, `p50`, `p95`, `p99`, and hitch counts using [references/frame-budgets-and-profiling.md](references/frame-budgets-and-profiling.md) and [scripts/analyze_frame_times.py](scripts/analyze_frame_times.py).
2. **Isolate CPU vs GPU Bottleneck**:
   - Run the **Resolution Halving Test** (`1280x720 -> 640x360`): if frame time drops by `>= 30%`, you are GPU fragment/fill-rate bound; if frame time barely changes, check CPU or vertex/draw-call submission using [references/cpu-vs-gpu-bound-diagnosis.md](references/cpu-vs-gpu-bound-diagnosis.md).
3. **Cut Draw Calls & State Changes**:
   - Merge shared materials into texture atlases and convert repeated props (`>= 5` instances) to `MultiMeshInstance3D` / `InstancedMesh` using [references/draw-calls-and-batching.md](references/draw-calls-and-batching.md).
4. **Eliminate Fill-Rate & Shader Bottlenecks**:
   - Replace procedural noise in fragment shaders with baked channel-packed textures (`ORM`), tighten transparent particle bounds to reduce overdraw (`<= 2.5x`), and cap dynamic shadow lights (`<= 1` directional sun on LOW) using [references/shader-and-overdraw-optimization.md](references/shader-and-overdraw-optimization.md).
5. **Audit Memory & VRAM**:
   - Compress textures (`BC7` / `ETC2`), cap max texture size to `1024px` on LOW, and verify zero per-frame allocations using [references/memory-and-vram-footprints.md](references/memory-and-vram-footprints.md).
6. **Configure Culling & LOD Hysteresis**:
   - Set per-category `visibility_range_end` fade distances and room portals using [references/culling-and-streaming.md](references/culling-and-streaming.md), and document before/after metrics in [templates/PERF_REPORT.md](templates/PERF_REPORT.md).

## Numbers and defaults

| Metric | `LOW` Preset (1 GB Intel UHD, 720p) | `MEDIUM` Preset (1080p) | `HIGH` Preset (Dedicated GPU) |
|---|---|---|---|
| **Frame Time Budget (`p95 / p99`)** | `<= 16.67 ms` / `<= 22.0 ms` (or locked `30 FPS` `33.3 ms` fallback) | `<= 16.67 ms` / `<= 19.0 ms` | `<= 16.67 ms` / `<= 17.5 ms` |
| **Max Draw Calls / Frame** | `<= 150` | `<= 400` | `<= 1,200` |
| **Max Visible Triangles / Frame** | `<= 150,000` | `<= 500,000` | `<= 1,800,000` |
| **Max Shadow-Casting Lights** | `1` Directional (`1024px` single cascade) | `1` Directional (`2048px`) + `2` Local | `1` Directional (`4096px`) + `6` Local |
| **Transparent Overdraw Ratio** | `<= 2.0x` screen area | `<= 3.0x` screen area | `<= 4.0x` screen area |
| **GPU VRAM Budget** | `<= 512 MB` | `<= 1,200 MB` | `<= 3,000 MB` |

## Failure modes and fixes

- **Symptom**: Average FPS is 58, but the game visibly stutters for `90 ms` every time a new enemy fires a plasma weapon for the first time.
  - **Fix**: Synchronous GPU driver shader compilation or lazy `load("res://plasma.tscn")` disk I/O on the main thread. Preload combat prefabs during level load and render a warmup frame with all active combat materials behind the loading curtain.
- **Symptom**: Looking at a small campfire with 40 smoke sprites drops frame rate on Intel UHD from 60 FPS to 22 FPS.
  - **Fix**: Massive alpha overdraw on integrated GPUs (which have severely limited memory bandwidth). Cut particle count from 40 to 12 larger particles, trim transparent quad dead-space tightly around the smoke silhouette, and cap particle screen-space radius.
- **Symptom**: Scene has only 80,000 triangles, yet CPU render thread takes `14 ms`.
  - **Fix**: `80,000` triangles split across `1,800` separate `MeshInstance3D` nodes with unique Material instances (`1,800` draw calls). Share a single material resource and batch static props into `MultiMeshInstance3D`.

## Done check

- [ ] Before/after performance metrics are recorded in `PERF_REPORT.md` with `p50`, `p95`, `p99`, draw calls, and VRAM usage.
- [ ] `LOW` preset runs within `<= 150` draw calls, `<= 150k` triangles, and `<= 512 MB` VRAM.
- [ ] `python3 skills/26-optimization/scripts/analyze_frame_times.py --self-test` exits with code `0`.

## Related files

- [references/frame-budgets-and-profiling.md](references/frame-budgets-and-profiling.md)
- [references/cpu-vs-gpu-bound-diagnosis.md](references/cpu-vs-gpu-bound-diagnosis.md)
- [references/draw-calls-and-batching.md](references/draw-calls-and-batching.md)
- [references/shader-and-overdraw-optimization.md](references/shader-and-overdraw-optimization.md)
- [references/memory-and-vram-footprints.md](references/memory-and-vram-footprints.md)
- [references/culling-and-streaming.md](references/culling-and-streaming.md)
- [templates/PERF_REPORT.md](templates/PERF_REPORT.md)
- [scripts/analyze_frame_times.py](scripts/analyze_frame_times.py)
