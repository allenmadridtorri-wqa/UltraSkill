# Example 01 — Hyperrealistic Cycles Studio Still (`BRIEF_AND_BARS.md`)

This golden-master worked example demonstrates how UltraSkill orchestrates **Director (`00`) -> Art Direction (`10`) -> Modeling (`11`) -> Materials & Lighting (`12`) -> Blender Cycles OptiX Pipeline (`14`)** to create a photorealistic macro product still of a **Brushed Titanium & Sapphire Mechanical Chronograph** resting on a wet basalt slab.

---

## 1. Hardware Execution Split

- **Local 4 GB RAM Laptop (1 GB Intel UHD)**:
  - Run `python3 build_still_scene.py --dry-run` or `--self-test` to generate and verify the scene specification JSON (`< 1 second`, `0 MB` GPU VRAM required).
  - Run `python3 audit_still.py --self-test` to audit all 10 photorealism quality bars (`scale`, `bevels >= 0.3 mm`, `PBR albedo bounds [0.02, 0.85]`, `3-point physical lighting`, `AgX High Contrast`, `OptiX GPU enforcement`).
- **Google Colab GPU (`Tesla T4` 16 GB VRAM)**:
  - Run `blender -b -P build_still_scene.py -- --output /content/drive/MyDrive/UltraSkill_Colab_Renders/chrono_still_0001.exr --preset STILL_HIGH` to build the geometry, enable **Cycles + OptiX + OIDN**, and render the 16-bit OpenEXR master.

---

## 2. Camera, Lighting & Material Specification

| Parameter | Exact Value | Skill Reference |
|---|---|---|
| **Subject Dimensions** | `42.0 mm` case diameter (`0.042 m`), `11.5 mm` thickness (`0.0115 m`) | `skills/11-modeling/references/scale-and-bevels.md` |
| **Bevel Radii** | Case lugs: `0.45 mm` (`3` segments); bezel chamfer: `0.25 mm`; basalt slab edge: `1.8 mm` | Zero razor-sharp 0-width CG edges |
| **Camera & Lens** | `85 mm` prime macro lens on `36x24 mm` Full-Frame sensor, `f/4.0`, focus distance `0.28 m` on crown logo | `skills/10-art-direction/references/lens-and-camera.md` |
| **3-Point Motivated Rig** | **Key**: `0.6x0.4 m` softbox at `45°` azimuth, `35°` elevation, `4800 K`, `45 W`<br>**Fill**: `0.9x0.9 m` bounce card at `-50°`, `6000 K`, `9 W` (`5:1` Key:Fill ratio)<br>**Rim**: `0.5x0.12 m` strip light at `155°` backlight, `5600 K`, `65 W` (grazing titanium bevels) | `skills/12-materials-lighting/references/physical-lighting-rigs.md` |
| **PBR Materials** | **Brushed Titanium**: `Metallic = 1.0`, BaseColor `[0.54, 0.53, 0.50]`, `Roughness = 0.24 ± 0.06` (`Anisotropy = 0.65`)<br>**Sapphire Crystal**: `Transmission = 1.0`, `IOR = 1.77`, `Roughness = 0.015`<br>**Wet Basalt Slab**: `Metallic = 0.0`, BaseColor `[0.045, 0.047, 0.050]`, `Roughness = 0.18–0.55` | `skills/12-materials-lighting/references/pbr-energy-conservation.md` |
| **Color & Render Preset** | `AgX` (`AgX - High Contrast`), `STILL_HIGH` (`1024 samples`, adaptive threshold `0.005`, `OPTIX` + `OPENIMAGEDENOISE` Albedo+Normal) | `skills/14-blender-pipeline/references/quality-presets.md` |
