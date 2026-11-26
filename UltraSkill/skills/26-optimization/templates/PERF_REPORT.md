# Performance Optimization Report (`PERF_REPORT.md`)

- **Project / Scene**: `<Project Name - Scene/Arena ID>`
- **Hardware Profile & Preset**: `<e.g., 4 GB RAM Laptop / 1 GB Intel UHD @ 1280x720 - LOW Preset>`
- **Benchmark Scenario**: `<Deterministic 10-second camera spline + 12-enemy combat wave, seed=1337>`
- **Target Budget**: `p95 <= 16.67 ms` (`60 FPS`), `Draw Calls <= 150`, `VRAM <= 512 MB`

---

## 1. Before vs After Telemetry Summary

| Metric | Baseline (Before) | Optimized (After) | Delta / Improvement | Target Budget | Status |
|---|---|---|---|---|---|
| **Median Frame Time (`p50`)** | `24.80 ms` | `11.40 ms` | `-13.40 ms` (`-54.0%`) | `<= 14.00 ms` | PASS |
| **95th Percentile (`p95`)** | `31.20 ms` | `14.90 ms` | `-16.30 ms` (`-52.2%`) | `<= 16.67 ms` | PASS |
| **99th Percentile (`p99` / 1% Low)** | `68.50 ms` | `17.80 ms` | `-50.70 ms` (`-74.0%`) | `<= 22.00 ms` | PASS |
| **Frames `> 16.67 ms` (Dropped)** | `542 / 600` (`90.3%`) | `14 / 600` (`2.3%`) | `-88.0%` | `<= 5.0%` | PASS |
| **CPU Game + Render Thread (`p95`)** | `19.40 ms` | `9.20 ms` | `-10.20 ms` | `<= 12.50 ms` | PASS |
| **GPU Frame Time (`p95`)** | `29.80 ms` | `13.80 ms` | `-16.00 ms` | `<= 14.50 ms` | PASS |
| **Draw Calls / Frame (Peak)** | `640` | `118` | `-522` (`-81.6%`) | `<= 150` | PASS |
| **Visible Triangles / Frame (Peak)** | `420,000` | `124,000` | `-296,000` (`-70.5%`) | `<= 150,000` | PASS |
| **GPU VRAM Used** | `740 MB` | `382 MB` | `-358 MB` (`-48.4%`) | `<= 512 MB` | PASS |
| **System RAM Used** | `2,150 MB` | `1,340 MB` | `-810 MB` (`-37.7%`) | `<= 1,800 MB` | PASS |

---

## 2. Bottleneck Isolation Diagnosis

1. **Resolution Halving Test (`720p -> 360p`)**: Frame time dropped from `24.8 ms` to `18.9 ms` (`-23.8%`), indicating a **mixed GPU Fill-Rate + CPU Draw-Call Submission** bottleneck.
2. **Spike Audit (`p99 = 68.5 ms`)**: Traced to synchronous `instantiate()` and shader compilation when enemy plasma projectiles spawned on frames 120, 240, and 360.

---

## 3. Applied Optimizations (Ranked by Measured Impact)

| # | Optimization Applied | Subsystem Affected | Measured Frame-Time Win (`p95`) |
|---|---|---|---|
| 1 | Converted 380 modular wall/pillar/rock props to chunked `MultiMeshInstance3D` and shared 1 material | CPU Render / Draw Calls (`640 -> 145`) | `-6.80 ms` |
| 2 | Pre-warmed projectile shaders and pooled 64 projectiles + hit sparks in `NodePool` | Eliminated `68.5 ms` `p99` hitches | `-48.0 ms` on `p99` |
| 3 | Compressed textures to `BC7/ETC2`, packed `ORM` maps, and clamped `LOW` preset max texture to `1024px` | GPU Bandwidth & VRAM (`740 MB -> 382 MB`) | `-4.90 ms` |
| 4 | Replaced 36-quad alpha-blended smoke emitters with 10-octagon trimmed particles + disabled small prop shadows | GPU Fill-Rate & Shadow Pass | `-3.10 ms` |
| 5 | Time-sliced enemy vision raycasts (`10 Hz`) and NavMesh pathing (`4 Hz`) across 6 frames | CPU Physics & AI (`5.8 ms -> 1.6 ms`) | `-1.50 ms` |
