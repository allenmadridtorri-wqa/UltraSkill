# Trailer Sound Design, Stem Layering & -14 LUFS Mastering

## 1. Sound Carries 50% of Perceived Visual Realism

A path-traced Cycles OptiX render accompanied by thin, clipping, or absent audio feels flat; the same render paired with textured physical Foley, low-end sub weight, and spatial room tone feels tactile and heavy.

## 2. The 5-Stem Trailer Audio Architecture

Mix trailer audio across five distinct stems before summing to the final stereo (`48 kHz, 24-bit`) master:

| Stem | Frequency Pocket | Core Elements | Mixing & Ducking Rule (Starting Values) |
|---|---|---|---|
| **1. Sub & Low Impacts (`LFE / Boom`)** | `30 Hz – 90 Hz` | Sub-drops (`65 Hz -> 32 Hz` sine pitch sweep), explosion thuds, act-transition booms. | High-pass filter at `28 Hz` (`24 dB/oct`) to protect laptop/phone speakers; mono below `90 Hz`. |
| **2. Percussion & Braams / Hits** | `90 Hz – 2.5 kHz` | Taiko/anvil hits on Act 3 cuts, low brass/synth braams, rhythmic pulse ticks. | Align transient peak (`0 ms`) to the exact first video frame of the cut (`+-0 frames`). |
| **3. Risers & Whooshes (Transitions)** | `250 Hz – 12 kHz` | Pitch/filter risers leading into act breaks (`1.5 – 3.0 s` build), camera pass-by whooshes. | Cut the riser to **absolute silence `2 frames` (`83 ms`) before** the impact boom so the hit punches out of a vacuum. |
| **4. Physical Foley & Hard SFX** | `150 Hz – 16 kHz` | Metallic clicks, servo whirs, footsteps, rain, cloth rustle, glass shatter. | Pan `15% – 45%` L/R to match subject screen X position; adds physical ground truth. |
| **5. Dialogue / VO & Room Tone Bed** | `120 Hz – 8 kHz` (`VO`) + continuous `-38 LUFS` air bed | Narrator/character lines + uninterrupted room/wind tone underneath all cuts. | Sidechain-duck Music/Percussion by `-4.0 dB to -6.0 dB` (`1.5 kHz–4 kHz` pocket) whenever Dialogue is active. |

## 3. EBU R128 / Streaming Loudness Standard (`-14.0 LUFS`)

Verify every final audio/video deliverable using [`../scripts/loudness_check.py`](../scripts/loudness_check.py):
- **Integrated Loudness (`I`)**: **`-14.0 LUFS +- 1.0 LU`** (matches YouTube, Steam, itch.io, and web streaming normalization without platform penalty attenuation).
- **Maximum True Peak (`TP`)**: **`<= -1.0 dBTP`** (prevents inter-sample DAC clipping during AAC/Opus lossy transcoding).
- **Loudness Range (`LRA`)**: `6.0 LU – 12.0 LU` (wide enough that Act 3 climax hits `+4 LU` louder than Act 1 cold hook).
