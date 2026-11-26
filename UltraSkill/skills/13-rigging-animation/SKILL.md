---
name: 13-rigging-animation
description: >-
  Skeletal rigging, skin weight deformation, mocap foot-lock cleanup, physical
  camera mass rigs, facial FACS/saccade animation, and keyframe baking for
  Blender Cycles trailers and realtime game engines.
---

# 13-Rigging-Animation: Physical Mass, Deformation & Camera Inertia

Synthetic CG motion betrays itself in the first 12 frames through weightless spline interpolation, sliding feet, rigid eyeballs, and zero-mass camera pans. Every rig and animation in UltraSkill honors physical inertia and bakes deterministically before Colab rendering or glTF export.

## When to use

Load this skill whenever building armatures, painting skin weights, cleaning up motion-capture clips, animating characters or mechanical assemblies, choreographing physical camera dolly/crane moves, or baking keyframes for headless rendering.

## Inputs

- Retopologized quad mesh from `11-modeling` (`mesh_linter.py` passing, scale `1.0`).
- `SHOT_LIST.md` timing, frame rate (`24 fps` film or `60 Hz` game), and camera lens specs from `10-art-direction`.

## Steps

1. **Construct Clean Hierarchy & Control Rigs**:
   - Follow [`references/skeleton-and-controls.md`](references/skeleton-and-controls.md): separate deformation bones (`DEF-*`) from control curves (`CTRL-*`) and mechanism bones (`MCH-*`), align bone primary roll axes consistently (`+Y` along bone length, `+Z` bend plane), and include twist bones on forearms and thighs.
2. **Normalize Skin Weights & Add Joint Correctives**:
   - Follow [`references/skinning-and-correctives.md`](references/skinning-and-correctives.md): normalize all vertex weights (`sum == 1.0`), cap at `<= 4` bone influences per vertex for game/web targets, enable `Preserve Volume` (dual-quaternion) in Cycles, and add driver-controlled corrective shape keys at `90 deg+` elbow/knee/shoulder bends.
3. **Animate with Physical Mass & Clean Up Mocap**:
   - Follow [`references/animation-principles-for-realism.md`](references/animation-principles-for-realism.md) and [`references/mocap-cleanup.md`](references/mocap-cleanup.md): lock planted feet with world-space IK floor contact (`0.0 mm` drift during stance phase), shift the pelvis center of mass over the supporting foot before lifting the opposite leg, and add micro-settle damping (`2–4 frames`) on hard stops.
4. **Animate Eyes, Faces & Secondary Overlap**:
   - Follow [`references/facial-and-eyes.md`](references/facial-and-eyes.md) and [`references/secondary-motion.md`](references/secondary-motion.md): use stepped saccadic eye darts (eyes never pan smoothly except when tracking a moving target) paired with automatic eyelid-cornea flesh displacement.
5. **Drive Cameras Through a Physical Dolly/Crane Rig**:
   - Run [`scripts/camera_rig_builder.py`](scripts/camera_rig_builder.py) and follow [`references/physical-camera-animation.md`](references/physical-camera-animation.md) so camera translations and focus pulls carry tripod fluid-head drag and subtle operator breathing.
6. **Bake All Procedural Motion & Constraints Before Colab Upload**:
   - Run `blender -b scene.blend -P skills/13-rigging-animation/scripts/bake_animation.py` so every frame renders deterministically across Colab session resumes.

## Numbers and defaults

All values below are **starting values**:

| Parameter | Starting Value | Verification Method |
|---|---|---|
| **Timeline Frame Rate** | `24 fps` (cinematic trailer/VFX) or `60 fps` (realtime gameplay) | `scene.render.fps` |
| **Max Bone Influences per Vertex** | `4` (realtime glTF/Godot hard limit); `8` (offline Cycles) | Blender Weight Limit Total (`limit=4`) |
| **Foot Contact Drift Tolerance** | `<= 0.5 mm` (`0.0005 m`) horizontal translation while foot is planted | Inspect IK foot bone world XY graph |
| **Eye Saccade Duration** | `2 – 3 frames` at `24 fps` (`80 – 125 ms`) between fixed gaze holds | Graph Editor stepped/fast S-curve check |
| **Blink Duration** | `3 – 5 frames` (`1 frame` fast down, `1 frame` closed, `2–3 frames` eased up) | Inspect eyelid controller F-curve |
| **Handheld Camera Breathing Noise** | Rotation amplitude `0.08 deg – 0.25 deg`, frequency `0.25 – 0.40 Hz` (`Scale = 45–80` frames) | `camera_rig_builder.py` defaults |

## Failure modes and fixes

- **Candy-wrapper wrist twist**: Forearm rotates `180 deg` at a single wrist joint, collapsing the mesh to zero thickness. Split forearm twist `50% / 50%` across two forearm bones (`DEF-forearm.upper`, `DEF-forearm.lower`) driven by a damped-track twist constraint.
- **Spline float (underwater astronauts)**: Bezier handles left on `Auto Clamped` across a strike or foot impact. Switch contact keyframes to `Vector` incoming / steep ease-out so velocity transfers sharply at impact.
- **Colab resume renders wrong pose on frame 120**: Unbaked spring/jiggle add-on or physics modifier evaluated without prior frames. Always run `bake_animation.py` before uploading to Google Drive.

## Done check

- Planted feet show zero horizontal sliding on floor contact frames.
- Camera rig uses eased acceleration and target focus distance tracking (`camera_rig_builder.py`).
- All animation curves are baked (`bake_animation.py` exit code `0`) and verified over a 24-frame playblast/motion strip.

## Related files

- [`references/skeleton-and-controls.md`](references/skeleton-and-controls.md)
- [`references/skinning-and-correctives.md`](references/skinning-and-correctives.md)
- [`references/animation-principles-for-realism.md`](references/animation-principles-for-realism.md)
- [`references/mocap-cleanup.md`](references/mocap-cleanup.md)
- [`references/physical-camera-animation.md`](references/physical-camera-animation.md)
- [`references/facial-and-eyes.md`](references/facial-and-eyes.md)
- [`references/secondary-motion.md`](references/secondary-motion.md)
- [`scripts/camera_rig_builder.py`](scripts/camera_rig_builder.py)
- [`scripts/bake_animation.py`](scripts/bake_animation.py)
