# Character Forms, Anatomical Landmarks & Garment Layering

## 1. Proportions and Bony Landmarks

Whether modeling a realistic human, a stylized protagonist, or a mechanical biped, believable mass requires readable skeletal landmarks beneath soft tissue:

| Landmark | Metric Height / Proportion (`1.78 m` Adult Starting Value) | Why It Matters for Lighting & Rigging |
|---|---|---|
| **Total Stature** | `1.72 m – 1.82 m` (`~7.5 to 8.0` head heights) | Anchors door, furniture, and camera height (`1.60 m` eye level). |
| **Clavicle & Acromion** | `1.45 m` elevation; `0.42 m – 0.48 m` bi-deltoid width | Catches top key light and defines shoulder pivot for arm elevation. |
| **Iliac Crest & Greater Trochanter** | `0.92 m – 1.00 m` elevation | Separates torso tilt from leg swing in contrapposto weight shifts. |
| **Patella (Knee) & Tibial Tuberosity** | `0.48 m – 0.52 m` elevation | Must stay rigid during knee flexion while surrounding tendons compress. |
| **Zygomatic Arch, Brow Ridge & Mandible** | Head height `~0.23 m`; inter-pupillary distance `0.063 m` (`63 mm`) | Incorrect inter-pupillary distance (`< 56 mm` or `> 72 mm`) triggers immediate uncanny rejection. |

## 2. The Multi-Part Eye Assembly (Critical for Realism)

Never model a realistic eye as a single textured sphere:
1. **Outer Cornea / Sclera Shell**: Radius `~12.0 mm` (`0.024 m` diameter), transparent refractive shader (`IOR = 1.376`, roughness `0.01`) with a `0.8 mm` forward corneal dome bulge over the pupil.
2. **Inner Iris & Pupil Disc**: Recessed behind the corneal dome with a slight concave bowl so grazing side light illuminates the far side of the iris (caustic crescent).
3. **Caruncle & Tear Meniscus Strip**: A thin (`0.4 mm` tall) curved refractive mesh ribbon bridging the lower eyelid rim and the eyeball surface. Without the wet tear-line specular catchlight, eyes look like dry plastic marbles dropped into holes.

## 3. Garment Thickness & Layering

- Every collar, cuff, pocket flap, and hem must have real geometric thickness (`1.5 mm` cotton shirt, `3.0 mm` denim/wool coat, `4.5 mm` leather belt, starting values).
- Offset outer garments by a real physical gap (`1.5 mm – 4.0 mm`) over underlying skin or inner shirts so contact ambient occlusion and cast shadows read under key light.
- Delete hidden underlying body faces only after rigging weights are finalized and only where the skin can never be seen through collar/sleeve openings during extreme poses.
