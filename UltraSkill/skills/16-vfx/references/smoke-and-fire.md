# Mantaflow Smoke, Fire & Volumetric Blackbody Shading

## 1. Avoiding the "CG Mushroom Blob"

Default Mantaflow smoke/fire simulations look fake for three reasons:
1. **Too low voxel resolution (`32` or `64` divisions)** combined with zero vorticity produces smooth, pillowy spheres.
2. **Too fast buoyancy (`Heat = 4.0+`)** shoots a straight vertical column with a single symmetric mushroom cap.
3. **Uniform emitter fuel** emits gas evenly across a smooth sphere instead of a turbulent, noisy surface texture.

## 2. Calibrated Mantaflow Domain Settings (Starting Values)

Always verify memory and disk size with [`../scripts/sim_budget_estimator.py`](../scripts/sim_budget_estimator.py) before baking on Google Colab:

| Domain Parameter | Blocking Preview | Final Hero Plume (Colab Bake) | Purpose |
|---|---|---|---|
| `Resolution Divisions` | `64 – 96` | `192 – 280` | Base voxel grid along longest domain axis. |
| `Adaptive Domain` | `True` (`Margin = 4`) | `True` (`Margin = 6`, `Threshold = 0.005`) | Shrinks active voxel box around actual smoke, saving `50%–80%` RAM and disk. |
| `Time Scale` | `0.85 – 1.0` | `0.75 – 0.90` (`< 1.0` adds massive scale weight) | Large industrial fires evolve slightly slower in apparent angular velocity than tabletop matches. |
| `Vorticity` | `0.25` | `0.35 – 0.55` | Injects small-scale rotational eddies along shear boundaries. |
| `Noise (Upres Factor 2)` | `False` | `True` (`Strength = 0.8`, `Scale = 2.0`) | Synthesizes fine wavelet turbulence on top of the base grid. |
| `Cache Format` | `OpenVDB` (`BLOSC` or `ZIP`, `Half Float 16-bit`) | `OpenVDB` (`ZIP`, `16-bit Half Float`) | Saved directly to `/content/drive/MyDrive/<project>/vdb_cache/`. |
| `Emitter Surface Texture` | Animated 3D `Clouds/Voronoi` (`Size = 0.25`) | Animated 3D `Noise` modulating `Fuel` (`0.4 – 1.8`) | Breaks up emission at the source so flames lick in ragged tongues. |

## 3. Physically Based `Principled Volume` Shader Under AgX

Never color fire with an arbitrary RGB ColorRamp in Standard sRGB:
1. Set `Principled Volume -> Color` (smoke albedo) to dark soot `[0.06, 0.06, 0.065]` for oil/tire fires or `[0.35, 0.36, 0.38]` for wood/steam smoke.
2. Set `Density` to `15.0 – 45.0` (multiplied by the `density` grid via an `Attribute` + `Math Multiply` node).
3. Set `Anisotropy` to `0.35 – 0.55` so backlighting rims the smoke billow edges.
4. Set `Blackbody Intensity` to `1.5 – 4.0` (driven by the `flame` attribute passed through a power curve $f^{1.8}$ so the transition from flame to dark smoke is crisp) and `Temperature` to `2400 K – 3800 K`. Under **AgX**, the `3800 K` core naturally rolls off to pale incandescent yellow-white while the outer `1600 K` shell glows deep orange-red.
