# Glass, Liquids, Meniscus Geometry & Caustics

## 1. Solid Glass vs Architectural Window Panes

Cycles path traces real dielectric refraction (`Transmission Weight = 1.0`). Use two distinct setups depending on whether the glass bends rays as a curved lens/goblet or acts as a flat window pane letting exterior sunlight into a room:

| Glass Role | Geometry Rule | Shader & Light-Path Rule |
|---|---|---|
| **Hero Lenses, Bottles, Watch Crystals, Goblets** | Model real double-sided thickness (`1.5 mm – 6.0 mm`). Never use a single flat plane (a single plane tells Cycles the entire room behind the glass is solid quartz!). | `Principled BSDF` (`Base Color = [0.98, 0.99, 0.98]`, `Roughness = 0.01–0.05` modulated by fingerprints, `IOR = 1.515`, `Transmission Weight = 1.0`). Ensure `transmission_bounces >= 12`. |
| **Flat Architectural Window Panes** | Double-paned (`2` sheets of `4 mm` glass separated by `12 mm` air gap) so exterior shots show authentic twin ghost reflections. | Mix `Principled BSDF` with `Transparent BSDF` using `Light Path -> Is Shadow Ray` (so direct sunlight passes straight into the room without waiting for caustic convergence). |

## 2. Liquid-in-Glass Meniscus & Interface Overlap

When rendering liquid inside a glass container, three interface rules prevent dark air-gap artifacts:

1. **Penetrate the Liquid Mesh slightly into the Glass Wall**: Expand the outer sides of the liquid mesh by `+0.15 mm` (`0.00015 m`) so it overlaps inside the inner glass wall rather than leaving a microscopic `0.01 mm` air gap. An air gap forces a 4-surface refraction (`Glass -> Air -> Liquid`), creating an unnaturally thick silver mirror ring.
2. **Model the Capillary Meniscus Rim**: Pull the outer perimeter edge loop of the top liquid surface upward by `+1.5 mm to +2.5 mm` with a smooth concave curve against the glass wall. That curved meniscus ring catches a bright razor highlight that immediately sells real liquid.
3. **Volumetric Beer-Lambert Absorption for Colored Liquids**:
   - Do not tint clear wine, whiskey, tea, or deep water by painting the surface `Base Color` dark brown—that makes a `1 mm` splash look as dark as a `10 cm` deep glass.
   - Keep `Base Color = [0.98, 0.98, 0.98]` and wire a **`Volume Absorption`** node (`Color = [0.85, 0.42, 0.12]`, `Density = 8.0 – 35.0`, starting value) into the material output's `Volume` socket so thin meniscus edges glow golden while the deep core darkens physically.

## 3. Enabling Cycles Shadow Caustics (Manifold Next Event Estimation)

For hero macro shots of watch crystals, perfume bottles, or water glasses on a table:
1. Select the **Light** source -> enable `light.cycles.is_caustics_light = True`.
2. Select the **Glass/Liquid Mesh** -> enable `obj.cycles.is_caustics_caster = True`.
3. Select the **Table/Floor Mesh** -> enable `obj.cycles.is_caustics_receiver = True`.
4. In Render Properties -> Light Paths -> enable `caustics_refractive = True`.
