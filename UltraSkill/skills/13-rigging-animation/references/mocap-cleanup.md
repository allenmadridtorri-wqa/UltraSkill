# Motion Capture Retargeting & Foot-Lock Cleanup

## 1. The Four Classic Mocap Artifacts

Raw optical or video-extracted motion capture data never ships cleanly without cleanup:
1. **Foot Skating / Sliding**: Due to skeleton proportion differences between the actor and the 3D rig, planted feet drift `2 cm – 10 cm` across the floor tile during stance phases.
2. **High-Frequency Sensor Jitter**: `60–120 Hz` tracking noise causes fingers, head, and knees to vibrate nervously.
3. **Knee & Elbow Hyper-Extension Pops**: When the retargeted IK target pulls `1 mm` farther than the limb length, the knee snaps straight and pops backward for 1–2 frames.
4. **Intersecting Hands / Props**: Hands clip into hips, rifle stocks, or table surfaces because the actor's body girth differed from the character mesh.

## 2. Step-by-Step Mocap Cleanup Protocol in Blender

1. **Filter Sensor Noise First (Butterworth / Smooth F-Curves)**:
   - In the Graph Editor, select all rotation curves on spine, neck, head, and limbs and apply `Smooth Keys` or `Butterworth Smooth` (` cutoff = 6.0 – 9.0 Hz` at `24–60 fps`, starting value) **before** locking feet.
2. **Convert Limb Chains to IK and Lock Stance Phases**:
   - Identify every frame interval $[t_{\text{heel\_strike}}, t_{\text{toe\_off}}]$ where a foot bears weight.
   - At $t_{\text{heel\_strike}}$, snap the IK foot controller (`CTRL-foot_ik.L`) to `Z = 0.000 m` (floor plane) and copy its exact world `(X, Y, Z)` location across the entire stance interval using **`Constant` or zero-slope flat tangents** so horizontal drift is `0.0000 m`.
   - Use the foot-roll controller to peel the heel up during the final `3–4 frames` before $t_{\text{toe\_off}}$ while the toe tip pivot remains locked to the floor.
3. **Eliminate Knee Pops via Soft-IK or Pelvis Drop**:
   - Scrub the knee angle curve (`DEF-thigh` vs `DEF-shin`). Whenever the knee approaches `< 4.0 deg` from full straight extension, lower the pelvis controller (`CTRL-hips.location.z`) by `-0.01 m to -0.03 m` on an **Additive NLA Layer** over a `6-frame` bell curve.
4. **Additive NLA Layer for Posture & Prop Contact**:
   - Never hand-edit baked per-frame mocap keys directly. Push the cleaned base mocap clip down into an NLA track (`Combine`), create a new empty Action track on top set to `Add` or `Combine`, and key sparse 8–16 frame posture offsets to fix hand-to-prop contact and gaze direction.
