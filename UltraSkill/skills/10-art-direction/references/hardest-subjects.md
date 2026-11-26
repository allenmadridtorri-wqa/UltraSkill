# The Uncanny Five: Digital Humans, Hair, Cloth, Water & Fire

## 1. Plain Honesty Rule

State plainly to the user and in `BRIEF.md`: **digital humans, groom hair, dynamic cloth, open water, and close-up fire are the five hardest subjects in computer graphics to make convincing.** Human vision evolved over millions of years to detect sub-millimeter flaws in facial skin, eye moisture, and fluid motion; a single error in subsurface radius or simulation substep destroys the illusion immediately.

## 2. Why They Fail & Veteran Framing Strategies

| Subject | Primary Uncanny Failure Mode | When Full Simulation Is Required | Framing & Art-Direction Mitigation (Budget / T4 Safe) |
|---|---|---|---|
| **1. Digital Humans (Skin & Eyes)** | Waxy uniform SSS (`radius` not scaled to meters), missing tear-line meniscus between lower eyelid and cornea, rigid nasolabial fold during speech, dead non-saccadic eyes. | 8K UDIM pore displacement maps, Random Walk SSS (`scale 0.01 m`, radius `[1.0, 0.35, 0.2]`), dual-layer cornea/iris refraction, FACS blendshapes. | Frame in high-contrast chiaroscuro (3/4 rim or silhouette), behind helmet visors/goggles, in reflections, or at medium/wide distance (`>= 3.0 m`). |
| **2. Groom Hair & Fur** | Thick spaghetti ribbons (`radius > 0.08 mm`), missing flyaway hairs against backlight, flat specular without dual longitudinal shift (Marschner R/TT/TRT lobes). | `80,000 – 150,000` interpolated hair curves with `Principled Hair BSDF` (`Chiang` model, roughness `0.25`, radial roughness `0.35`, coat `0.1`). | Keep subjects wearing hoods, helmets, caps, or wet/tied-back grooms; avoid close macro wind-blown hair simulations unless budgeted. |
| **3. Dynamic Cloth** | Rubber-sheet stretching, self-intersection popping at elbows/knees, zero thickness at cuffs, floaty low-gravity settling. | High-substep (`>= 15` quality steps) cloth sim with `0.002 m` self-collision margin and Solidify modifier (`2–4 mm`) after bake. | Use structured hard-shell armor, stiff coats, or static sculpted folds with normal-map tension wrinkles for non-deforming areas. |
| **4. Open Water & Splashes** | Jelly-like thick droplets, low-resolution blobby FLIP mesh without whitewater foam/spray particles, flat procedural ocean waves without meniscus. | Mantaflow FLIP (`resolution >= 256`, spray/foam/bubble secondary particles) or Ocean Modifier + animated foam masks; baked to Drive. | Use calm wet puddles, rain streaks on glass, rippled dark pools with planar reflections, or distant mist-shrouded surf. |
| **5. Fire & Explosions** | Smooth laminar "mushroom balls", clip-white orange blobs without blackbody Kelvin roll-off under AgX, smoke that emits light without illuminating the room. | High-division Mantaflow (`192–320` divisions), vorticity `0.3–0.6`, temperature-driven `Principled Volume` Blackbody (`1800 K–4200 K`), baked OpenVDB. | Frame fire through heat-shimmer glass, use fast shutter sparks + flickering physical area lights off-camera, or layer real CC0 VDB plumes. |

## 3. Verification Check Before Approving Any of the Uncanny Five

If any of the Uncanny Five appears in a shot occupying `> 15%` of screen height:
1. Render a `REVIEW` (`1920x1080`) still and a `2048-sample` crop before animating.
2. Compare directly against a real photograph of the same subject under matching key light angle.
3. If the subject still fails `FAKE_3D_CHECKLIST.md` by Round 3, pivot the camera framing or lighting contrast immediately rather than burning Rounds 4–5 on minor parameter tweaks.
