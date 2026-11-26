# Physical Lenses, Camera Sensors & Optical Reality

## 1. Real Cameras Have Physical Dimensions and Mounts

A CG camera can sit inside a wall at `0.001 m` with a `12 mm` rectilinear lens and infinite depth of field—and the human eye immediately recognizes that no physical camera body could occupy that space.

### Physical Camera Placement Rules
- Keep the nodal point at least `0.20 m` away from walls and floors (size of a cinema camera body + matte box).
- Keep verticals straight (`X rotation = 90 deg`, `Y rotation = 0 deg`) on architectural wide shots (`<= 28 mm`) and use ** Camera Shift Y** (`camera.shift_y` between `-0.15` and `+0.20`, starting value) instead of pitching the camera up and creating converging keystone towers.

## 2. Sensor & Lens Reference Table (Starting Values)

Configure `camera.sensor_fit = 'HORIZONTAL'` and `camera.sensor_width = 36.0` (Full Frame) or `24.89` (Super35 Cinema):

| Focal Length (36mm Sensor) | Horizontal FOV | Typical Aperture (`f-stop`) | Visual Compression & Depth of Field Behavior |
|---:|---:|---|---|
| `24 mm` | `73.7 deg` | `f/5.6 – f/8.0` | Expansive depth, steep perspective lines, deep focus (`1.2 m` to infinity). Keep subjects `> 1.5 m` from lens to avoid bulbous distortion. |
| `35 mm` | `54.4 deg` | `f/2.8 – f/5.6` | Classic cinema director's lens. Preserves spatial context while separating a subject at `1.5–2.5 m`. |
| `50 mm` | `39.6 deg` | `f/2.0 – f/4.0` | Neutral perspective closely matching human central vision. Clean background falloff at `2.0 m` focus distance. |
| `85 mm` | `23.9 deg` | `f/1.8 – f/2.8` | Flattering portrait and hero product lens; compresses background distance and isolates silhouette against creamy bokeh. |
| `105 mm – 135 mm` | `19.5 – 15.2 deg` | `f/2.8 – f/8.0` | Telephoto compression for outdoor streets, machinery close-ups, or tabletop macro (`f/8.0 – f/11` required at `< 0.5 m` focus distance!). |

## 3. The Macro Depth-of-Field Trap (Toy Miniatures)

If you model a building or car at `0.1x` scale (or set `f/1.4` at a `0.30 m` focus distance), the depth of field narrows to `3 millimeters`. The viewer's brain interprets ultra-shallow DOF on a large object as a **tilt-shift toy miniature**.

- **Verification formula**:
  - For a human-scale subject at `2.5 m` distance on a `50 mm` lens at `f/2.8`, the sharp zone is roughly `0.35 m` deep (front of nose to behind ears).
  - For a tabletop watch (`0.04 m` wide) at `0.25 m` distance on a `100 mm` macro lens, stop down to `f/8.0 – f/11` so the dial and hands remain sharp while the background table drops out of focus.

## 4. Bokeh Blades and Anamorphic Ratio

In Cycles (`camera.dof`):
- Set `aperture_blades = 7` or `9` (odd blade counts match cinema prime lenses) and `aperture_rotation = 0.26` rad (`15 deg`).
- For widescreen cinema trailers (`2.39:1`), optionally set `aperture_ratio = 1.8` or `2.0` to produce oval anamorphic bokeh highlights.
