# Photographic Reference Gathering & Deconstruction

## 1. Never Reference Other CGI for Realism

When aiming for footage that viewers could mistake for real photography, never use other 3D renders, concept paintings, or AI-generated images as your lighting or material ground truth—they amplify existing CG biases (over-saturated rim lights, uniform edge wear, impossible bounce glow). Only use real photographs and motion picture frames shot through physical glass lenses.

## 2. The 4-Quadrant Reference Spec

Document four distinct reference targets in your project `BRIEF.md` or `SHOT_LIST.md` before modeling starts:

| Quadrant | What to Extract | Measurable Values to Record |
|---|---|---|
| **1. Scale & Structural Anatomy** | Real manufacturing seams, fastener sizes, wall thickness, cables, and human-scale anchors (door handles at `1.0 m`, stairs at `0.18 m` riser). | Overall bounding box in meters; bevel radius in millimeters (`0.5 mm` machined metal vs `4.0 mm` cast concrete). |
| **2. Surface Imperfection History** | Where hands touch (polished oils), where dust settles (upward-facing crevices), where mop/wiper blades leave streaks. | Base albedo value (`0.04–0.80`), roughness min/max spread (e.g., `0.15` worn contact zone vs `0.45` dusty recess). |
| **3. Lighting Direction & Ratio** | Key light elevation angle, shadow penumbra softness, sky vs bounce fill color temperature delta. | Key Kelvin (`e.g. 5400 K`), fill Kelvin (`e.g. 7500 K` skylight), stops of contrast between key side and shadow side (`2.5 to 4.5 stops`, starting value). |
| **4. Optical & Sensor Signatures** | Depth-of-field bokeh shape, highlight halation, barrel distortion, shadow noise floor. | Focal length (`mm`), f-stop, chromatic aberration limit (`<= 1.5 px` at frame corners, starting value). |

## 3. How to Verify Your Render Against Reference

1. Place the real reference photo and your `REVIEW` render side by side at equal vertical height.
2. Convert both images to **luminance grayscale** and blur both with a `16 px` Gaussian radius:
   - If the blurred grayscale patches do not match in black floor, midtone distribution, and highlight area percentage, fix the lighting ratios (`12-materials-lighting`) before touching any texture map.
3. Inspect a `200%` crop of an edge highlight and a shadow transition to verify bevel width and surface micro-roughness.
