# Memory and VRAM Footprints

On a 4 GB RAM laptop with 1 GB Intel UHD integrated graphics, the "VRAM" is carved directly out of the 4 GB system RAM. Exceeding **`512 MB` GPU VRAM** or **`1,800 MB` total process RAM** triggers OS swap-file thrashing (`200–1,500 ms` freezes) or an immediate WebGL Context Lost / Out-Of-Memory crash.

---

## 1. Exact Texture VRAM Math

Never confuse a PNG's disk file size (`450 KB` compressed on disk) with its uncompressed GPU VRAM footprint. A raw `RGBA8` texture with mipmaps (`1.333x` multiplier) vs hardware block-compressed (`BC7` / `ETC2` at `8 bits per pixel = 1 byte/pixel`):

| Resolution | Uncompressed `RGBA8` + Mipmaps | GPU Compressed (`BC7` / `ETC2`) + Mipmaps | Reduction |
|---|---|---|---|
| `4096 x 4096` (4K) | **`89.47 MB`** per texture | **`22.37 MB`** per texture | **4.0x** (`BC1/ETC1` = `11.18 MB`, **8.0x**) |
| `2048 x 2048` (2K) | **`22.37 MB`** per texture | **`5.59 MB`** per texture | **4.0x** |
| `1024 x 1024` (1K) | **`5.59 MB`** per texture | **`1.40 MB`** per texture | **4.0x** |
| `512 x 512` | **`1.40 MB`** per texture | **`0.35 MB`** per texture | **4.0x** |

### Why 4K Textures Crash 1 GB GPUs
Just **three** assets with uncompressed 4K BaseColor + Normal + ORM textures (`9` textures $\times 89.47\text{ MB}$) consume **`805 MB` of VRAM**—instantly blowing past the 512 MB budget before the framebuffer or shadow maps are even allocated.
- **LOW Preset Rule**: Cap maximum texture dimension to **`1024x1024`** (`512x512` for small props) with GPU block compression enabled (`1.40 MB` per 1K texture).

---

## 2. Render Target & Framebuffer Budgets

Every post-processing effect (Bloom, SSR, SSAO, DOF) allocates full-screen or half-screen floating-point (`RGBA16F = 8 bytes/pixel`) render targets:
- At `1920x1080`, a single `RGBA16F` color buffer + `D24S8` depth buffer costs **`24.8 MB`**. With MSAA 4x and full post-processing chains, render targets alone can exceed **`180 MB`**.
- **LOW Preset Rule**: Render at `1280x720` (or `0.75x` internal scale), disable MSAA (use FXAA or TAA if needed), and disable SSR/SSAO/DOF, keeping total render-target VRAM under **`32 MB`**.

---

## 3. Audio & Mesh Memory Hygiene

- **Audio**: Stream any `.ogg` file longer than `10 seconds` (music, ambient loops) from disk (`stream = true`, buffer `~64 KB` RAM) rather than decoding the full 45 MB uncompressed PCM waveform into RAM.
- **Meshes**: Strip unused vertex attributes (`UV2`, vertex colors, extra bone weights beyond 4 joints/vertex) on export.
