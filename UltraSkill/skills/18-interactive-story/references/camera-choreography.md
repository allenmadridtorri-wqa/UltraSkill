# Interactive Camera Choreography & Mark Blending

## 1. Authored Camera Marks vs Free Orbit

Pure free-orbit cameras let players frame conversations from awkward angles (inside a character's shoulder or staring at a blank wall). Pure locked cutscenes strip away agency. Combine both using **Authored Camera Marks with Subtle Mouse/Touch Parallax**:

| Camera Mark Type | Typical FOV (`vertical deg`) | Position & Look-At Target | Permitted Player Parallax Offset (Starting Values) |
|---|---:|---|---|
| **`cam_wide` (Exploration Hub)** | `45 deg` (`~35 mm` lens) | High corner or doorway overlooking all room hotspots | `+-0.35 m` horizontal pan, `+-0.18 m` vertical tilt |
| **`cam_prop_macro` (Clue Inspection)** | `28 deg` (`~65 mm` lens) | `0.55 m` from prop at `30 deg` angle | `+-15 deg` orbit around the prop focus target |
| **`cam_dialogue_ots` (Conversation)** | `34 deg` (`~50 mm` lens) | Over listener's shoulder (`0.65 m` behind, `0.25 m` lateral offset), focused on speaker's eyes | `+-0.06 m` subtle breathing + pointer parallax |

## 2. Frame-Rate-Independent Exponential Damping

Never use `camera.position.lerp(target, 0.05)` without delta time—at `30 FPS` (`LOW` laptop preset) the camera moves half as fast as at `60 FPS`, and at `144 Hz` it snaps twice as fast!

Use exact exponential decay damping driven by frame delta time $\Delta t$ (seconds) and responsiveness rate $\lambda \in [4.0, 7.0]\text{ s}^{-1}$ (starting value):

```javascript
export function dampVec3(currentVec, targetVec, lambda, dt) {
  const factor = 1.0 - Math.exp(-lambda * dt);
  currentVec.lerp(targetVec, factor);
}

export function dampFloat(current, target, lambda, dt) {
  return current + (target - current) * (1.0 - Math.exp(-lambda * dt));
}
```

## 3. When to Hard-Cut vs Smooth-Transition

- **Smooth Damped Transition (`lambda = 5.0`, `~1.1 s`)**: Moving between two viewpoints inside the same physical room within `< 90 deg` heading change (e.g., `cam_wide` -> zooming into `cam_chronometer_macro` on the desk).
- **Hard Cut (or 6-Frame Cross-Dissolve)**: Crossing the `180 deg` line, jumping more than `6.0 meters`, or switching between two speakers in a rapid Act 3 dialogue confrontation. Swinging a 3D camera `160 deg` across walls in 1 second induces motion sickness and clips through pillars.
