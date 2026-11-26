# Fixed-Timestep Game Loops, Interpolation & Time Dilation

## 1. Never Multiply Physics or Jump Velocity by Variable Render `delta`

If you integrate gravity and velocity inside a variable render callback (`_process(delta)` or raw `requestAnimationFrame`) without a fixed timestep accumulator:
$$v \leftarrow v - g \cdot \Delta t, \quad y \leftarrow y + v \cdot \Delta t$$
A player running at `30 FPS` (`\Delta t = 33.3 ms` on the `LOW` laptop preset) jumps **`8%` lower** and clips through thin `0.25 m` walls compared to a player on a `144 Hz` monitor (`\Delta t = 6.9 ms`).

## 2. The Canonical Fixed-Timestep Accumulator (`60 Hz`)

In custom JavaScript/Three.js or C++/Rust loops, run simulation steps at an exact constant $\Delta t_{\text{fixed}} = \frac{1}{60}\text{ s}$ (`16.6667 ms`) and interpolate visual transforms using the remainder $\alpha \in [0, 1)$:

```javascript
const FIXED_DT = 1.0 / 60.0;
const MAX_FRAME_DT = 0.1; // Clamp tab-switch stalls at 100 ms (6 physics steps max)
let accumulator = 0.0;

export function stepGameLoop(rawDeltaSeconds, timeScale, simulateFixedTick, renderInterpolated) {
  const clampedDelta = Math.min(Math.max(0.0, rawDeltaSeconds), MAX_FRAME_DT);
  accumulator += clampedDelta * timeScale;

  while (accumulator >= FIXED_DT) {
    simulateFixedTick(FIXED_DT);
    accumulator -= FIXED_DT;
  }

  const alpha = accumulator / FIXED_DT;
  renderInterpolated(alpha);
}
```
*(In Godot 4, place all character movement, `move_and_slide()`, hitbox scans, and AI ticks inside `_physics_process(delta)` and enable `physics/common/physics_interpolation = true`.)*

## 3. Isolated Time Dilation for Hitstop & Pause Menus

When a heavy melee strike lands (`22-gameplay-systems`), freezing or slowing the world for **`40 – 85 ms` (`3 – 5 frames` at `60 Hz`)** makes the impact feel bone-crunching.
- **Never set global `Engine.time_scale = 0.0` blindly** if your UI animations, audio ducking timers, or camera trauma shake decay read from the same scaled clock—setting `time_scale = 0.0` can freeze the timer that was supposed to end the hitstop!
- **Rule**: Always track hitstop duration using the **unscaled real-time monotonic clock** (`Time.get_ticks_usec()` in Godot or `performance.now()` in JS), or pause only the `WorldSimulation` subtree (`process_mode = PROCESS_MODE_PAUSABLE`) while keeping `HUD`, `AudioDirector`, and `CameraShake` on `PROCESS_MODE_ALWAYS`.
