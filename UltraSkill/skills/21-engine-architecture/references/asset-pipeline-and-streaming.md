# Asset Pipeline and Streaming

An asset pipeline transforms raw authoring files (`.blend`, `.psd`, `.wav`) into compressed, engine-ready runtime artifacts (`.glb`, `.ktx2`, `.ogg`) and streams them into memory without hitching the main thread or exceeding the **512 MB** texture VRAM budget on 1 GB Intel UHD GPUs.

---

## 1. Source vs Runtime Asset Separation

| Asset Category | Authoring Format (Git LFS / Archive) | Runtime Format (Packaged Build) | Compression / Settings |
|---|---|---|---|
| **3D Meshes** | `.blend` | `.glb` / `.scn` | Tangent space baked (`MikkTSpace`), vertex colors quantized, Draco/meshopt optional |
| **Color / Albedo Textures** | 16-bit `.png` / `.tif` (sRGB) | `.ktx2` (BasisU ETC1S / UASTC) or `.dds` (BC7) | Mipmaps generated; `sRGB` flag enabled |
| **Normal / Roughness / Metallic** | 16-bit `.png` (Linear) | `.ktx2` (UASTC) or `.dds` (BC5 / BC7) | Linear color space; normal RG channels in BC5 |
| **UI Sprites / Icons** | `.svg` / `.png` | Packed Texture Atlas (`.png` / `.ktx2`) | Power-of-two atlas (`2048x2048` max), 2px extrusion padding |
| **Music & Ambience (> 10s)** | 24-bit `48kHz` `.wav` | `.ogg` Vorbis / `.opus` | Streamed from disk; `128–160 kbps` stereo |
| **Short SFX (< 3s)** | 24-bit `48kHz` `.wav` | `.wav` (ADPCM) or `.ogg` | Preloaded in RAM; mono for 3D spatialized sounds |

---

## 2. Automated Import Rules (Godot 4 & Custom Pipelines)

### Texture Budget Tiers
Never ship raw 4K PNGs to runtime. Configure import presets per hardware tier:
- **LOW Preset (1 GB VRAM / 4 GB RAM)**:
  - Global texture mipmap bias / skip top mip: clamp max dimension to `1024x1024`.
  - VRAM compression: `ETC2` / `BC7` mandatory; never keep uncompressed `RGBA8` in VRAM for 3D surfaces.
- **MEDIUM Preset**:
  - Max dimension `2048x2048` for hero assets, `1024x1024` for props.
- **HIGH Preset**:
  - Max dimension `4096x4096` for hero characters/weapons, `2048x2048` for environment tiles.

### Mesh Import Checklist
1. **Scale & Orientation**: `1.0 unit = 1.0 meter`, `-Z` forward, `+Y` up.
2. **Collision Generation**: Parse naming suffixes automatically on import:
   - `*_col`: Static trimesh or convex collision shape (hidden from rendering).
   - `*_conv`: Simplified convex hull (`<= 32` vertices).
   - `*_lod0`, `*_lod1`, `*_lod2`: Bind to screen-size LOD thresholds (`100%`, `25%`, `8%`).

---

## 3. Asynchronous Background Streaming

Loading a 15 MB `.glb` synchronously on the main thread freezes the game for `120–400 ms` (7–24 dropped frames).

### Three-Stage Streaming Protocol
1. **Background I/O & Decompression (Worker Thread)**:
   - Use `ResourceLoader.load_threaded_request(path)` in Godot 4 or Web Workers in Three.js.
   - Poll status once per frame (`load_threaded_get_status`) with zero main-thread blocking.
2. **Time-Sliced Instantiation (Main Thread Budget `<= 2.0 ms/frame`)**:
   - Do not instantiate an entire level tree in one frame.
   - Push loaded resources into an instantiation queue and pop items until the frame's streaming timer hits `2.0 ms`.
3. **Shader Warmup & GPU Upload**:
   - Render newly streamed materials on a `1x1` off-screen quad behind a loading curtain or transition zone so driver shader compilation never stalls combat.

---

## 4. Zone Streaming Ring Model

Divide large levels into discrete streaming cells (`64m x 64m` or room-based portals):
- **Active Ring (Distance `0–1` cell)**: Fully loaded, physics active, visible.
- **Preload Ring (Distance `2` cells)**: Threaded load started in background; meshes resident in RAM, physics disabled.
- **Eviction Ring (Distance `>= 3` cells)**: Unreferenced assets freed (`queue_free()`); verify reference count drops to `0` so VRAM is reclaimed.
