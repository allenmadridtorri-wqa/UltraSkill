# HDRI Environment Maps, Nishita Sky & Interior Light Portals

## 1. Selecting & Evaluating True 32-Bit HDRIs

Many free ".hdr" files online have clipped sun discs (`max value = 15.0` instead of `20,000+`), which produce muddy, shadowless outdoor renders.
- **Verification check**: Load the `.exr` or `.hdr` in Blender's Image Editor and drop view exposure to `-12 EV`. If the sun disc turns gray at `-4 EV`, the HDRI has clipped dynamic range.
- **Fix for clipped HDRIs**: Align a physical Cycles `SUN` light (`Strength = 3.0 – 5.0`, `Angle = 0.526 deg` for clear day or `2.5 deg` for hazy cloud cover, `Blackbody = 5400 K`) with the HDRI sun azimuth/elevation so cast shadows have crisp physical penumbras.

## 2. Cycles Physical Nishita Sky Texture (Zero-Download Exterior Lighting)

When no external HDRI is bundled, use Cycles' built-in physical `Sky Texture` node set to **`NISHITA`**:

| Parameter | Golden Hour (Starting Value) | Crisp Midday (Starting Value) | Overcast / Hazy (Starting Value) |
|---|---|---|---|
| `sky_type` | `'NISHITA'` | `'NISHITA'` | `'NISHITA'` (or mix `80%` diffused Z gradient) |
| `sun_disc` | `True` | `True` | `False` (use broad `AREA` / soft `SUN` at `Angle = 15 deg`) |
| `sun_size` | `0.545 deg` (`0.00951 rad`) | `0.526 deg` (`0.00918 rad`) | `8.0 deg` |
| `sun_elevation` | `4.0 – 12.0 deg` | `48.0 – 65.0 deg` | `35.0 deg` |
| `air_density` | `1.2 – 1.8` | `1.0` | `1.5` |
| `dust_density` | `1.5 – 3.0` | `0.8` | `4.0` |
| `ozone_density` | `1.5` (deepens twilight blue overhead) | `1.0` | `1.0` |
| `Background Strength` | `0.15 – 0.35` (calibrated for AgX `0.0` exposure) | `0.08 – 0.18` | `0.20` |

## 3. Mandatory Light Portals for Interior Window Scenes

When rendering an interior room lit primarily by exterior sky/HDRI through window openings, Cycles wastes 90% of environment rays shooting into solid walls.
- Place an `AREA` light directly outside each window frame, sized to cover the exact window opening (`+0.05 m` margin), pointing inward (`-Z` into the room).
- Enable **`light.cycles.is_portal = True`**.
- Portals emit zero light of their own; they steer environment sky rays directly through the window opening, cutting interior shadow noise by `3x to 5x` at equal sample counts.
