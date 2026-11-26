# Mandatory Fake-3D Frame Audit Checklist

Run this checklist on every rendered `REVIEW` (`1920x1080`) frame before approving lookdev or launching a `FINAL` sequence render. Any `FAIL` item becomes the single target candidate for the next studio round.

- **Frame Inspected**: `frame_0001_review.png`
- **High-Sample Reference Crop Inspected**: `frame_0001_crop_2048spp.png`
- **Overall Checklist Verdict**: `PASS` (`25 / 25` items verified)

| # | Category | Diagnostic Check | Verdict (`PASS`/`FAIL`) | Observation / Evidence |
|---:|---|---|---|---|
| 1 | Geometry | All visible hard edges have physical bevels (`0.5-5.0 mm`) catching a specular line | `PASS` | Verified 1.5 mm 3-segment bevels via `mesh_linter.py` and 200% zoom crop |
| 2 | Geometry | Thin panels, glass, and cloth have real wall thickness (`>= 2 mm`) | `PASS` | Glass lens and casing walls solidified to 2.5 mm |
| 3 | Geometry | Curved silhouettes show zero polygon faceting against bright areas | `PASS` | Cylinder rim uses 64 segments + Subsurf level 2 |
| 4 | Geometry | Resting objects make tight contact (`0.0 mm` gap) with contact shadow occlusion | `PASS` | Base sits flush on surface with tight dark contact crease |
| 5 | Geometry | Repeated props vary in rotation, scale, and UV texture offset | `PASS` | Fasteners and dust motes randomized via Object Info Random |
| 6 | Geometry | Props break strict 90-degree world-axis alignment (`+-0.5 to 3.5 deg` asymmetry) | `PASS` | Hero prop and background tools rotated off-grid |
| 7 | Materials | Zero constant-roughness hero materials; fingerprints/wipes/dust modulate roughness | `PASS` | Verified via `audit_materials.py` and grazing highlight crop |
| 8 | Materials | Dielectric base color stays within physically plausible `[0.04, 0.80]` albedo bounds | `PASS` | Dark carbon body at 0.06, brushed steel metallic 1.0, dial at 0.74 |
| 9 | Materials | All Roughness, Metallic, Normal, and Displacement maps set to `Non-Color` | `PASS` | Confirmed 0 non-color violations in `audit_materials.py` |
| 10 | Materials | Procedural noises use multi-octave domain warping (no raw Perlin/Voronoi look) | `PASS` | 3-octave warped micro-grain on metal and table surface |
| 11 | Materials | Dust accumulates in upward cavities (`AO`) and wear appears on exposed outer edges | `PASS` | Cavity AO mask darkens screw recesses by 18% and raises roughness to 0.55 |
| 12 | Materials | Translucent organic/wax/skin materials use metric `Random Walk` SSS | `PASS` | Dial lume and leather strap use metric SSS radius |
| 13 | Materials | Silhouette surfaces with heavy relief use real displacement, not flat normal maps | `PASS` | Surface grooves displaced in geometry |
| 14 | Lighting | Zero unmotivated flat gray ambient world fill; shadows have natural depth | `PASS` | World background strength 0.0; fill comes from physical bounce card |
| 15 | Lighting | All lights have physical emitting area (`>= 0.05 m`); zero point-light pinpricks | `PASS` | Key area light 0.65 m x 0.45 m, rim light 0.40 m x 0.20 m |
| 16 | Lighting | Light sources use realistic Blackbody Kelvin contrast (warm key vs cool fill) | `PASS` | Key at 4800 K, fill bounce at 6800 K, rim at 5600 K |
| 17 | Lighting | View transform is `AgX` with smooth highlight desaturation and zero neon clipping | `PASS` | Confirmed `view_transform = 'AgX'` and clean highlight roll-off |
| 18 | Lighting | Zero light leaks at room corners or object seams | `PASS` | Enclosure shell blocks stray exterior rays |
| 19 | Lighting | Volumetrics (if present) are subtle (`density <= 0.015`) and bounded | `PASS` | Subtle atmospheric haze bounded to light beam |
| 20 | Lighting | Specular/metallic surfaces reflect a complete environment behind the camera | `PASS` | Dark studio flags and softbox reflections visible in glass crystal |
| 21 | Camera | Focal length and f-stop match physical scale (`f/8.0` macro, no toy-miniature blur) | `PASS` | 100 mm macro lens at f/8.0 focused at 0.32 m |
| 22 | Camera | Camera motion (if animated) includes physical inertia/settle, not linear spline movement | `PASS` | Static locked tripod still frame |
| 23 | Camera | Motion blur is enabled (`shutter = 0.5`) on all moving sequences | `PASS` | Configured in `REVIEW` and `FINAL` presets |
| 24 | Post/Denoise | Denoised image matches `2048-sample` reference crop without waxy loss of detail | `PASS` | Brushed steel grain preserved in side-by-side comparison |
| 25 | Post/Finish | Restrained physical glare, optical vignette, and 35mm sensor grain applied in comp | `PASS` | Fog glow glare (threshold 1.8) + 0.018 sensor grain applied |
