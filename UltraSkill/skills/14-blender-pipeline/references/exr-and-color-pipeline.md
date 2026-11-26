# OpenEXR, AgX Color Pipeline & 16-Bit Intermediates

## 1. Why AgX Replaces Standard sRGB and Filmic

Standard sRGB clips bright highlights at `1.0` brutally, causing neon-saturated rings around lamps, fire, and sun speculars. **AgX** (default in Blender 4.0+) models filmic chroma attenuation: as exposure increases toward specular peak, colors smoothly desaturate toward white just like real camera sensors and photochemical film stock.

### Required Scene Color Settings
```python
scene = bpy.context.scene
scene.display_settings.display_device = "sRGB"
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"  # starting value; use "None" if grading externally
scene.view_settings.exposure = 0.0
scene.view_settings.gamma = 1.0
```

## 2. Linear vs Non-Color Texture Spaces

One of the top 3 causes of fake-looking PBR materials is leaving utility maps in `sRGB`:

| Texture Map Type | Required `image.colorspace_settings.name` | Effect if Wrong (`sRGB` used by mistake) |
|---|---|---|
| Base Color / Albedo / Emission | `'sRGB'` (or `'Linear Rec.709'` for `.exr` textures) | Washed out or overly dark albedo if set to Non-Color. |
| Roughness | `'Non-Color'` | Gamma curve shifts mid-grey `0.5` to `0.21`, making every surface look wet/glossy plastic. |
| Metallic | `'Non-Color'` | Partial metallic transition values corrupt Fresnel reflectance. |
| Normal Map (Tangent Space) | `'Non-Color'` | Normals bend at a 45-degree angle; hard shading seams appear at every UV border. |
| Displacement / Height / AO | `'Non-Color'` | Mid-level `0.5` shifts, inflating meshes across seams. |

Verify every material automatically with `skills/12-materials-lighting/scripts/audit_materials.py`.

## 3. Choosing Between Multi-Layer OpenEXR and 16-Bit PNG

| Format | Codec & Depth | File Size per 1080p Frame (Starting Value) | Best Use Case |
|---|---|---|---|
| `OPEN_EXR_MULTILAYER` | `DWAA` (lossy film-grade) or `ZIP` (lossless), `16-bit Half Float` | `4 MB – 18 MB` (DWAA) / `15 MB – 45 MB` (ZIP) | `FINAL` VFX shots and hero stills requiring post exposure adjustments, Cryptomatte masks, or separate light group relighting. Note: EXR stores scene-linear values before the AgX view transform; apply AgX in the Blender Compositor or OCIO during final deliverable encode. |
| `PNG` (16-bit) | Lossless Deflate, `16-bit RGBA` | `6 MB – 14 MB` | `REVIEW` sequences and `FINAL` trailer shots where Blender's built-in Compositor already applies glare, grain, and the AgX view transform directly into the baked frame for FFmpeg assembly. |
| `PNG` (8-bit) | Lossless Deflate, `8-bit RGBA` | `1.5 MB – 3.5 MB` | `PREVIEW` (`960x540`) layout and blocking checks only. Never use 8-bit PNG for heavy grading (causes sky/volumetric banding). |
