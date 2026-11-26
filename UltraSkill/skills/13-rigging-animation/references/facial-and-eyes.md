# Facial Rigging, FACS Action Units & Saccadic Eye Motion

## 1. Eyes Never Pan Smoothly (Unless Tracking a Moving Target)

The single biggest uncanny tell in digital character animation is rotating the eyes from left to right using a smooth `20-frame` Bezier interpolation while looking around a room.
- **Physiological reality (Saccades)**: Human eyes jump between fixation points in ballistic darts lasting **`2 to 3 frames` (`80 – 125 ms` at `24 fps`)**, hold completely locked on the target for `12 – 48 frames`, and dart again (`0.5 deg – 2.0 deg` micro-saccades between left eye, right eye, and mouth of the listener during conversation).
- **Head-Lag Rule**: When looking at a new target `> 15 deg` away, the **eyes dart first (`Frame 0`)**, the **eyelids blink (`Frame 1–5`)** to mask the motion blur, and the **head/neck follows `3 – 5 frames` later** with a soft damped settle.

## 2. Eyelid-Cornea Fleshy Coupling

Real eyelids wrap over a spherical eyeball with a raised corneal dome (`+0.8 mm` bulge):
1. **Gaze-Driven Eyelid Follow (`25% – 40%`)**:
   - When the eye rotates upward (`+15 deg`), the upper eyelid is pushed up by `+6 deg` and the lower eyelid rises by `+3 deg`.
   - When looking downward (`-15 deg`), the upper eyelid drops by `-8 deg` to keep the upper iris margin slightly covered (`10–15%` covered at neutral gaze; showing white sclera above the iris reads as terror or madness).
2. **Corneal Bulge Deformer**:
   - Use a `SurfaceDeform` / `Shrinkwrap` modifier or rotational corrective shape keys on the eyelid skin so the moving corneal bump pushes a subtle `0.6 mm` traveling bulge under the closed or half-closed eyelid during saccades.

## 3. Core FACS Blendshape / Bone Matrix (Starting Values)

| FACS Action Unit | Muscle Name | Visual Coupled Effect (Never Isolate One Zone!) |
|---|---|---|
| **AU1 + AU2** | Inner / Outer Brow Raiser (`Frontalis`) | Horizontal forehead compression wrinkles + upper eyelid skin stretches taut. |
| **AU4** | Brow Lowerer (`Corrugator`) | Vertical glabellar ("11") furrow between brows; inner brow heads pull down and together. |
| **AU6 + AU12** | Cheek Raiser + Lip Corner Puller (Genuine Duchenne Smile) | A fake smile moves only the mouth corners (`AU12`). A real smile (`AU6+AU12`) pushes the infraorbital cheek pad up, narrowing the lower eyelid aperture and creasing outer crow's-feet. |
| **AU26 / Jaw Open** | Mandible Hinge + Translation | The jaw does not hinge around the ear like a nutcracker; the mandibular condyle rotates `~10 deg` and **slides forward and down (`+4 mm`)** along the temporal fossa. |
