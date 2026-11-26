# Audio Buses and Mixing

Playing every sound effect at `0.0 dB` straight to the master output creates a muddy wall of noise where footsteps drown out dialogue and overlapping explosions clip the DAC.

---

## 1. Canonical 7-Bus Audio Hierarchy

```text
Master (Limiter ceiling: -1.0 dBTP)
├── Voice (Default: 0.0 dB | Sidechain Trigger Source)
├── UI (Default: -4.0 dB | Bypasses pause low-pass filter)
└── WorldMix (Low-Pass Filter enabled when Paused: cutoff 650 Hz)
    ├── SFX_Player (Default: -2.5 dB | Weapons, footsteps, hit confirm)
    ├── SFX_Combat (Default: -3.5 dB | Enemy attacks, explosions; Compressor 3:1)
    ├── SFX_World (Default: -6.0 dB | Doors, physics impacts, props)
    ├── Music (Default: -7.0 dB | Sidechain Ducked -4.5 dB by Voice)
    └── Ambience (Default: -12.0 dB | Wind, room tone, rain loops)
```

---

## 2. Logarithmic Volume Slider Math

Human hearing perceives loudness logarithmically. Binding a `0.0 .. 1.0` UI slider linearly to decibels (`-80 dB .. 0 dB`) makes the bottom 70% of the slider completely silent and crams all usable volume change into the top 15%.

Always convert linear slider values (`slider_val` in `[0.0, 1.0]`) using `linear_to_db()`:

```gdscript
func set_bus_volume_from_slider(bus_name: StringName, slider_val: float) -> void:
	var bus_idx := AudioServer.get_bus_index(bus_name)
	if bus_idx == -1:
		return
	var clamped := clampf(slider_val, 0.0, 1.0)
	if clamped <= 0.001:
		AudioServer.set_bus_mute(bus_idx, true)
	else:
		AudioServer.set_bus_mute(bus_idx, false)
		AudioServer.set_bus_volume_db(bus_idx, linear_to_db(clamped))
```

---

## 3. Sidechain Ducking & Priority Hierarchy

In the middle of combat, only **2–3 sounds** can occupy foreground focus simultaneously:
1. **Tier 1 (Critical Threats & Dialogue)**: Player damage taken, sniper telegraph cue, parry chime, story dialogue (`0.0 to -1.5 dB`).
2. **Tier 2 (Player Actions)**: Player weapon fire, melee hit confirm (`-2.5 to -4.0 dB`).
3. **Tier 3 (Enemy & World Actions)**: Enemy footsteps, distant gunfire, shell casings (`-6.0 to -10.0 dB`).
4. **Tier 4 (Bed)**: Music and environmental ambience (`-7.0 to -14.0 dB`).

When a Tier 1 `Voice` line or critical boss telegraph plays, duck `Music` by **`-4.5 dB`** and `SFX_Combat` / `SFX_World` by **`-3.0 dB`** with a fast `30 ms` attack and smooth `350 ms` release.
