# Example 02 — 60-Second Cinematic Trailer Pipeline (`TRAILER_PLAN.md`)

This golden-master worked example demonstrates how UltraSkill plans, batches, renders on a **Google Colab GPU (`Tesla T4` with Blender Cycles OptiX)**, and masters a **60-second (`1,440 frames @ 24 fps`)** cinematic sci-fi trailer (*"OBELISK: AWAKENING"*).

---

## 1. Three-Act Trailer Beat Structure (`1,440 Frames @ 24.0 FPS`)

| Act | Timecode | Frame Range | Shot Count | Average Shot Length (ASL) | Editorial & Sound Goal |
|---|---|---|---|---|---|
| **Act I: Cold Open & World Establish** | `00:00 – 00:18` | `0001 – 0432` (`432f`) | `4` (`SH010–SH040`) | `4.50 s` (`108f`) | Wide anamorphic establishing shots (`24mm`/`35mm`), low sub-bass drone (`-18 LUFS`), single piano motif |
| **Act II: Escalation & Anomaly** | `00:18 – 00:42` | `0433 – 1008` (`576f`) | `8` (`SH050–SH120`) | `3.00 s` (`72f`) | Tracking push-ins (`50mm`/`85mm`), monolith energy activation, rising braaam + rhythmic percussion |
| **Act III: Rapid Montage, Drop & Title** | `00:42 – 01:00` | `1009 – 1440` (`432f`) | `8` (`SH130–SH200`) | `2.25 s` (`54f`) | Rapid 18–36 frame kinetic cuts, hard `1.5s` audio vacuum cut at frame `1260`, final title card & stinger (`-14.0 LUFS`, `-1.0 dBTP`) |

---

## 2. Colab T4 GPU Batching & Resilience Budget

- **Per-Frame Render Target on Colab T4 (`PROD_1080P`, `1920x1080`, `192 samples` + OptiX + OIDN)**:
  - Average render time: `~4.5 seconds/frame` (`~1.8 hours` total across `1,440` frames).
  - VRAM footprint per shot: `2,400 – 4,800 MB` (well below the **`12,500 MB`** T4 safe ceiling).
- **Preemption-Safe Chunking**:
  - `generate_trailer_shots.py` splits the 20 shots into **20 independent manifest chunks** saved directly to `/content/drive/MyDrive/UltraSkill_Colab_Renders/obelisk_trailer/SH###/frame_####.exr`.
  - If Colab disconnects at frame `0890`, re-running the notebook automatically verifies existing `.exr` files (`size >= 32 KB` + magic bytes) and resumes at frame `0891` with zero wasted GPU minutes.
- **Mastering (`master_trailer.py`)**:
  - Verifies 100% frame continuity (`1..1440`), generates the 2-pass EBU R128 loudness normalization (`I = -14.0 LUFS`, `TP = -1.0 dBTP`) and `libx264` (`CRF 16`, `yuv420p`, `+faststart`) FFmpeg mastering commands.
