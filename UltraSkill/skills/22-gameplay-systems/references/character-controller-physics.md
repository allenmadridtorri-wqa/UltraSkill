# Character Controller Physics

A responsive character controller uses kinematics (`CharacterBody3D` / `CharacterBody2D` with `move_and_slide()`), never an unguided dynamic rigid body (`RigidBody3D`) pushed by raw forces.

---

## 1. Kinematic Jump Math from Designer Metrics

Designers specify **Jump Height ($H$)** in meters and **Time to Apex ($t_{apex}$)** in seconds—never raw impulse or gravity constants. Derive physics parameters directly:

$$g_{up} = \frac{2H}{t_{apex}^2}, \quad v_{jump} = \frac{2H}{t_{apex}}$$

### Worked Example (`H = 2.4 m`, `t_apex = 0.42 s`, `t_fall = 0.32 s`)
- **Ascent Gravity ($g_{up}$)**: $\frac{2 \times 2.4}{0.42^2} = 27.21\text{ m/s}^2$
- **Initial Jump Velocity ($v_{jump}$)**: $\frac{2 \times 2.4}{0.42} = 11.43\text{ m/s}$
- **Descent Gravity ($g_{down}$)**: $\frac{2 \times 2.4}{0.32^2} = 46.88\text{ m/s}^2$ (`~1.72x` ascent gravity)
- **Terminal Fall Velocity**: Clamp `velocity.y >= -28.0 m/s` so falling off tall cliffs never tunnels through thin floors.

---

## 2. Coyote Time & Jump Buffering

Two non-negotiable forgiveness windows separate amateur platforming from responsive controls:

1. **Coyote Time (`0.10 s` / 6 frames @ 60 Hz)**:
   - Track `time_since_grounded`. Reset to `0.0` every frame `is_on_floor()` is true.
   - When the player walks off a ledge *without jumping*, allow a jump if `time_since_grounded <= 0.10`.
   - Upon jumping, immediately set `time_since_grounded = 999.0` to prevent double-jumping inside the coyote window.
2. **Jump Buffering (`0.12 s` / 7 frames @ 60 Hz)**:
   - When the player presses `jump` while airborne, set `jump_buffer_timer = 0.12`.
   - On the first frame `is_on_floor()` becomes true while `jump_buffer_timer > 0.0`, execute the jump immediately and consume the buffer.

---

## 3. Ground Acceleration, Friction, and Turning Snap

1. **Instant Turn-Around Boost**:
   - When the player's input vector opposes their current horizontal velocity (`input_dir.dot(velocity_horiz) < 0.0`), multiply acceleration by **`2.0x`** (`90.0 m/s²`) so direction reversals feel crisp rather than slippery.
2. **Slopes & Floor Snapping**:
   - Set `floor_max_angle = deg_to_rad(45.0)`.
   - Set `floor_snap_length = 0.25` meters (disabled on the frame a jump is initiated) so running down a 30° ramp keeps the capsule glued to the slope instead of micro-bouncing into the air.
   - Enable `floor_constant_speed = true` so running uphill at 30° does not slow the player to `cos(30°) = 86.6%` speed unless explicitly desired.

---

## 4. Ledge Corner Correction (Head Bump Nudging)

When jumping near the underside edge of a platform, if the outer 15% of the player's head capsule clips the corner while the center ray is clear, nudge the player laterally by up to `0.20 m` instead of killing their upward momentum.
