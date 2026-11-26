# Project Brief

- **Project Slug**: `<PROJECT_SLUG>`
- **Primary Pillar**: `3D / Game Development / Software Engineering`
- **Target Deliverable**: `Cycles OptiX Still (.exr/.png) / 60s Trailer (.mp4) / Three.js Scene / Godot Build / CLI Tool`
- **Created UTC**: `2026-11-26`

## 1. Objective & Audience

State in two sentences what the user or viewer experiences and what concrete problem or emotional beat the deliverable solves.

## 2. Hardware & Execution Boundaries

| Execution Environment | Hardware Profile | Assigned Role in This Project |
|---|---|---|
| **Local Authoring Laptop** | 4 GB RAM, 1 GB Intel UHD Graphics | Edit text/scripts, run unit tests and static audits, preview output, run LOW preset (`>= 30 FPS`). |
| **Offline GPU Renderer** | Google Colab NVIDIA Tesla T4 (15 GB VRAM) | Run Blender Cycles with **OptiX**, prove GPU via `nvidia-smi`, benchmark 3 frames, save to Google Drive. |
| **Cloud Build Runner** | GitHub Actions (`windows-latest` / `ubuntu-latest`) | Run automated test suites and compile Windows `.exe` or distribution packages. |

## 3. Deliverable Specifications

- **Resolution / Aspect Ratio**: `1920x1080 (16:9)` (REVIEW/FINAL starting value; `960x540` for PREVIEW)
- **Frame Rate / Frame Count**: `24 fps, 1 frame (Still)` or `24 fps, 1440 frames (60s Trailer)` or `60 Hz fixed physics (Game)`
- **Color Management / Audio Standard**: `AgX View Transform, 16-bit PNG / OpenEXR` and `-14 LUFS integrated loudness`
- **Uncanny Five Risk Subjects Present**: `None` (List any digital humans, hair, cloth, water, or fire and the framing mitigation strategy)

## 4. Explicit Non-Goals

1. Never execute Blender Cycles rendering or heavy native C++/Windows compilation on the 4 GB local laptop.
2. Never ship a realtime scene or game without a verified `LOW` hardware preset.
3. Never proceed past a 3.0-hour estimated Colab render job without explicit user approval.
