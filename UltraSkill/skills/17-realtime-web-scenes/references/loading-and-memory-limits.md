# Progressive Loading, Texture Memory Caps & glTF Compression

## 1. The Hidden Cost of PNG/JPG Textures in GPU VRAM

A heavily compressed `4096 x 4096` JPEG file may only weigh `900 KB` over the network, **but the instant WebGL uploads it via `gl.texImage2D()`, it decompresses to a raw `4096 x 4096 x 4 bytes` (`64 MB`) buffer in GPU VRAM**—plus `+33%` (`21.3 MB`) for mipmaps = **`85.3 MB` per 4K texture!**
- Ten 4K textures (`Albedos + Normals + Roughness/Metallic`) consume **`853 MB` of uncompressed VRAM**, instantly exhausting a 1 GB Intel UHD laptop's shared video memory and crashing the browser tab.

## 2. Hard Texture & Geometry Memory Ceilings (Starting Values)

| Resource Tier | `LOW` Preset (4 GB RAM / 1 GB Intel UHD) | `MEDIUM` Preset | `HIGH` Preset |
|---|---|---|---|
| **Max Single Texture Resolution** | `1024 x 1024` (`5.3 MB` w/ mipmaps) | `2048 x 2048` (`21.3 MB` w/ mipmaps) | `2048 x 2048` (`4096` only for single baked atlas) |
| **Total GPU Texture VRAM Budget** | `<= 128 MB` (`256 MB` hard crash limit) | `<= 384 MB` | `<= 768 MB` |
| **ORM Channel Packing (`Occlusion / Roughness / Metallic`)** | Mandatory: pack `AO (R)`, `Roughness (G)`, `Metallic (B)` into **1 shared texture** | Mandatory | Mandatory |
| **KTX2 / Basis Universal GPU Compression** | Optional/Recommended (`UASTC` / `ETC1S` stays compressed at `1/4` to `1/8` size inside VRAM!) | Recommended | Recommended |
| **Max Total `.glb` Download Size** | `<= 15 MB` | `<= 35 MB` | `<= 65 MB` |

## 3. Progressive & Fallback Asset Loading Strategy

1. **Boot the Playable Scene in `< 1.5 Seconds`**:
   - Never block first paint behind a 40 MB `.glb` download spinner.
   - Render the primary room layout, interactive hotspots, and procedural studio lighting immediately on frame 1 using lightweight procedural/instanced geometry or a `< 1.5 MB` core `.glb`, then stream secondary decorative props asynchronously.
2. **Pre-Compile Shaders Before Starting the Camera Intro**:
   - Call `renderer.compile(scene, camera)` during the loading transition so the first camera pan does not stutter for `400 ms` when a new material enters the frustum.
3. **Graceful Asset Error Recovery**:
   - Wrap every `GLTFLoader.load()` call with an `onError` handler that substitutes a clean procedural fallback mesh (`MeshStandardMaterial`) rather than leaving an uncaught Promise rejection or blank black screen.
