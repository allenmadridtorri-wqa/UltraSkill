---
name: ultraskill-ui-audio
description: Game HUD and menu ergonomics, full gamepad/keyboard focus navigation, accessibility standards, hierarchy audio bus mixing with sidechain ducking, 3D spatial audio and interactive music stems, and localization.
---

# 25 — UI, Audio & Accessibility

This skill designs responsive game HUDs, zero-dead-end gamepad/keyboard menus, industry-standard accessibility options, punchy hierarchical audio bus mixing, 3D spatial soundscapes, and overflow-proof localization tables.

## When to use

- Designing HUD layouts, reticle feedback, damage indicators, or pause/inventory/settings menus.
- Implementing full gamepad D-pad/stick and keyboard focus navigation without requiring a mouse cursor.
- Auditing game accessibility (colorblind shape redundancy, scalable subtitles, input remapping, shake/flash reductions).
- Configuring hierarchical audio buses (`Master <- Music / SFX / Voice / Ambience / UI`) with limiters and voice sidechain ducking.
- Setting up 3D spatial audio attenuation, pitch/volume variation pools, or interactive combat music stems.
- Structuring localization string tables (`.csv` / `.json`) with placeholder token validation.

## Inputs

- Gameplay events (`damage_dealt`, `objective_updated`, `pause_state_changed`, `device_changed`) from `skills/21-engine-architecture/`.
- Target resolution baseline (`1280x720` on LOW preset up to `1920x1080` and `16:10` / `21:9` aspect ratios).

## Steps

1. **Lay Out the HUD & Menu Navigation**:
   - Anchor HUD widgets inside a `5%` screen title-safe margin, keep the center `60%` viewport unobstructed during combat, and enforce explicit neighbor focus graphs for gamepad navigation using [references/hud-and-menu-ergonomics.md](references/hud-and-menu-ergonomics.md).
2. **Enforce Accessibility Baseline**:
   - Provide independent sliders (`UI Scale`, `Subtitle Size`, `Camera Shake 0–100%`, `Master/Music/SFX/Voice Volume`), full action remapping, and non-color-only visual cues following [references/game-accessibility.md](references/game-accessibility.md).
3. **Build the Audio Bus Hierarchy & Mixing**:
   - Route every sound cue to an explicit sub-bus (`Music`, `SFX_Combat`, `SFX_World`, `Voice`, `Ambience`, `UI`), place a Brickwall Limiter (`-1.0 dBTP`) on `Master`, and duck `Music` + `SFX` by `-4.5 dB` when `Voice` plays using [references/audio-buses-and-mixing.md](references/audio-buses-and-mixing.md).
4. **Configure Spatial Audio & Interactive Music**:
   - Randomize repeating SFX (`pitch ±0.08`, `volume ±1.5 dB`), cap concurrent identical SFX instances (`max_polyphony = 3`), and crossfade horizontal/vertical music stems on beat boundaries using [references/spatial-audio-and-music.md](references/spatial-audio-and-music.md).
5. **Localize All User-Facing Text**:
   - Externalize all strings into keyed localization tables, allow `+35%` horizontal container expansion for German/French/Spanish translations, and audit placeholders with [references/localization-and-typography.md](references/localization-and-typography.md) and [scripts/check_loc_strings.py](scripts/check_loc_strings.py).

## Numbers and defaults

| Parameter | Default Value | Tolerance / Notes |
|---|---|---|
| HUD Safe Area Margin | `5%` inset (`64 px` horizontal, `36 px` vertical @ 1080p) | Never place text flush against viewport edges |
| Minimum Readable Font Size | `18 px` @ 1080p (`14 px` @ 720p) | Subtitles default `24 px` @ 1080p with `75%` dark backing box |
| Minimum Text Contrast Ratio | `>= 4.5:1` (`>= 7.0:1` over dynamic 3D backgrounds) | Use `2 px` dark outline or semi-opaque backing plate |
| Master Bus Ceiling / Loudness | `-1.0 dBTP` true peak, `-16 LUFS` integrated gameplay | Prevents digital clipping when 5 explosions overlap |
| Default Sub-Bus Levels | `Voice: 0 dB`, `SFX: -3 dB`, `UI: -4 dB`, `Music: -7 dB`, `Ambience: -12 dB` | Keeps dialogue and critical combat cues clear |
| Voice Sidechain Ducking | `-4.5 dB` on `Music` & `-3.0 dB` on `SFX_World` | Attack `30 ms`, Release `350 ms` |
| Repeating SFX Variation | Pitch `0.92–1.08`, Gain `-1.5 to +0.5 dB`, `>= 4` variations | Eliminates "machine-gun ear fatigue" on footsteps/gunfire |

## Failure modes and fixes

- **Symptom**: Opening a modal dialog or closing an inventory submenu loses gamepad focus, leaving the player stuck without a mouse.
  - **Fix**: Push the previously focused `Control` onto a `_focus_stack` when opening a modal, explicitly call `default_button.grab_focus()` on modal open, and restore `_focus_stack.pop_back().grab_focus()` on modal close.
- **Symptom**: White HUD text becomes completely unreadable when the player looks toward a bright sky or snow environment.
  - **Fix**: Never render raw unbordered white text over a 3D viewport. Always add a `2 px` dark stroke/outline (`#0B0D12`) or a `rgba(10, 12, 16, 0.72)` backing container.
- **Symptom**: When three enemies fire shotguns simultaneously, the audio distorts at `+9 dB` and blows out the player's headphones.
  - **Fix**: Set `max_polyphony = 3` per weapon SFX cue, apply a `15 ms` minimum re-trigger cooldown for identical sounds, and attach a Compressor + `-1.0 dBTP` Limiter on the `SFX_Combat` and `Master` buses.

## Done check

- [ ] Every menu screen is 100% navigable via gamepad D-pad/buttons and keyboard alone (focus never escapes to `null`).
- [ ] Settings menu persists independent `Master`, `Music`, `SFX`, and `Voice` volume sliders (mapped logarithmically via `linear_to_db`), camera shake scale, and key/button remapping.
- [ ] All repeating SFX use pitch/volume randomization and polyphony caps (`<= 3–4`).
- [ ] `python3 skills/25-ui-audio/scripts/check_loc_strings.py --self-test` exits with code `0`.

## Related files

- [references/hud-and-menu-ergonomics.md](references/hud-and-menu-ergonomics.md)
- [references/game-accessibility.md](references/game-accessibility.md)
- [references/audio-buses-and-mixing.md](references/audio-buses-and-mixing.md)
- [references/spatial-audio-and-music.md](references/spatial-audio-and-music.md)
- [references/localization-and-typography.md](references/localization-and-typography.md)
- [scripts/check_loc_strings.py](scripts/check_loc_strings.py)
