# Animation Principles for Physical Realism

## 1. Realism vs Cartoon Exaggeration

In photorealistic trailers and grounded games, traditional Disney squash-and-stretch breaks the illusion immediately (bones and steel do not stretch 20% mid-air). Realistic animation relies on **Newtonian mass, center-of-gravity support, and ballistic momentum**:

| Principle | How It Manifests in Photoreal 3D | Numbers & Starting Values (`24 fps`) |
|---|---|---|
| **Center of Mass (CoM) Shift** | A biped cannot lift its left foot until its pelvis shifts laterally (`+0.06 m to +0.10 m`) over the planted right foot. | Pelvis lateral weight shift leads foot liftoff by `3 – 5 frames` (`125 – 200 ms`). |
| **Ballistic Gravity Parabola** | Once airborne, the center of mass follows $z(t) = z_0 + v_0 t - \frac{1}{2} g t^2$ ($g = 9.81\text{ m/s}^2$). Never hang or slow down mid-air after apex. | A `0.50 m` vertical jump takes `0.32 s` (`~8 frames`) up and `0.32 s` (`~8 frames`) down. |
| **Impact Compression & Settle** | Heavy objects and bodies absorb kinetic energy on landing through knee/suspension compression and damped oscillation. | Heavy landing: `2 frames` rapid compression (`-0.12 m` to `-0.25 m` pelvis drop), `6 – 10 frames` damped recovery. |
| **Sequential Breaking of Joints** | The hips rotate first, followed by chest (`+2 frames`), shoulder (`+3 frames`), elbow (`+4 frames`), and wrist (`+5 frames`). | Simultaneous keyframing on the same frame across spine/arm/head looks robotic ("twinning"). Offset downstream bone keys by `1 – 3 frames`. |
| **Micro-Alive Holds** | No living creature freezes to `0.000` velocity during dialogue or aiming. | Keep a `0.25 Hz` breathing cycle (`chest X rot +0.8 deg`, `shoulder Z +3 mm`) active during all idle holds. |

## 2. F-Curve Tangent Discipline

- **Impacts & Footstrikes**: The incoming tangent into a floor collision or sword strike must be **`Vector` (linear high velocity)**, never eased to zero before touching the ground. Slowing down 2 frames before hitting the floor destroys all perceived weight.
- **Mechanical Hydraulics & Robotics**: Heavy machinery accelerates quickly to a constant motor slew velocity (`Linear` F-curve middle segment) and stops with a brief high-frequency structural vibration (`2–3 cycles` at `8–12 Hz`, amplitude `1–2 mm`), reflecting steel mass and hydraulic fluid compression.
