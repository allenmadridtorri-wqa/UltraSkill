# FFmpeg Sequence Assembly & Mastering Pipeline

## 1. Never Render Direct-to-MP4 Out of Blender Cycles

If a 1440-frame Cycles render writes directly to an `.mp4` container and Google Colab disconnects at frame `1438`, the entire 1438-frame video file has an unclosed MOOV atom and is destroyed. Always render numbered **16-bit PNG (`frame_%04d.png`)** or **OpenEXR (`frame_%04d.exr`)** frames to Google Drive via `render_sequence.py`, verify them with `verify_frames.py`, and run FFmpeg as a final 30-second assembly step (`assemble_sequence.py`).

## 2. Verified FFmpeg Encoding Profiles (Starting Values)

| Deliverable Profile | Codec & Flags | Color & Pixel Format | Audio Flags | Use Case |
|---|---|---|---|---|
| **1. Editorial / Archive Master (`ProRes 422 HQ`)** | `-c:v prores_ks -profile:v 3 -vendor apl0` | `-pix_fmt yuv422p10le -colorspace bt709` | `-c:a pcm_s24le -ar 48000` | Lossless-grade 10-bit master (`.mov`) for editing or archival on Google Drive. |
| **2. Universal Web & Store Delivery (`H.264 High`)** | `-c:v libx264 -crf 16 -preset slow -profile:v high -level 4.2 -movflags +faststart` | `-pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709` | `-c:a aac -b:a 320k -ar 48000` | Plays on 100% of browsers, phones, Discord, Steam, and the user's 4 GB laptop (`~25–45 Mbps` at 1080p). |
| **3. Review Workprint (Burned Timecode)** | `-c:v libx264 -crf 20 -preset fast -vf "drawtext=..."` | `-pix_fmt yuv420p` | `-c:a aac -b:a 192k` | Frame-accurate director review (`ROUNDS.md`) with shot ID and frame number burned into top-left corner. |

## 3. Exact FFmpeg Command Reference

### A. 16-Bit PNG Sequence + WAV Audio -> H.264 Web Master with `-14 LUFS` Normalization
```bash
ffmpeg -y \
  -framerate 24 -start_number 1 -i /content/drive/MyDrive/proj/frames/frame_%04d.png \
  -i /content/drive/MyDrive/proj/audio/trailer_mix.wav \
  -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -af "loudnorm=I=-14:TP=-1.0:LRA=11" \
  -c:a aac -b:a 320k -ar 48000 \
  -shortest -movflags +faststart \
  /content/drive/MyDrive/proj/trailer_final_1080p.mp4
```

### B. Concatenating Per-Shot Sub-Sequences via FFmpeg Concat Demuxer
When shots are rendered into separate directories (`SH-010/frame_%04d.png`, `SH-020/frame_%04d.png`), encode each shot to a 10-bit intermediate or use [`../scripts/assemble_sequence.py`](../scripts/assemble_sequence.py) to validate frame continuity and assemble the master cleanly.
