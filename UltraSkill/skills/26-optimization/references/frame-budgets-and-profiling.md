# Frame Budgets and Profiling

Never measure game performance in **Average FPS**. Average FPS hides severe stutters: if a game runs at `10 ms` for 59 frames and freezes for `410 ms` on the 60th frame, the 1-second average is still `"60 FPS"`, yet the player experienced a jarring nearly half-second freeze. Always measure in **milliseconds per frame (`ms/frame`)** using **Percentiles (`p50`, `p95`, `p99`, `1% low`)**.

---

## 1. The 16.67 ms Frame Budget Breakdown (60 FPS Target)

| Subsystem | CPU Budget (`ms`) | GPU Budget (`ms`) | Notes |
|---|---|---|---|
| **Input, Gameplay & State Machines** | `2.0 ms` | — | Player controller, combat hitboxes, quests |
| **AI Perception, BT & Pathfinding** | `2.0 ms` | — | Time-sliced across 6 frames (`10 Hz` perception, `4 Hz` pathing) |
| **Physics Simulation & Queries** | `2.5 ms` | — | Broadphase, narrowphase, `move_and_slide`, raycasts |
| **Animation Skinning & Audio** | `1.5 ms` | `1.0 ms` | Disable off-screen bone updates (`VisibilityEnabler3D`) |
| **Scene Culling & Draw Submission** | `3.5 ms` | — | Scales linearly with draw call & node count |
| **Shadow Pass & Depth Pre-Pass** | — | `2.5 ms` | `1` directional shadow map (`1024px` on LOW) |
| **Opaque Geometry & Lighting Pass** | — | `6.5 ms` | Main PBR surface shading |
| **Transparents, Particles & UI** | `1.0 ms` | `3.0 ms` | Alpha blending and HUD composition |
| **Post-Processing & Tonemapping** | — | `1.5 ms` | AgX tonemap; skip SSR/SSAO on LOW preset |
| **OS / Driver Safety Headroom** | `4.17 ms` | `2.17 ms` | Absorbs thermal throttling and OS background scheduling |
| **Total Budget** | **`<= 16.67 ms`** | **`<= 16.67 ms`** | Frame duration = `max(CPU_total, GPU_total)` |

---

## 2. Reproducible Benchmark Camera Track

You cannot compare "Before" and "After" optimizations by running around manually with a mouse. Build a **deterministic 15-second benchmark harness**:
1. Fixed random seed (`seed(1337)`).
2. Automated camera spline + scripted combat stress event (e.g., spawning 12 enemies firing projectiles + 3 explosions at `t = 5.0 s`).
3. Discard the first `60` warmup frames, then record `600` frames (`10 seconds`) of CSV telemetry (`frame_idx,frame_ms,cpu_ms,gpu_ms,draw_calls,primitives,vram_mb`).
