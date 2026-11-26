# Example 04 — Realtime WebGL / Three.js Interactive Story Scene (`README.md`)

This golden-master worked example demonstrates how UltraSkill combines **Realtime Web Scenes (`17`)** and **Interactive Story (`18`)** to run a smooth **60 FPS (`<= 16.67 ms`)** interactive 3D narrative scene (*"The Observatory Vault"*) directly on the user's **4 GB RAM laptop with 1 GB Intel UHD integrated graphics**.

---

## 1. Low-Spec Hardware & Preset Compliance

| Parameter | `LOW` Preset Default (1 GB Intel UHD) | `MEDIUM` Preset | `HIGH` Preset |
|---|---|---|---|
| **Device Pixel Ratio (`DPR`)** | Clamped to `1.0` (`1280x720`) | Clamped to `1.25` | Clamped to `1.5` |
| **Draw Calls / Frame** | **`4`** (1 Instanced Pillar Ring + 3 Hero Props) | `6` | `8` |
| **Visible Triangles** | **`18,400`** (`<= 150,000` budget) | `18,400` | `36,800` |
| **Estimated GPU VRAM** | **`28.5 MB`** (`<= 512 MB` budget) | `64 MB` | `140 MB` |
| **Shadows & Post-Processing** | Baked AO + `1` `1024px` directional shadow; zero SSR/DOF | `2048px` shadow | `2048px` shadow + bloom |

---

## 2. Interactive Story Features Included

1. **Zero-Allocation Render Loop**: Module-scoped scratch vectors (`_tmpVec3`, `_tmpTarget`) prevent Garbage Collection hitches inside `requestAnimationFrame`.
2. **Branching Story Graph + Rewind Stack**: 5 narrative nodes (`n_start`, `n_inspect_astrolabe`, `n_insert_lens`, `n_align_beam`, `n_vault_opened`) with full state snapshot rewind (`[Rewind Step]` button and `localStorage` persistence).
3. **Camera Choreography**: Exponential decay (`1 - Math.exp(-decay * dt)`) camera transitions between overview and macro inspection viewpoints.
4. **Adaptive FPS Watchdog**: Monitors rolling 60-frame average and automatically steps down to `LOW` preset if frame time exceeds `22.0 ms`.
