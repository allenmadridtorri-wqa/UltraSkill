# Organic Environment Modeling: Terrain, Rocks & Foliage

## 1. The Rule of Three Spatial Frequencies

Natural forms (cliffs, boulders, tree trunks, mud tracks) look fake whenever geometry only contains a single noise scale. Layer every organic mesh across three spatial frequencies:

| Frequency Tier | Spatial Scale (Starting Values) | Modeling / Displacement Method |
|---|---|---|
| **1. Primary (Macro Silhouette)** | `0.50 m – 10.0 m` | Block out major geological bedding planes, overhangs, or trunk lean. Must read clearly as a black-and-white silhouette at `960x540`. |
| **2. Secondary (Meso Structure)** | `0.03 m – 0.50 m` | Voronoi fracture cracks, stratified sedimentary shelves, exposed root buttresses, or bark plates via mesh geometry or Subdivision + Displacement modifier. |
| **3. Tertiary (Micro Relief)** | `0.0005 m – 0.03 m` (`0.5–30 mm`) | Pores, lichen bumps, sand grains, leaf veins via tangent-space Normal map or Cycles Adaptive Subdivision (`dicing_rate = 1.0 px` on hero assets). |

## 2. Rock & Cliff Construction Without "Melted Ice Cream"

Standard procedural Perlin/Cloud displacement rounds off every corner, turning rocks into melted wax blobs:
- Use **Voronoi Distance-to-Edge** or stepped `Map Range` / `ColorRamp` curves with sharp linear/constant transitions to create planar cleavage faces and sharp fracture ridges.
- Model 3–5 modular, closed-manifold "hero boulder" assets with unique faces on all 6 sides. Rotating and scaling a single 6-sided asymmetrical boulder across `90 deg` and `180 deg` axes yields 12 visually distinct rock formations at the cost of **1 mesh datablock** in Tesla T4 VRAM.

## 3. Translucent Foliage Geometry

Never model close-up or midground leaves as flat 2-triangle square alpha cards when rendering offline with Cycles:
1. **Geometric Cutout Over Heavy Alpha Overdraw**: Cut a 10–18 vertex polygon around the actual leaf boundary so rays do not waste transparent bounces in empty card corners. If alpha cutouts are used on distant trees, raise `scene.cycles.transparent_max_bounces` to `16–24` (starting value).
2. **Camber & Gravity Bend**: Bend every leaf blade along its midrib (`10–25 deg` droop) and fold the two lateral halves slightly upward (`5–12 deg` V-trough). Flat planar leaves catch specular highlights all at once like a mirror solar panel; cambered leaves catch soft rolling highlights.
3. **Ground Transition Debris**: Never plant a tree trunk directly into a flat terrain plane like a lollipop pole. Surround the base with root flare geometry, a slight soil mound (`+0.08 m` to `+0.20 m`), and scattered fallen leaves, twigs, and pebbles.
