# Game Camera Systems

The camera is the player's eyes. A jittery, wall-clipping, or nauseating camera ruins even the best combat and art direction.

---

## 1. Frame-Rate Independent Smoothing (Exponential Decay)

Never use `pos = lerp(pos, target, 0.1)` inside a variable-delta `_process(delta)` loop—at 30 FPS it lags twice as far behind as at 60 FPS. Use exponential decay damping:

```gdscript
func exp_decay_vec3(current: Vector3, target: Vector3, decay: float, dt: float) -> Vector3:
	return target + (current - target) * exp(-decay * dt)
```

| Camera Axis / Mode | Decay Constant (`decay`) | Feel |
|---|---|---|
| Horizontal Follow (X/Z) | `14.0 – 18.0` | Tight framing, minimal lag |
| Vertical Follow (Y - Grounded) | `10.0 – 12.0` | Smooths stairs and small steps |
| Vertical Follow (Y - Airborne) | `4.0` (until apex/landing) | Reduces vertical bob during small jumps |
| Combat Lock-On Framing | `16.0` | Keeps player and target inside inner 70% safe frame |

---

## 2. Third-Person Orbit & Collision Whiskers

1. **Pivot Offset (Over-the-Shoulder Framing)**:
   - Place the pivot at `height = 1.55 m` (chest/shoulder height) with a lateral offset of `+0.35 m` (right shoulder) so the player character does not block the center crosshair.
   - Default boom length: `3.2 m` (exploration), `4.2 m` (melee combat with multiple enemies).
2. **Sphere-Cast Spring Arm (Anti-Clipping)**:
   - Cast a sphere of radius `0.22 m` (greater than the camera near clip plane `0.10 m`) from the character's head pivot to the desired camera position against Static Environment layers only (never collide with enemies, ragdolls, or small debris).
   - **Asymmetric Snap**:
     - When an obstacle blocks the boom: snap forward **fast** (`decay = 45.0`) so the wall never clips the near plane.
     - When the obstacle clears: ease back out **smoothly** (`decay = 8.0`) to prevent rapid zoom-pumping past pillars.

---

## 3. Pitch Clamping & Horizon Auto-Leveling

- **Pitch Limits**:
  - First-Person: `[-85°, +85°]` (prevents gimbal flip at `±90°`).
  - Third-Person: `[-60°` looking up from low angle, `+75°` looking down from overhead`]`.
- **Optional Movement Auto-Centering**:
  - Only engage gentle yaw recentering (`decay = 1.5`) after `2.0 seconds` of zero right-stick / mouse input while moving laterally, and provide a toggle to disable it in settings.

---

## 4. Rotational Trauma Camera Shake

Never shake a camera with pure `randf_range(-1, 1)` position offsets (causes severe motion sickness and clips geometry). Use **Perlin-noise rotational trauma**:
- Store `trauma` in `[0.0, 1.0]`. Add `+0.25` for light hits, `+0.60` for explosions.
- Decay trauma linearly: `trauma = max(0.0, trauma - 1.8 * dt)`.
- Compute shake intensity as `shake = trauma * trauma` (quadratic curve gives punchy peaks and soft tails).
- Apply to camera local Euler angles only (`max_pitch = 2.5°`, `max_yaw = 2.5°`, `max_roll = 3.5°`), multiplied by a user accessibility slider (`0%–100%`).
