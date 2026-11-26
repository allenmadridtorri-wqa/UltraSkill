---
name: 15-film-trailer
description: >-
  Cinematic trailer direction, 60-second beat sheets, previz animatics,
  editorial pacing, sound design and -14 LUFS loudness mastering, shot-to-shot
  color continuity, and FFmpeg sequence assembly. Follows the Section 4 Cycles
  OptiX Render Standard.
---

# 15-Film-Trailer: Story Beats, Editorial Rhythm, Sound & FFmpeg Delivery

A cinematic trailer is an engineered 60-second audiovisual rhythm (`1440 frames` at `24 fps`). Never render 1440 frames of Cycles OptiX before locking the frame-exact cut in a previz animatic and proving a single keyframe still for every shot.

## When to use

Load this skill whenever planning a trailer or short film, writing a beat sheet, locking an animatic edit, designing trailer sound stems, checking shot-to-shot color continuity, or encoding rendered EXR/16-bit PNG sequences with FFmpeg.

## Inputs

- Approved `BRIEF.md` and `SHOT_LIST.md` (`10-art-direction`).
- Rendered image sequences verified on Google Drive via `14-blender-pipeline/scripts/verify_frames.py`.
- Audio master or stem WAV files (`48 kHz, 24-bit`).

## Steps

1. **Lock the 60-Second Beat Sheet (`1440 Frames`)**:
   - Fill out [`templates/TRAILER_BEAT_SHEET.md`](templates/TRAILER_BEAT_SHEET.md) using [`references/trailer-structure.md`](references/trailer-structure.md).
   - Map every shot to exact start/end frame numbers, lens focal length, camera move, and synchronous audio hit so zero un-used handle frames are wasted on Colab T4 GPUs.
2. **Build and Cut the Previz Animatic First**:
   - Follow [`references/storyboard-and-animatic.md`](references/storyboard-and-animatic.md) and [`references/editorial-pacing.md`](references/editorial-pacing.md): render `PREVIEW` (`960x540`) keyframe stills or a stamped headless EEVEE playblast and cut them against the audio scratch track before launching final Cycles lighting.
3. **Approve One Cycles OptiX Still Per Shot & Check Color Continuity**:
   - Render 1 representative hero frame per shot at `REVIEW` (`1920x1080`, AgX) via `14-blender-pipeline`.
   - Run `python3 skills/15-film-trailer/scripts/contact_sheet.py` and follow [`references/color-continuity.md`](references/color-continuity.md) to verify black levels, white balance Kelvin progression, and eye-trace alignment across adjacent shots.
   - Design high-contrast title cards following [`references/title-cards-and-typography.md`](references/title-cards-and-typography.md).
4. **Master the Sound Mix to `-14 LUFS`**:
   - Follow [`references/sound-design-and-stems.md`](references/sound-design-and-stems.md) and verify integrated loudness (`-14.0 LUFS +- 1.0 LU`) and true peak (`<= -1.0 dBTP`) using `python3 skills/15-film-trailer/scripts/loudness_check.py`.
5. **Benchmark & Render Shots on Colab, Then Encode via FFmpeg**:
   - Benchmark 3 frames (`benchmark_scene.py` in `14-blender-pipeline`); if estimated total trailer render time exceeds `3.0 hours`, stop and request user approval.
   - Assemble the verified 16-bit PNG / OpenEXR frames and audio master using `python3 skills/15-film-trailer/scripts/assemble_sequence.py` and [`references/ffmpeg-encoding-pipeline.md`](references/ffmpeg-encoding-pipeline.md).

## Numbers and defaults

All values below are **starting values**:

| Parameter | Starting Value | Verification Method |
|---|---|---|
| **Trailer Duration & Frame Rate** | `60.0 s` @ `24 fps` = `1440 frames` (`12 – 18` distinct shots) | `TRAILER_BEAT_SHEET.md` total frame sum |
| **Act 1 (Cold Hook)** | `0 – 12 s` (`Frames 0001–0288`, `3–4` slow establishing shots, `72–96 f` each) | `trailer-structure.md` |
| **Act 2 (World & Escalation)** | `12 – 38 s` (`Frames 0289–0912`, `6–8` medium/action shots, `48–72 f` each) | `trailer-structure.md` |
| **Act 3 (Rhythmic Climax)** | `38 – 52 s` (`Frames 0913–1248`, `5–7` fast cuts on drum hits, `18–36 f` each + 12f blackout) | `trailer-structure.md` |
| **Act 4 (Title Stinger & Post-Title Beat)** | `52 – 60 s` (`Frames 1249–1440`, title card `120 f` + 1 final reveal shot `72 f`) | `trailer-structure.md` |
| **Audio Loudness Target** | `-14.0 LUFS +- 1.0 LU` integrated, `<= -1.0 dBTP` true peak, `48 kHz` | `loudness_check.py` |
| **Web Master Delivery Codec** | H.264 (`libx264`, `-crf 16`, `-preset slow`, `yuv420p`, `bt709`) + AAC `320 kbps` | `assemble_sequence.py` |

## Failure modes and fixes

- **Rendering 150 frames for a shot that only stays on screen for 36 frames**: Wastes `75%` of Colab T4 GPU quota. Lock the edit in `TRAILER_BEAT_SHEET.md` first and render only the exact cut range plus a `4-frame` (`0.16 s`) safety handle on each end.
- **Jarring jump cuts between shots**: Camera lens focal length and subject distance changed by `< 20%` and `< 30 deg` angle between consecutive shots. Enforce the **30-Degree / 2x-Size Rule** between any two same-subject cuts.
- **Banding in dark volumetric smoke after MP4 compression**: 8-bit PNG intermediates were used without film grain. Render 16-bit PNG / OpenEXR, apply `0.018` 35mm sensor grain in compositing, and encode at `-crf 15..16`.

## Done check

- `TRAILER_BEAT_SHEET.md` accounts for all `1440` frames with zero gaps.
- `contact_sheet.py` tile grid confirms shot-to-shot black floor and Kelvin continuity under AgX.
- `loudness_check.py` confirms `-14 LUFS +- 1 LU` and `<= -1.0 dBTP`.
- `assemble_sequence.py` produces a playable `.mp4` with frame-accurate audio sync.

## Related files

- [`references/trailer-structure.md`](references/trailer-structure.md)
- [`references/storyboard-and-animatic.md`](references/storyboard-and-animatic.md)
- [`references/editorial-pacing.md`](references/editorial-pacing.md)
- [`references/sound-design-and-stems.md`](references/sound-design-and-stems.md)
- [`references/title-cards-and-typography.md`](references/title-cards-and-typography.md)
- [`references/color-continuity.md`](references/color-continuity.md)
- [`references/ffmpeg-encoding-pipeline.md`](references/ffmpeg-encoding-pipeline.md)
- [`templates/TRAILER_BEAT_SHEET.md`](templates/TRAILER_BEAT_SHEET.md)
- [`scripts/assemble_sequence.py`](scripts/assemble_sequence.py)
- [`scripts/contact_sheet.py`](scripts/contact_sheet.py)
- [`scripts/loudness_check.py`](scripts/loudness_check.py)
