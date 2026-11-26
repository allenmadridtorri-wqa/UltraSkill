# Project Intake & Constraint Triage

## 1. Purpose

Intake converts a vague prompt ("make a realistic sci-fi corridor trailer" or "build a top-down arena game") into a bounded engineering and artistic contract in `BRIEF.md` before a single polygon, shader, or game loop is written.

## 2. Mandatory Intake Questions (Resolve or Default Explicitly)

When the user's prompt omits parameters, record explicit starting defaults in `BRIEF.md` rather than stalling:

| Dimension | Default Starting Value | How to Verify |
|---|---|---|
| **Primary Medium** | Offline 3D Still / Offline Trailer / Realtime Web 3D / Game Build / CLI-Backend Software | Confirm deliverable file extension (`.exr`/`.png`, `.mp4`, `.html`/`.glb`, `.pck`/`.exe`, `.py`). |
| **Authoring Machine** | 4 GB RAM laptop, 1 GB Intel UHD iGPU | Check that no local process exceeds `1.5 GB` RSS RAM or requires local Cycles/MSVC compilation. |
| **Offline Render Target** | Blender Cycles with OptiX on Google Colab GPU (Tesla T4, 15 GB VRAM) | Verify via `skills/14-blender-pipeline/scripts/optix_verify.py` and `nvidia-smi`. |
| **Realtime Performance Floor** | LOW preset: `>= 30 FPS` (`<= 33.33 ms`), `1280x720`, `pixelRatio = 1.0`, `<= 100` draw calls | Verify with frame-time CSV (`skills/26-optimization/scripts/analyze_frame_times.py`). |
| **Windows Native Builds** | GitHub Actions `windows-latest` runner | Check `.github/workflows/` YAML syntax and artifact upload step. |

## 3. Scope Triage Rules for the Uncanny Five

If the brief requests **close-up digital humans, groom hair, dynamic cloth simulation, open-water splashes, or hero fire**:

1. State plainly in `BRIEF.md` that these five subjects are the hardest in computer graphics to make indistinguishable from photography.
2. Adjust framing and art direction to protect realism and T4 VRAM:
   - Use helmet visors, silhouettes, medium/wide framing (`>= 3.0 m` camera distance, starting value), atmospheric backlight, or hard-surface hero props unless the user explicitly allocates extra simulation rounds and Colab time.
   - Bake any dynamic cloth, smoke, or fluid caches to Google Drive before starting final Cycles frame rendering.

## 4. Non-Goals Declaration

Every `BRIEF.md` must list at least 3 explicit **Non-Goals** (e.g., "No local Cycles rendering on the laptop", "No dynamic global illumination in the LOW WebGL preset", "No multiplayer networking in a single-player vertical slice"). Non-goals prevent scope creep during Rounds 2–5.
