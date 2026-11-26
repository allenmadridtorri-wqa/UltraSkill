# Architecture & Creative Decisions Log

Record every non-trivial technical or artistic decision so later rounds do not undo validated choices.

## Decision 01: Offline Renderer & Device Selection

- **Date**: `2026-11-26`
- **Context**: User authoring machine has 4 GB RAM and 1 GB Intel UHD graphics. Photorealistic path tracing is required.
- **Options Considered**:
  1. Local CPU path tracing on the laptop.
  2. Realtime WebGL / EEVEE approximation only.
  3. Headless Blender Cycles with NVIDIA OptiX on a Google Colab Tesla T4 GPU, writing frames to Google Drive.
- **Decision**: Option 3 (Blender Cycles with OptiX on Colab GPU, with mandatory `optix_verify.py` proof and 3-frame benchmark).
- **Consequences**: Zero thermal or RAM overload on the laptop; hardware RT core acceleration on T4; requires per-frame Drive persistence and manifest resume to survive Colab session timeouts.

## Decision 02: Local Realtime Fallback Preset

- **Date**: `2026-11-26`
- **Context**: Interactive scenes and games must remain testable on the user's 4 GB RAM / 1 GB Intel UHD laptop.
- **Options Considered**:
  1. Single high-end graphics preset with dynamic shadows and screen-space post-processing.
  2. Tiered `LOW` / `MEDIUM` / `HIGH` presets with `LOW` as the automatic baseline for integrated GPUs.
- **Decision**: Option 2 (`LOW` preset locked to `1280x720`, `pixelRatio = 1.0`, baked lighting, shadows disabled, `<= 100` draw calls, `>= 30 FPS`).
- **Consequences**: Reliable 30+ FPS local execution while preserving optional `HIGH` fidelity on discrete GPUs.
