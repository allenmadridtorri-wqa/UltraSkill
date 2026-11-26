# Motivated Physical Lighting Rigs & Contrast Ratios

## 1. Banning Unmotivated Ambient Fill

The fastest way to ruin a photorealistic 3D model is adding a uniform world gray background or an unmotivated omni fill light that illuminates every shadow equally. In real cinematography:
- **Every photon has an origin**: A sun disc, a sky dome through a window opening, a softbox diffuser, an LED panel, a tungsten bulb, or light bouncing off a concrete floor.
- **Shadows create form**: Without dark shadow valleys and negative fill, objects lose three-dimensional volume.

## 2. Three-Point Physical Studio Rig (Starting Values)

Run [`../scripts/setup_studio_lighting.py`](../scripts/setup_studio_lighting.py) to construct this calibrated rig automatically around any subject of radius $R$:

| Light Role | Light Type & Physical Size | Position Relative to Subject & Camera | Kelvin (`Blackbody`) | Relative Exposure / Ratio |
|---|---|---|---|---|
| **1. Key Light** | `AREA` (`Rectangle`, `1.2 R x 0.9 R`, `Spread = 95 deg`) | `35–45 deg` off camera axis, `30–45 deg` elevation, distance `2.5 R` | `4800 K – 5400 K` | `0.0 EV` (`100%` baseline reference; places 18% grey card at middle grey under AgX) |
| **2. Bounce Fill (Passive or Soft Area)** | Physical white matte bounce plane (`0.75` albedo, `2.0 R x 2.0 R`) or large `AREA` (`2.0 R x 1.5 R`) | Opposite side of camera from Key (`-45 to -60 deg`), low elevation (`15 deg`) | `6200 K – 7000 K` (cooler than Key) | `-2.0 to -3.0 EV` (`4:1` to `8:1` key-to-fill ratio) |
| **3. Rim / Kicker Light** | `AREA` (`Strip`, `0.3 R x 1.2 R`, `Spread = 60 deg`) | Behind subject (`135–160 deg` from camera), grazing top/side bevels | `5200 K – 5800 K` | `-0.5 to +0.5 EV` (tuned to separate dark silhouette edges from background) |
| **4. Negative Fill Flag** | Black matte cutter card (`0.03` albedo, `1.5 R x 2.0 R`) | Placed close (`0.8 R`) to the shadow side of glossy/metallic subjects | N/A (absorbs bounce) | Carves deep dark reflections into chrome, glass, and curved hulls |

## 3. Practical Lamps & IES Profiles

When a lamp, monitor, or neon strip is visible inside the camera frame ("a practical"):
1. **Separate Visible Emitter from Illuminating Area Light**:
   - Give the visible bulb filament or frosted glass tube a `Principled BSDF` / `Emission` shader strong enough to read nicely under AgX without fireflies (`Strength = 5.0 – 25.0`, starting value).
   - Place a physical `AREA` or `POINT` light (`radius >= 0.04 m`, `Camera Ray Visibility = False`) right outside the fixture to cast clean, low-noise illumination into the room.
2. **IES Photometric Profiles for Architectural Downlights**:
   - Real recessed ceiling cans do not emit a uniform hemisphere; their internal baffles produce scalloped hyperbolic light cones on nearby walls. Attach an `IES Texture` node (`Strength` scaled to lumens/watts) to architectural spot/point lights.
