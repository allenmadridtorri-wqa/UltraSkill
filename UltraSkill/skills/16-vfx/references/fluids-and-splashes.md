# FLIP Fluids, Splashes, Whitewater & Wetmaps

## 1. Scale & Viscosity Physics

Liquid simulations fail most often because the artist models a coffee cup `2.0 meters` wide. A `2.0 m` wide cup holds `6,000 liters` of water—so its waves slosh like a swimming pool while its droplets look as thin as dust.
- **Rule 1**: Confirm `mesh_linter.py` metric scale (`1.0 unit = 1.0 m`) before adding a Fluid Domain.
- **Rule 2 (Minimum Domain Size in Mantaflow)**: Mantaflow's FLIP solver becomes unstable below `0.15 m` total domain width. For macro tabletop shots (e.g., a `4 cm` whiskey glass), model at `1.0x` scale and set `Domain Time Scale = 0.5` with `CFL Number = 2.0` and `Timesteps Min/Max = 4 / 12` so fast droplets do not tunnel through thin glass walls.

## 2. Calibrated FLIP Liquid Parameters (Starting Values)

| Parameter | Calm Pour / Tabletop | Turbulent Splash / Wave | Purpose |
|---|---|---|---|
| `Resolution Divisions` | `128 – 180` | `192 – 256` | Controls smallest resolvable droplet diameter (`domain_size / divisions`). |
| `Particle Radius` | `1.0 – 1.1` | `0.95 – 1.05` | Lower values (`0.95`) prevent thick "melted jelly" water sheets. |
| `FLIP Ratio` | `0.97` | `0.97` | Balances splashy energetic particles (`1.0`) against smooth PIC viscosity (`0.0`). |
| `Mesh Upres Factor` | `2` (`Concavity Upper = 3.5`) | `2` (`Particle Radius Factor = 1.8`) | Generates the renderable polygon surface from FLIP particles. |
| `Secondary Particles` | `Off` | `Spray + Foam + Bubbles ON` (`Upres = 2`, `Wave Crest Potential = 2.0–8.0`) | High-velocity turbulent water looks like clear plastic without whitewater air bubbles and spray mist. |

## 3. Dynamic Wetmaps (Where Water Touches Dry Stone/Wood)

Water splashing against dry concrete or wood without darkening the contact zone looks completely disconnected:
- Use Blender **Dynamic Paint** (`Canvas` on the rock/floor mesh outputting a `dp_wetmap` vertex color or image sequence; `Brush` on the FLIP fluid mesh with `Paint Distance = 0.015 m`).
- In the rock's `Principled BSDF` shader, use `dp_wetmap` (`0.0` dry -> `1.0` wet) to:
  1. Multiply `Base Color` by `0.38` (wet porous materials darken by `~60%` due to internal total reflection in water-filled pores).
  2. Lerp `Roughness` down to `0.06` and raise `Coat Weight` to `1.0`.
