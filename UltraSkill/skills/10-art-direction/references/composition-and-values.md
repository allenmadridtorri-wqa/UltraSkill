# Composition, Depth Planes & Luminance Value Structure

## 1. Three-Plane Depth Staging

Flat CG renders happen when every asset sits on a single midground plane at equal lighting intensity. Stage every camera view across three distinct depth planes:

| Depth Plane | Distance from Camera (Starting Values) | Value & Focus Role |
|---|---|---|
| **1. Foreground (FG)** | `0.4 m – 1.5 m` | Dark silhouette (`luminance 0.02 – 0.10`), out of focus, occupying `10% – 20%` of one frame border (doorframe, cable, foliage branch, machinery shoulder) to frame the view and give parallax during camera dolly moves. |
| **2. Midground (MG - Hero)** | `1.5 m – 8.0 m` | Critical sharp focus, highest key-to-fill contrast ratio (`3:1` to `8:1`), richest specular and texture detail. |
| **3. Background (BG)** | `8.0 m – infinity` | Lower local contrast, softened by optical defocus and subtle atmospheric scattering (`Principled Volume density 0.002 – 0.015`, starting value). |

## 2. Luminance Hierarchy & The Squint Test

The human visual system reads luminance contrast long before hue. To verify composition on a `PREVIEW` (`960x540`) render:

1. **The Squint / Blur Test**:
   - View the image at `25%` size (thumbnail scale). Can you identify the hero focal point in `< 0.5 seconds`?
   - If bright background windows, random ceiling lights, or shiny floor tiles compete with the hero subject, place a dark flag/cutter (`gobos`) or dim secondary practical lights by `1.5 to 2.0 stops`.
2. **Light-on-Dark or Dark-on-Light Separation**:
   - Place the lit side of the hero subject against a shadowed background area, and the shadowed side of the hero subject against a subtly lit background gradient (checkerboard value alternation).
3. **Rule of Thirds & Eye-Trace Continuity**:
   - Place the primary focal point near a thirds intersection (`x = 0.33` or `0.67`, `y = 0.38` or `0.62`) unless shooting a deliberate Kubrickian symmetrical one-point perspective shot.
   - In multi-shot trailers (`15-film-trailer`), keep the viewer's eye focus quadrant within `15%` screen distance across hard cuts so the viewer does not lose frames hunting for the subject.
