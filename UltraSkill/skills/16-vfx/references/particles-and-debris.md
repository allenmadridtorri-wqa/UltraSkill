# Particle Systems: Sparks, Dust Motes, Rain & Micro-Debris

## 1. Power-Law Size Distribution (Never Use Uniform Particle Sizes)

In real physical impacts, grinding sparks, and crumbling concrete, small particles outnumber medium particles by `10:1` and large chunks by `100:1`. If every particle in a system has `scale = 0.02 m +- 10%`, it reads immediately as a 1990s particle emitter.
- **Fix**: Drive instance scale with a power curve ($s = s_{\min} + (s_{\max} - s_{\min}) \cdot u^3$, where $u \in [0, 1]$ is uniform random) so `85%` of particles are fine grit (`1–3 mm`), `12%` are medium chips (`5–15 mm`), and `3%` are tumbling hero fragments (`20–45 mm`).

## 2. Four Production Particle Recipes (Starting Values)

| Particle System | Count & Lifespan | Velocity & Forces | Geometry & Shader |
|---|---|---|---|
| **1. Atmospheric Dust Motes (Sunbeam)** | `800 – 2,500` inside camera frustum box; persistent | `Gravity = 0.02` (almost neutral buoyancy), `Turbulence = 0.08 m/s`, `Brownian = 0.03` | Tiny 8-vert uneven flake (`0.5 – 2.2 mm`); `Principled BSDF` (`Roughness = 0.4`, `Alpha = 0.35`, `Translucent` mix `40%`). Catches bokeh discs when out of focus! |
| **2. Welding / Impact Grinding Sparks** | `300 – 1,500` burst over `4–12 frames`; lifespan `8–35 frames` | Initial velocity `6.0 – 16.0 m/s`, `Air Drag = 0.35`, `Collision Bounciness = 0.25`, `Friction = 0.4` | Elongated 6-vert octahedron (`1.5 mm`); `Emission` driven by `Particle Info -> Age / Lifetime` mapped via `Blackbody` from `3600 K` (birth) down to `1400 K` (death). **Requires Cycles Motion Blur (`shutter = 0.5`) to draw streaks!** |
| **3. Falling Rain Streaks** | `4,000 – 12,000` inside frustum cylinder | Terminal velocity `-8.5 to -11.0 m/s` (`-Z`) + wind `1.5 m/s` (`+X`) | `2 mm` refractive water drop (`IOR = 1.333`, `Transmission = 1.0`). Motion blur stretches each drop into a `0.18 m` translucent streak. Pair with ground splash ripple rings. |
| **4. Concrete / Rock Impact Chips** | `150 – 600` per fracture event | Inherit parent rigid-body velocity + normal impulse `2.0 – 5.0 m/s`; `Angular Velocity = 15 – 45 rad/s` | Collection of `5` asymmetrical Voronoi rock shards instanced (`Instance on Points`). |
