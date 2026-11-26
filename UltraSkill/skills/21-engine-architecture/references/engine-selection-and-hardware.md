# Engine Selection & Hardware Realities (4 GB Laptop vs Optional Commercial Engines)

## 1. Why FOSS Engines (Godot 4 Compatibility & Three.js) Are Default

Under Section 3 Hard Constraints:
- The user's authoring laptop has **4 GB system RAM and 1 GB Intel UHD integrated graphics**.
- Default tools must be **free and open source (Godot 4.x, Three.js, Blender, FFmpeg)**.
- **Unreal Engine and Unity are optional**, and their actual hardware demands must be stated plainly whenever discussed.

## 2. Engine Hardware & Workflow Comparison Table

| Engine / Stack | License | Editor Disk & RAM Footprint | Runs on 4 GB RAM / 1 GB Intel UHD Laptop? | Cloud Windows `.exe` CI Build (`GitHub Actions`) |
|---|---|---|---|---|
| **Godot 4.x (`gl_compatibility` OpenGL ES 3 / WebGL 2 mode)** | MIT (FOSS) | `~110 MB` single binary, **`350 – 750 MB` RAM** | **YES (Recommended Native/Web Engine)**. Boots in `< 3 seconds`, exports to Windows/Linux/Web via headless CLI. | Official `abarichello/godot-ci` or portable Godot CLI container (`~2 min` build). |
| **Three.js + Vite / Vanilla ES Modules** | MIT (FOSS) | `~50 MB` `node_modules`, **`250 – 500 MB` browser tab RAM** | **YES (Recommended Browser 3D Engine)** when locked to `LOW` preset (`pixelRatio=1.0`, `<= 50` draw calls). | Zero native compilation needed; static bundle deploys anywhere. |
| **Unity 2022 LTS / Unity 6 (`URP`)** | Commercial Tiered | `8 – 18 GB` editor + Hub + IL2CPP toolchains, **`3.5 – 8.0 GB` RAM** | **NO (Not recommended on 4 GB laptop)**. Unity Editor + background AssetImportWorkers will OOM-thrash a 4 GB system. Requires **`>= 16 GB RAM`** for comfortable authoring. | Requires GameCI (`game-ci/unity-builder`) + Unity license secrets in GitHub Actions. |
| **Unreal Engine 5.x (`Lumen / Nanite`)** | Commercial Royalty | `65 – 120 GB` disk, **`16 – 64 GB` RAM**, **`8+ GB` discrete RTX/RX VRAM** | **NO (Impossible on 4 GB / 1 GB Intel UHD)**. UE5 Editor and ShaderCompileWorkers require a **`32 GB RAM` workstation with an RTX 3060 / RX 6700 (`8–12 GB` VRAM) minimum**. | Requires self-hosted runners or 100+ GB container images. |

## 3. Mandatory `project.godot` Settings for the 4 GB Laptop

Whenever generating a Godot 4 project (`examples/05-godot-micro-game/project.godot`), explicitly lock the renderer to `gl_compatibility` so it never initializes a heavy Vulkan `forward_plus` pipeline on an integrated GPU:

```ini
[rendering]
renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"
anti_aliasing/quality/msaa_3d=0
anti_aliasing/quality/msaa_2d=0
lights_and_shadows/directional_shadow/size=1024
```
