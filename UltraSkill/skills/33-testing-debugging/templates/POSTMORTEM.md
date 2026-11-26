# Blameless Technical Postmortem (`POSTMORTEM.md`)

- **Incident / Defect ID**: `INC-2026-007`
- **Title**: `<Concise Summary — e.g., Colab Batch Render Restart Overwrote Completed Frames Due to Missing Size Check on Truncated .exr>`
- **Severity**: `[x] S0 Blocker/Data Loss | [ ] S1 Major`
- **Date**: `<YYYY-MM-DD>`

---

## 1. Executive Summary & Impact

- **What Happened**: When a Google Colab T4 session disconnected mid-frame on `frame_0142.exr`, Drive flushed a `4 KB` truncated header file. On session resume, the naive `if os.path.exists(frame_path): skip` check treated `frame_0142.exr` as completed, resulting in a corrupt black frame in the final 60s trailer master.
- **Blast Radius**: 1 corrupted frame out of 1,440 (`0.07%`), caught before final client delivery.

---

## 2. Root-Cause Analysis (The 5 Whys)

1. **Why did the final MP4 contain a black flash at 00:05.91?** Because `frame_0142.exr` was only `4,096 bytes` (corrupted header, zero scanline payload).
2. **Why was `frame_0142.exr` only `4,096 bytes`?** Because the Colab VM preempted while Blender was mid-write directly to the final filename `frame_0142.exr`.
3. **Why did the resumed runner skip `frame_0142.exr`?** Because the resume guard checked only `path.exists()` instead of checking minimum valid file size (`>= 32 KB`) and OpenEXR magic bytes (`76 2f 31 01`).
4. **Why did Blender write directly to the final filename?** Because atomic `.tmp -> final` rename or `verify_frames.py` pre-resume scrubbing was not invoked before starting `--frame-jump`.
5. **Why wasn't this caught by unit tests?** Because unit tests only tested missing files (`FileNotFoundError`), not `0-byte` or truncated `4 KB` partial files.

---

## 3. Corrective Actions & Regression Guards

| Action Item | Type | Owner / File | Status |
|---|---|---|---|
| Update `verify_frames.py` and `render_sequence.py` to check OpenEXR magic bytes (`\x76\x2f\x31\x01`) + size `>= 32 KB` | Preventative Fix | `skills/14-blender-pipeline/scripts/verify_frames.py` | DONE |
| Automatically delete truncated/invalid frames before building the resume frame list in `colab_optix_runner.py` | Recovery Guard | `skills/14-blender-pipeline/templates/colab_optix_runner.py` | DONE |
| Add unit test `test_truncated_exr_detected_and_queued_for_rerender` | Regression Test | `skills/33-testing-debugging/scripts/run_test_suite.py` | DONE |
