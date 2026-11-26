# PBR Energy Conservation & Principled BSDF v2 Standards

## 1. The Three Laws of Physically Based Shading

Blender 4.x `Principled BSDF` enforces energy conservation automatically (diffuse + specular + transmission never exceeds incoming light energy) **only if** the artist feeds physically legal inputs into its sockets:

1. **No Pure Black (`< 0.03`) or Pure White (`> 0.82`) Dielectric Albedo**:
   - The darkest matte materials on Earth (coal, fresh asphalt, black velvet) reflect `3% – 5%` of incoming light (`linear RGB 0.03 – 0.05`). Setting Base Color to `0.00` kills bounce light and turns shadow creases into dead holes.
   - The brightest matte materials (titanium white wall paint, chalk, fresh snow) reflect `72% – 82%` (`linear RGB 0.72 – 0.82`). Setting a room's walls to `1.00` causes every bounce ray to retain 100% energy, washing out all contrast and doubling Cycles render noise.
2. **Metallic Is Binary (`0.0` or `1.0`)**:
   - A material is either a conductor (`Metallic = 1.0`, no diffuse subsurface reflection, colored F0 specular tint) or a dielectric (`Metallic = 0.0`, colored diffuse albedo, achromatic ~4% F0 Fresnel reflection).
   - The only valid values between `0.0` and `1.0` are sub-texel boundary pixels on a mask separating raw metal from a thick layer of paint, rust, or dirt (`Non-Color` mask passed through a steep `ColorRamp`).
3. **Physical Index of Refraction (`IOR`)**:
   - At grazing angles (`90 deg`), all smooth materials approach `100%` specular reflection (Fresnel effect). At normal incidence (`0 deg`), dielectric reflectivity is governed by:
     $$F_0 = \left(\frac{\text{IOR} - 1}{\text{IOR} + 1}\right)^2$$
   - Leave `IOR` at physical values instead of hacking specular sliders.

## 2. Calibrated Material Reference Table (Starting Values, Linear RGB)

| Material | Base Color (Linear Luminance / RGB) | Metallic | Roughness Range | IOR | Coat / Notes |
|---|---|---:|---|---:|---|
| **Asphalt (Weathered / Wet)** | `0.08` dry / `0.035` wet | `0.0` | `0.65 – 0.85` dry / `0.08 – 0.25` wet | `1.50` | Wet asphalt gets darker and glossier (`Coat Weight = 1.0, Coat Roughness = 0.05`). |
| **Architectural Concrete** | `0.24 – 0.38` | `0.0` | `0.55 – 0.82` | `1.52` | Add form-tie holes, micro-pitting normal map, and `6 mm` chipped bevels. |
| **Hardwood (Oiled Walnut/Oak)** | `[0.16, 0.09, 0.05]` to `[0.35, 0.22, 0.12]` | `0.0` | `0.22 – 0.48` (driven by wood pore map) | `1.53` | Use `Coat Weight = 0.4, Coat Roughness = 0.15` for polyurethane varnish. |
| **Matte Interior Drywall Paint** | `0.68 – 0.76` | `0.0` | `0.50 – 0.68` | `1.48` | Add subtle `0.15 mm` roller stipple bump (`Distance = 0.0002 m`). |
| **Anodized Black Aluminum** | `[0.06, 0.06, 0.065]` | `1.0` | `0.24 – 0.38` | `1.50` | Add `Anisotropic = 0.45` and edge-wear mask revealing raw `[0.88, 0.90, 0.92]` aluminum. |
| **Brushed Stainless Steel** | `[0.63, 0.62, 0.60]` | `1.0` | `0.18 – 0.34` | `2.50` | `Anisotropic = 0.65 – 0.85`, tangent aligned to UV brushing direction. |
| **Polished Brass / Gold** | Brass `[0.88, 0.72, 0.32]` / Gold `[1.0, 0.76, 0.33]` | `1.0` | `0.08 – 0.28` (`0.45+` in oxidized crevices) | `1.47` | Darken and roughen cavities with an Ambient Occlusion oxidation mask. |

Verify every material in the scene using [`../scripts/audit_materials.py`](../scripts/audit_materials.py).
