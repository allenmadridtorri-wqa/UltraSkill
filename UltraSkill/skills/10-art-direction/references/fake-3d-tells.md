# The 25 Fake-3D Tells & How Veterans Fix Them

Every offline Cycles frame must be audited against these 25 common CGI giveaways before passing `REVIEW`.

## A. Geometry & Scale Tells (1–6)
1. **Zero-Radius Razor Edges**: Real metal, wood, and stone have rounded edges (`0.5 mm – 5.0 mm`) that catch a thin specular highlight line. *Fix*: Add Bevel modifier (`2–3` segments, Harden Normals) or Cycles Bevel shader node (`radius 0.001 m`).
2. **Paper-Thin Single-Sided Walls/Cloth**: Window glass, sheets, and metal panels without physical thickness refract and shadow incorrectly. *Fix*: Solidify modifier (`2 mm – 15 mm`).
3. **Faceted Cylinders & Curved Silhouettes**: Low-poly rim visible against bright backlight. *Fix*: Ensure curved silhouettes subtend `< 2 px` per edge segment on screen (`64+` vertices on close cylinders or Subdivision level `2`).
4. **Floating Contact Seams**: Tires, boots, or table legs hovering `1 mm` above the floor or intersecting cleanly without a contact bevel/groove. *Fix*: Snap to surface (`0.0 mm` gap) and add a micro-skirt or contact displacement depression.
5. **Cloned Identical Repetition**: Five identical rocks or crates in a row with the same scratch pattern. *Fix*: Randomize Z rotation (`0–360 deg`), scale (`0.85–1.15`), and drive shader UV offsets with `Object Info -> Random`.
6. **Perfect 90-Degree Grid Alignment**: Furniture, books, and panels aligned to exact world axes. *Fix*: Perturb rotations by `+-0.5 deg` to `+-3.5 deg`.

## B. Material & Texture Tells (7–13)
7. **Constant Uniform Roughness**: A flat float value (`roughness = 0.25`) across a surface. *Fix*: Modulate roughness with wiped smudge/dust maps (`+-0.08` around base roughness).
8. **Illegal Super-White or Super-Black Albedo**: Pure `1.0` white blows out GI bounce; pure `0.0` black eats all light. *Fix*: Clamp dielectric base color inside `[0.04, 0.80]`.
9. **Wrong Normal Map Color Space**: Normal map left as `sRGB` instead of `Non-Color`, causing dark seam creases. *Fix*: Set `image.colorspace_settings.name = 'Non-Color'`.
10. **Procedural Noise That Looks Like Perlin/Voronoi Math**: Unbroken raw Musgrave or Voronoi patterns at a single octave. *Fix*: Warp domain coordinates with a second noise texture and blend across 3 spatial frequencies (macro, meso, micro).
11. **Missing Cavity Dust & Edge Wear**: Uniform dirt in flat middle areas instead of accumulated grime inside crevices and wear on exposed outer edges. *Fix*: Drive dirt mix with `Ambient Occlusion` node and edge wear with `Pointiness` / Bevel dot-product.
12. **Opaque Wax/Skin/Leaves Without Subsurface Scattering**: Organic surfaces looking like painted drywall. *Fix*: Enable `Random Walk` SSS with metric scale (`skills/12-materials-lighting/references/subsurface-scattering.md`).
13. **Flat Bump Without Micro-Displacement on Silhouettes**: Heavy brick or rock normal maps whose outer profile against the sky is a straight line. *Fix*: Enable adaptive displacement or geometric displacement on silhouette edges.

## C. Lighting & Color Tells (14–20)
14. **Unmotivated Flat Ambient Fill**: Uniform gray world background lifting all shadows to milk. *Fix*: Set world strength to `0.0` (interiors) or use a directional HDRI / physical Nishita sky with portal lights.
15. **Point Lights With Zero Radius**: Infinitely sharp shadow edges and zero specular reflection dot. *Fix*: Use Area lights or Sphere lights with physical radius (`>= 0.05 m` bulb, `>= 0.60 m` softbox).
16. **Mismatched Color Temperatures**: Every light at pure white `6500 K`. *Fix*: Use Blackbody node (`2700 K–3200 K` tungsten practicals, `5200 K` sun, `7500 K–9000 K` sky shadow fill).
17. **sRGB Highlight Clipping (Neon Rings)**: Bright lamps turning yellow/cyan around overexposed cores. *Fix*: Switch View Transform to **AgX**.
18. **Light Leaking Through Thin Corners**: Bright glow bleeding inside closed room corners. *Fix*: Give room walls outer thickness (`>= 0.20 m`) or surround interior sets with a black light-blocker shell.
19. **Overdone Volumetric Fog**: Dense gray soup hiding poor lighting. *Fix*: Keep `Principled Volume` density subtle (`0.001 – 0.015`, anisotropy `0.5 – 0.7`) and bound it to lit shafts.
20. **Missing Reflection Environment Behind Camera**: Chrome or glass reflecting an empty gray void behind the camera frustum. *Fix*: Place dark bounce/room geometry or an interior HDRI behind the camera.

## D. Camera, Motion & Post-Processing Tells (21–25)
21. **Impossible Depth of Field (Miniature Effect)**: `f/0.95` blur on a full-size building. *Fix*: Match physical lens aperture to real subject distance (`f/5.6 – f/11` for wide/macro).
22. **Linear Robotic Camera Interpolation**: Camera starting and stopping instantaneously on a single spline segment. *Fix*: Ease acceleration with tripod drag, dolly mass, and subtle `0.15 deg` handheld breathing noise (`13-rigging-animation`).
23. **Rendered Animation Without Motion Blur**: Stroboscopic crisp edges on fast-moving props. *Fix*: Enable Cycles Motion Blur (`shutter = 0.5`).
24. **Denoiser Waxiness / Shadow Boiling**: Fine pores and grain wiped smooth by low-sample denoising. *Fix*: Verify against a `2048-sample` crop and re-apply subtle 35mm sensor grain (`0.015–0.030` strength) in compositing after denoising.
25. **Excessive Chromatic Aberration & Lens Flare**: Rainbow fringes `10 px` wide across the image. *Fix*: Cap lens dispersion/CA at `<= 1.5 px` at extreme corners and use thresholded physical fog-glow glare (`threshold >= 1.5`).
