# Eval 02 — Preemption-Safe 60-Second Cinematic Trailer on Google Colab

## 1. Benchmark Prompt

> "Plan and build the automated rendering and mastering pipeline for a 60-second (`24 fps`) cinematic sci-fi trailer rendered on a Google Colab Tesla T4 GPU with Blender Cycles OptiX. It must survive Colab disconnects without re-rendering finished frames and master to a web-ready MP4 normalized to `-14 LUFS`."

---

## 2. Skills Routed

1. [`skills/14-blender-pipeline/SKILL.md`](../skills/14-blender-pipeline/SKILL.md) (Colab Google Drive mounting, `.exr` magic-byte verification, `--frame-jump` resume)
2. [`skills/15-film-trailer/SKILL.md`](../skills/15-film-trailer/SKILL.md) (3-act `1,440-frame` beat sheet, EBU R128 `-14 LUFS` / `-1.0 dBTP`, FFmpeg `libx264` CRF 16 `+faststart`)

---

## 3. Pass / Fail Grading Rubric (100 Points Total — Pass Threshold `>= 90`)

| Check ID | Criterion | Points | Verification Command / Method |
|---|---|---|---|
| `E02-1` | **Exact 1,440-Frame Continuity**: Shot manifest covers frames `1..1440` (`60.0s @ 24fps`) with zero frame gaps or overlaps | `25` | `python3 examples/02-60s-trailer/generate_trailer_shots.py --self-test` |
| `E02-2` | **Truncated `.exr` Resume Protection**: Frame verifier checks both OpenEXR magic bytes (`76 2f 31 01`) and minimum file size (`>= 32 KB`), deleting partial/corrupt files before resuming | `25` | `python3 skills/14-blender-pipeline/scripts/verify_frames.py --self-test` |
| `E02-3` | **Colab T4 VRAM Budget Compliance**: Every shot stays under the `12,500 MB` safe VRAM ceiling on a 16 GB Tesla T4 | `20` | `python3 skills/14-blender-pipeline/scripts/vram_audit.py --help` |
| `E02-4` | **EBU R128 Audio & x264 Mastering**: FFmpeg mastering command enforces `loudnorm=I=-14.0:TP=-1.0:LRA=11.0`, `-crf 16`, `-pix_fmt yuv420p`, and `-movflags +faststart` | `30` | `python3 examples/02-60s-trailer/master_trailer.py --self-test` |
