# Storyboard, Previz Animatic & Screen-Direction Continuity

## 1. Never Render Un-Edited Shots

In professional studio production, the **Edit is locked before Final Lighting starts**.
1. **Stage 1 — Keyframe Storyboard (`1` frame per shot at `PREVIEW` `960x540`)**:
   - Render the middle frame of each planned shot in `TRAILER_BEAT_SHEET.md`.
   - Assemble the stills into [`../scripts/contact_sheet.py`](../scripts/contact_sheet.py) to check shot progression (Wide -> Medium -> Close-Up) and silhouette clarity.
2. **Stage 2 — Timed Previz Animatic (`1440` frames)**:
   - Hold each `PREVIEW` keyframe still for its planned frame count (or render a fast stamped EEVEE playblast) muxed with the scratch sound track.
   - Watch the 60-second MP4 straight through without pausing. If a shot lingers `8 frames` too long or a cut misses a percussion hit, adjust the frame numbers in `TRAILER_BEAT_SHEET.md` now while changes cost zero GPU hours.
3. **Stage 3 — Cycles OptiX Shot Replacement**:
   - As each shot finishes rendering on Colab at `REVIEW` / `FINAL`, splice it over its exact frame range in the animatic.

## 2. The 180-Degree Line & Screen-Direction Continuity

If a vehicle, projectile, or running character moves **Left-to-Right** in `SH-040` and then cuts to a camera on the opposite side of the action line where the same character moves **Right-to-Left** in `SH-050`, the audience perceives an instant head-on collision or reversal.

- **Rule**: Draw an imaginary **Line of Action** between the protagonist and their destination (or opponent). Keep all cameras within a single scene on the same side (`180 deg` hemisphere) of that line unless a camera physically dollies across the line during an unbroken shot.

## 3. Blender Timeline Camera Markers for Multi-Shot Scenes

When staging multiple shots inside a single `.blend` scene, bind each shot's camera to an exact timeline marker in Python:

```python
import bpy

def bind_camera_to_frame(scene: bpy.types.Scene, cam_obj: bpy.types.Object, frame_no: int, shot_id: str) -> None:
    marker = scene.timeline_markers.new(name=shot_id, frame=frame_no)
    marker.camera = cam_obj
```
