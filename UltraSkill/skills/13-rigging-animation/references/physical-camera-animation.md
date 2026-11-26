# Physical Camera Animation: Dolly Mass, Fluid Heads & Rack Focus

## 1. Why CG Cameras Feel Weightless

In real filmmaking, a cinema camera body + anamorphic prime lens + matte box + fluid head weighs `8 kg – 18 kg` (`300+ kg` on a dolly track with operator). When a 3D artist animates a single raw Camera object translating and rotating along all 6 degrees of freedom at once, the viewer instantly senses a disembodied flying webcam.

## 2. The 4-Node Physical Camera Rig (`camera_rig_builder.py`)

Always separate camera motion into the same four mechanical axes a real grip crew uses (built automatically by [`../scripts/camera_rig_builder.py`](../scripts/camera_rig_builder.py)):

1. **`RIG_Dolly_Base` (World XY Translation Only)**:
   - Moves only along a straight track vector or smooth ground arc (`Z` locked to floor height).
   - Eased start/stop (`12–24 frames` acceleration ramp to simulate pushing a heavy dolly cart).
2. **`RIG_Crane_Jib` (Parented to Dolly; Vertical Elevation / Boom Arm)**:
   - Controls camera height (`0.15 m` low angle to `3.5 m` jib elevation).
3. **`RIG_Fluid_Head` (Parented to Crane; Pan Z & Tilt X Only)**:
   - Simulates a fluid-damped tripod head. Uses `DAMPED_TRACK` (`Influence = 0.85 – 0.95`) toward `RIG_Aim_Target` so when a fast-moving character darts across the frame, the camera operator lags behind by `3 – 6 frames` (`125 – 250 ms` human reaction time) and slightly overshoots before settling.
4. **`Camera_Body` (Parented to Fluid Head; Dutch Roll Y & Handheld Breathing)**:
   - Holds the F-curve `Noise` modifier simulating operator heartbeat, breathing, or vehicle vibration.

## 3. Handheld & Vehicle Vibration Presets (Starting Values at `24 fps`)

| Camera Mount Mode | Rotation Noise Amplitude (`X / Y / Z` rad) | Noise Scale (`frames`) | Location Noise (`Z` meters) |
|---|---|---|---|
| **Locked Fluid Tripod** | `0.0004 rad` (`0.02 deg`) | `90.0` | `0.000 m` |
| **Shoulder-Mounted Documentary Handheld** | `0.0035 rad` (`0.20 deg` X/Z, `0.08 deg` Y roll) | `42.0` (`~0.57 Hz` breathing) | `0.004 m` (`4 mm`) |
| **Steadicam Walk** | `0.0020 rad` (`0.11 deg`) | `28.0` (`~0.85 Hz` stride cadence) | `0.008 m` (`8 mm` vertical bob) |
| **Action / Impact Shake (Trauma Impulse)** | `0.0180 rad` (`1.0 deg`) decaying exponentially over `14 frames` | `3.5` | `0.015 m` |

## 4. Rack Focus Pulls (1st AC Timing)

A real 1st Assistant Camera pulls focus by rotating a physical lens gear ring:
- A focus pull from a foreground prop (`0.60 m`) to a midground doorway (`3.80 m`) takes `10 – 18 frames` (`0.4 – 0.75 s`) with an S-curve ease, often accompanied by a `1–2 cm` slight overshoot and micro-correction on fast action shots. Never snap focus distance in `1 frame`.
