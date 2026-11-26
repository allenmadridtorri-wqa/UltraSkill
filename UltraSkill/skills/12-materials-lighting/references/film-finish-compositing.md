# Film Finish in Compositing: Glare, Lens Optics, Grade & Grain

## 1. Why Raw Path-Traced PixelsStill Look Clinical

Even a physically perfect path-traced frame lacks the optical and sensor physics of a real camera lens and CMOS/film gate. Real lenses scatter a small fraction of bright light internally (veiling glare / bloom), attenuate corner exposure (natural $\cos^4 \theta$ optical falloff), introduce sub-pixel lateral chromatic dispersion, and record photon shot noise (fine sensor grain).

**Rule**: Apply these optical effects in the **Blender Compositor** (or via [`../../16-vfx/scripts/build_compositor_tree.py`](../../16-vfx/scripts/build_compositor_tree.py)) with **strict restraint**. Overdoing bloom or chromatic aberration makes an image look like a cheap 2010 video game.

## 2. Calibrated Film-Finish Node Chain (Starting Values)

Execute the compositor stack in this exact order on scene-linear data:

| Step | Compositor Node | Starting Values | Restraint Limit (What Never to Exceed) |
|---:|---|---|---|
| **1. Optical Bloom / Halation** | `CompositorNodeGlare` (`glare_type = 'BLOOM'` or `'FOG_GLOW'`) | `Threshold = 1.6 – 2.5`, `Size = 6 – 8`, `Mix = -0.75` (or `Strength = 0.08 – 0.18` in Blender 4.2+) | Only specular catchlights and bare lamps may bloom. If midtone skin or concrete glows, raise `Threshold` to `2.5+`. |
| **2. Subtle Barrel Distortion & Dispersion** | `CompositorNodeLensdist` | `Distort = -0.006 to -0.015`, `Dispersion = 0.002 to 0.005`, `use_fit = True` | Never exceed `Dispersion = 0.008` (`~1.5 px` color fringe at extreme corners). |
| **3. Natural Optical Vignette** | Ellipse Mask -> `Blur` (`35%` screen size) -> `Mix (Multiply)` | Corner exposure drop of `-0.25 EV to -0.45 EV` (`Multiply factor = 0.12 – 0.22`) | Never darken corners into a heavy black tunnel keyhole. |
| **4. Color Balance (Lift / Gamma / Gain or Offset / Power / Slope)** | `CompositorNodeColorBalance` (`ASC-CDL`) | `Offset = [0.0, 0.0, 0.002]` (subtle shadow toe), `Power = [1.0, 1.0, 1.0]`, `Slope = [1.02, 1.0, 0.98]` | Keep black floor neutral (`R=G=B` within `0.003` at deepest black). |
| **5. 35mm Sensor / Film Grain (Last Step!)** | Procedural fine noise overlay (`Overlay` / `Soft Light` blend, weighted toward midtones) | `Strength = 0.015 – 0.028`, grain size `1.0 – 1.4 px` at 1080p, animated seed per frame | **Always apply grain AFTER denoising and lens distortion.** Grain restores micro-acutance removed by the denoiser and prevents 8-bit MP4 gradient banding. |
