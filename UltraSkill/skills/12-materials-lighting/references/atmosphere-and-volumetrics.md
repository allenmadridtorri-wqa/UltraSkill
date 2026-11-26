# Volumetric Atmosphere, God Rays & Haze Budgeting

## 1. Never Attach `Principled Volume` to the Infinite World Shader

Attaching a `Principled Volume` node to the `World` shader fills space out to infinity—meaning rays marching toward the sky dome or distant HDRI get absorbed completely, turning the sky black and multiplying render times by `4x`.

**Rule**: Always create a bounded box mesh (`Fog_Domain_Box`) enclosing only the active camera frustum and the lit zone (`+2.0 m` margin), disable its `Shadow` and `Diffuse` ray visibility if needed, set Viewport Display to `WIRE`, and assign the volumetric material to that bounded box.

## 2. Calibrated `Principled Volume` Parameters (Starting Values)

| Atmosphere Type | `Density` (`m^-1`) | `Anisotropy` (`g`) | `Color` / `Absorption Color` | Max Volume Bounces |
|---|---:|---:|---|---:|
| **Clean Large Warehouse / Museum Air** | `0.001 – 0.003` | `0.60` | `[0.85, 0.88, 0.92]` | `1 – 2` |
| **Dusty Sunbeam Interior (God Rays)** | `0.008 – 0.022` | `0.65 – 0.78` | `[0.82, 0.78, 0.72]` | `2` |
| **Misty Forest Morning / Street Alley** | `0.015 – 0.045` | `0.55 – 0.70` | `[0.75, 0.82, 0.88]` | `2 – 4` |
| **Thick Ground Steam / Dry Ice** | `0.150 – 0.600` (height-masked) | `0.40` | `[0.90, 0.92, 0.95]` | `4` |

## 3. Why Forward Scattering (`Anisotropy = 0.6 – 0.75`) Is Essential

Airborne dust and water droplets scatter light strongly in the forward direction (Henyey-Greenstein phase function $g \in [0.55, 0.80]$).
- At `Anisotropy = 0.0` (isotropic), fog looks like uniform gray milk across the entire frame, destroying black levels.
- At `Anisotropy = 0.68`, air stays crystal clear and dark in the shadows while glowing with localized halation around light fixtures and backlight shafts.

## 4. Exponential Height Falloff for Ground Mist

Real mist hugs cold floors and valleys rather than stopping at the flat top face of your domain cube. Drive `Principled Volume -> Density` with an exponential height gradient:
$$\rho(z) = \rho_0 \cdot \exp\left(-\max(0, z - z_{\text{floor}}) \cdot k_{\text{falloff}}\right) \cdot \text{Noise3D}(x, y, z)$$
where $k_{\text{falloff}} \in [0.8, 2.5]\text{ m}^{-1}$ (starting value), ensuring the top boundary of the fog box fades smoothly to `0.0` density with zero visible cube edge.
