---
name: 10-art-direction
description: >-
  Art direction and cinematography skill for photorealistic 3D renders,
  trailers, and game environments. Covers real-photo reference boards, physical
  camera sensors and lenses, value composition, the 25 fake-3D tells diagnostic,
  and framing strategies for the Uncanny Five.
---

# 10-Art-Direction: Photographic Grounding & Fake-3D Elimination

Photorealism is won or lost before shader nodes are wired. A veteran art director anchors every shot to real photography, physical camera optics, disciplined luminance ratios, and a systematic audit of CGI giveaways.

## When to use

Load this skill before modeling (`11-modeling`), lighting (`12-materials-lighting`), or storyboarding (`15-film-trailer`), and load [`templates/FAKE_3D_CHECKLIST.md`](templates/FAKE_3D_CHECKLIST.md) during every `REVIEW` round to diagnose why a frame looks synthetic.

## Inputs

- Approved `BRIEF.md` and `BARS.md` from `00-director`.
- Subject matter, environment setting, and time of day / mood.

## Steps

1. **Assemble a 4-Quadrant Photographic Reference Plan**:
   - Follow [`references/reference-gathering.md`](references/reference-gathering.md) to specify real-world photographic benchmarks for (A) Primary Subject & Scale, (B) Material Wear & Micro-Texture, (C) Motivated Lighting & Atmosphere, and (D) Lens Optics & Grade.
2. **Author the Shot List with Physical Camera Optics**:
   - Fill out [`templates/SHOT_LIST.md`](templates/SHOT_LIST.md) using [`references/lens-and-camera.md`](references/lens-and-camera.md).
   - Every shot must specify sensor width (`36 mm` full-frame or `24.89 mm` Super35), focal length (`24 mm` to `135 mm`), f-stop (`f/2.0` to `f/11`), focus distance in meters, shutter angle (`180 deg` = `0.5` frame shutter), and physical camera height above ground.
3. **Establish Composition & Grayscale Value Structure**:
   - Apply [`references/composition-and-values.md`](references/composition-and-values.md): separate foreground (dark silhouette or soft out-of-focus framing element), midground (lit hero focal point), and background (atmospheric falloff).
   - Check the frame in grayscale: the hero subject must carry the highest local contrast ratio (`>= 3:1` against immediate background, starting value).
4. **Apply Framing Rules for the Uncanny Five**:
   - Check [`references/hardest-subjects.md`](references/hardest-subjects.md). State plainly when digital humans, hair, cloth, water, or fire are requested, and frame them with motivated occlusion, distance, backlighting, or motion blur when budget is constrained.
5. **Run the Fake-3D Checklist on Every Approved Frame**:
   - Score [`templates/FAKE_3D_CHECKLIST.md`](templates/FAKE_3D_CHECKLIST.md) using [`references/fake-3d-tells.md`](references/fake-3d-tells.md). Any single `FAIL` becomes the target candidate for the next studio round.

## Numbers and defaults

All values below are **starting values** for physical 3D cameras:

- **Sensor size**: `36.0 mm x 24.0 mm` (Full Frame) or `24.89 mm x 18.66 mm` (Arri Super35).
- **Focal length by shot role**:
  - Wide establishing environment: `24 mm – 28 mm` (`f/5.6 – f/8.0`)
  - Natural human perspective / medium shot: `35 mm – 50 mm` (`f/2.8 – f/4.0`)
  - Hero portrait / product compression: `85 mm – 105 mm` (`f/2.0 – f/2.8`)
  - Macro mechanical detail: `100 mm` (`f/8.0 – f/16` to prevent paper-thin unusable DOF)
- **Camera height**: `1.60 m` standing eye level, `0.90 m` hip/cinematic tripod level, `0.15 m` low heroic angle.
- **Shutter speed / angle**: `180 deg` (`scene.render.motion_blur_shutter = 0.5` at `24 fps`, equivalent to `1/48 s`).

## Failure modes and fixes

- **Default 50mm camera floating at arbitrary height with infinite focus**: Looks like a viewport screenshot. Set physical height (`0.9 m` or `1.6 m`), enable Depth of Field on a target empty, and choose a deliberate lens (`28 mm` or `85 mm`).
- **Orthographic-looking wide shots without foreground anchor**: Place a dark out-of-focus foreground element across 10–15% of one frame edge to create parallax and depth scale.
- **Perfect mathematical alignment of props**: Humans never align chairs, books, or bolts to `0.000 deg`. Add `+-1.5 deg` to `+-4.0 deg` rotational and `+-5 mm` positional asymmetry to every prop.

## Done check

- `SHOT_LIST.md` defines sensor, focal length, aperture, focus distance, and camera height for every shot.
- `FAKE_3D_CHECKLIST.md` is 100% completed on the rendered `REVIEW` still with 0 `FAIL` items.

## Related files

- [`references/reference-gathering.md`](references/reference-gathering.md)
- [`references/lens-and-camera.md`](references/lens-and-camera.md)
- [`references/composition-and-values.md`](references/composition-and-values.md)
- [`references/fake-3d-tells.md`](references/fake-3d-tells.md)
- [`references/hardest-subjects.md`](references/hardest-subjects.md)
- [`templates/SHOT_LIST.md`](templates/SHOT_LIST.md)
- [`templates/FAKE_3D_CHECKLIST.md`](templates/FAKE_3D_CHECKLIST.md)
