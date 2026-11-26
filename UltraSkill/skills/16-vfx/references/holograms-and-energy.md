# Holograms, Plasma & Interactive Energy Emitters

## 1. Why Holograms Must Be Physically Integrated Into the Room

A glowing cyan mesh pasted over a dark room without illuminating the operator's fingertips, casting reflections into the table surface, or scattering inside room dust reads as a 2D UI overlay rather than a 3D hologram.

### Five Requirements of Photorealistic Holograms & Plasma in Cycles
1. **Real Indirect GI Emission**:
   - In Cycles path tracing, an `Emission` shader automatically casts indirect diffuse and glossy rays onto surrounding tables, hands, and eyeglasses.
   - To prevent firefly noise when a tiny bright wireframe illuminates a dark room, mix two emission strengths using `Light Path -> Is Camera Ray`:
     - **Camera Ray (`Is Camera Ray = 1`)**: Sharp high-contrast emission (`Strength = 12.0 – 35.0`) so AgX rolls the core toward white while preserving colored fringes.
     - **Diffuse/Glossy Bounce Rays (`Is Camera Ray = 0`)**: Smooth averaged emission (`Strength = 4.0 – 8.0`) or pair with a low-noise physical `AREA` light (`Spread = 110 deg`) tinted to the hologram's primary hue.
2. **Fresnel Edge Falloff (`Layer Weight`)**:
   - Real volumetric projections and CRT/laser interference fields brighten at grazing silhouettes (`Layer Weight -> Facing^2.5`) and become semi-transparent (`Transparent BSDF` mix) when viewed dead-on (`0 deg`).
3. **Physical Projector Origin & Volumetric Cone**:
   - A hologram does not float out of thin air without an emitter lens. Model a physical projector aperture on the table or wrist brace, place a dirty glass lens over it, and connect the lens to the hologram with a subtle `Principled Volume` light cone (`density = 0.04`, modulated by radial streaks).
4. **3D Spatial Scanlines & Voxel Grid Quantization**:
   - Drive opacity with object-space `Z` sine waves (`sin(P.z * 850.0)`) multiplied by a slow vertical phase roll (`#frame * 0.15`) so scanlines stick to 3D world millimeters rather than 2D screen pixels.
5. **Optical Depth-of-Field Blur**:
   - Because the hologram is rendered inside Cycles 3D space (not added in 2D post), background corners of the hologram naturally defocus into 7-bladed bokeh discs when the camera focuses on the foreground edge.
