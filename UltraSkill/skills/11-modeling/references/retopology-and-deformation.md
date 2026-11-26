# Retopology & Deformation Quad Flow

## 1. Core Rules for Deforming Meshes

Any mesh driven by an armature (`13-rigging-animation`) or blendshapes/shape keys must follow strict all-quad deformation topology:

1. **100% Quads in Deformation Zones**: Triangles and N-gons pinch and crease unpredictably when subdivided or bent across bone weights.
2. **Even Aspect-Ratio Quads**: Keep quad edge lengths roughly square (`aspect ratio <= 2:1`). Long thin rectangular strips buckle when twisted along a forearm or neck.
3. **Minimum 3 Loop Rings at Hinges**: Elbows, knees, finger knuckles, and jaw hinges require at least `3` parallel encircling edge loops (tighter spacing on the outer extension side, wider spacing on the inner compression crease side so volume is preserved).

## 2. Facial Loop Architecture

Structure every deforming face around five concentric muscle-aligned quad loops:
- **Orbicularis Oculi (Eye Mask Loops)**: Concentric rings radiating from the eyelids out across the temple and upper cheek.
- **Orbicularis Oris (Mouth Loops)**: Concentric rings radiating from the inner lip margin out to the chin cleft.
- **Nasolabial Fold Loop**: A continuous edge loop flowing from above the nostril wing (`ala`) down around the corner of the mouth (`modiolus`) to the chin. This loop must align directly with the smile crease so expression blendshapes never sawtooth across diagonal quad edges.
- **Muzzle / Nose-to-Chin Loop**: Wraps from the bridge of the nose around the mouth and under the jaw.
- **5-Edge Poles (Stars)**: Place the inevitable 5-edge junction poles on the flat bony cheek and forehead zones where skin slides minimally.

## 3. Target Polygon Budgets (Starting Values)

| Target Platform | Base Retopo Mesh (Before Subsurf) | Render / Engine Triangle Count |
|---|---|---|
| **Offline Cycles Hero Character** | `25,000 – 60,000` quads | `400,000 – 960,000` tris at Subsurf level `2` |
| **Offline Midground / Crowd Character** | `8,000 – 15,000` quads | `30,000 – 60,000` tris |
| **Realtime Desktop / Console Game Hero** | `15,000 – 35,000` tris | `15,000 – 35,000` tris (normal map baked) |
| **Realtime LOW Preset (4 GB Laptop / Web)** | `3,500 – 8,000` tris | `3,500 – 8,000` tris (`<= 4` bone weights/vertex) |
