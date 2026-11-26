# Spatial Audio and Interactive Music

3D spatial audio gives players 360° situational awareness, while interactive music adapts dynamically to tension and combat intensity without jarring cuts.

---

## 1. Anti-Fatigue Variation & Polyphony Caps

Playing the exact same `footstep_stone.wav` sample 4 times per second causes the human ear to hear a robotic comb-filter artifact ("machine-gun effect").

1. **Sample Round-Robin (No Immediate Repeat)**:
   - Store `4–6` distinct recordings per high-frequency action (footsteps, sword swings, bullet impacts).
   - Pick randomly from indices excluding `_last_played_index`.
2. **Per-Trigger Pitch & Gain Jitter**:
   - `pitch_scale = randf_range(0.93, 1.07)` (`±1.2 semitones`).
   - `volume_db = base_db + randf_range(-1.5, 0.5)`.
3. **Polyphony & Cooldown Gate**:
   - Cap identical cues to `max_polyphony = 3` and reject duplicate triggers of the same sound ID that occur within `< 20 ms` of the previous trigger.

---

## 2. 3D Spatial Attenuation & Occlusion

- **Mono Source Requirement**: All 3D positional audio clips (`AudioStreamPlayer3D` / Web Audio `PannerNode`) **must be single-channel Mono** files. Stereo files cannot be pan-localized cleanly in 3D space and consume `2x` RAM.
- **Distance Attenuation Curves**:
  - **Footsteps / Melee**: `unit_size = 2.5 m`, `max_distance = 18.0 m`, inverse distance + high-frequency air absorption (`lowpass cutoff = 18000 Hz -> 3500 Hz` over distance).
  - **Gunfire / Explosions**: `unit_size = 6.0 m`, `max_distance = 65.0 m`.
- **Cheap Raycast Occlusion**:
  - For active 3D emitters within `20 m`, cast a single ray to the listener at `5 Hz` (staggered). If blocked by `WorldStatic`, lower the emitter's low-pass filter cutoff to `1,400 Hz` and attenuate gain by `-5.0 dB`.

---

## 3. Interactive Music Architecture (Vertical Stems + Horizontal Stingers)

1. **Vertical Stem Layering (Synchronized Loops)**:
   - Export 3 time-aligned `.ogg` stems at the exact same BPM and bar length (`e.g., 120 BPM, 16 bars = 32.000 seconds`):
     - `stem_01_ambient_pad.ogg` (Always playing in zone; `0 dB` relative).
     - `stem_02_tension_pulse.ogg` (Fades in over `1.5 s` when enemies enter `Suspicious` alert state).
     - `stem_03_combat_percussion.ogg` (Fades in over `0.4 s` when combat starts; fades out over `3.5 s` on the next bar boundary after the last enemy dies).
2. **Beat-Quantized Stingers**:
   - Track `current_beat = fmod(playback_pos, seconds_per_beat)` so victory or phase-transition stingers fire on the next beat or half-bar subdivision rather than clashing off-beat.
