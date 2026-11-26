# Example 03 — Multi-Pass VFX Destruction & Smoke Shot (`VFX_SHOT_SPEC.md`)

This golden-master worked example demonstrates how UltraSkill executes a heavy **Rigid-Body Destruction + Mantaflow Smoke/Fire + Secondary Sparks VFX Shot (`96 frames = 4.0s @ 24 fps`)** within the **16 GB VRAM / 50 GB Disk cache ceiling** of a **Google Colab Tesla T4 GPU**.

---

## 1. Shot Breakdown (*"Reactor Core Pillar Breach"*, `SH_VFX_010`)

- **Duration**: `Frames 1..96` (`4.0 seconds @ 24 fps`), plus **`24` pre-roll warmup frames (`-23..0`)** so ambient dust and heat haze are already established on Frame 1.
- **Simulation Layers**:
  1. **Rigid Body Fracture (`Bullet`)**: Basalt containment pillar pre-fractured into **`140` convex Voronoi chunks** (`0.5 kg – 45 kg`), triggered at Frame `18` (`0.75 s`) by an internal impulse wave.
  2. **Smoke & Fire Plume (`Mantaflow OpenVDB`)**: Domain bounds `4.5m x 4.5m x 6.0m`, resolution divisions **`160`**, adaptive domain enabled, `vorticity = 0.25`, blackbody temperature `4,200 K` core cooling to `1,400 K` ember smoke.
  3. **Secondary Sparks (`Particle / Geometry Nodes`)**: `3,500` incandescent slag sparks emitted from fracture seams with motion blur (`shutter = 0.5`).

---

## 2. Multi-Pass AOV Compositing & Colab T4 Budget

| Budget Metric | Shot Value | Colab T4 Safe Ceiling | Status |
|---|---|---|---|
| **Voxel Count (`160` div on `4.5x4.5x6.0m`)** | `~2.73M` active voxels | `<= 8.0M` voxels | PASS (`34%` of limit) |
| **OpenVDB + Rigid Body Disk Cache (`96 + 24f`)** | `1.42 GB` (`ZIP/Half-Float`) | `<= 15.0 GB` | PASS |
| **Peak Render VRAM (Geometry + VDB + 2K Maps + AOVs)** | `5,840 MB` | `<= 12,500 MB` | PASS (`46.7%` of T4 VRAM) |
| **AOV Render Passes (MultiLayer OpenEXR)** | `Combined`, `DiffDir`, `DiffInd`, `DiffCol`, `GlossDir`, `GlossInd`, `GlossCol`, `Emit`, `VolumeDir`, `Mist`, `Vector`, `CryptomatteObject` | `16-bit Half-Float` (`32-bit` on `Z`/`Vector`/`Crypto`) | PASS |
