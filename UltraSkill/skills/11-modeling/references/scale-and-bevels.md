# Metric Scale Enforcement & Physical Bevel Standards

## 1. Why Real-World Metric Scale Is Mandatory

Cycles is a physically based light transport simulator. The following equations break when a scene is modeled at arbitrary scale (e.g., a wristwatch modeled `10 meters` wide or a room modeled `0.2 meters` tall):
- **Subsurface Scattering (`Random Walk`)**: Light mean-free-path inside skin (`~1.0 mm` red channel) is evaluated in scene meters.
- **Volume Absorption & Scatter**: Beer-Lambert attenuation $I(d) = I_0 e^{-\sigma_t d}$ depends directly on ray distance $d$ in meters.
- **Camera Depth of Field**: Circle of confusion $c = \frac{f^2}{N(S_1 - f)} \frac{|S_2 - S_1|}{S_2}$ requires real focal length $f$ (mm) and focus distance $S_1$ (meters).
- **Rigid Body & Fluid Physics**: Gravitational acceleration $g = -9.81\text{ m/s}^2$ looks like slow-motion giant monsters if objects are 10x oversized.

### Standard Metric Reference Dimensions (Starting Values)
- Standard interior door opening: `0.90 m` wide x `2.10 m` high
- Residential ceiling height: `2.40 m – 2.70 m`
- Desk / dining table height: `0.74 m – 0.76 m`
- Chair seat height: `0.45 m`
- Stair riser / tread: `0.175 m` high / `0.28 m` deep
- Standard beverage can: `0.066 m` diameter x `0.122 m` height

## 2. Physical Bevel Radius Table

Never leave a 90-degree polygon corner on a visible hard-surface asset. Use these bevel radii (starting values):

| Material / Manufacturing Process | Bevel Width (`m`) | Millimeters | Segments (Cycles Hero) | Notes |
|---|---:|---:|---:|---|
| Precision CNC metal / watch case / blade spine | `0.0004 – 0.0010` | `0.4 – 1.0 mm` | `3` | High-intensity thin specular catchlight line |
| Stamped sheet metal / electronics chassis | `0.0010 – 0.0025` | `1.0 – 2.5 mm` | `3` | Pair with `1.0 mm` recessed panel seam gaps |
| Injection-molded ABS plastic | `0.0015 – 0.0035` | `1.5 – 3.5 mm` | `3` | Include subtle `0.2 mm` parting line seam |
| Joinery hardwood / furniture edge | `0.0020 – 0.0045` | `2.0 – 4.5 mm` | `3` | Slightly softer highlight along grain |
| Cast iron / structural steel I-beam | `0.0030 – 0.0060` | `3.0 – 6.0 mm` | `3` | Combine with cast bump unevenness |
| Poured architectural concrete / stone curb | `0.0060 – 0.0150` | `6.0 – 15.0 mm` | `3–4` | Displace bevel profile with chipped Voronoi noise |

## 3. Blender Python Setup for Non-Destructive Bevels & Weighted Normals

```python
import bpy

def add_physical_bevel(obj: bpy.types.Object, width_m: float = 0.0015, segments: int = 3) -> None:
    # Ensure scale is applied first so bevel width is isotropic in meters
    bev = obj.modifiers.new(name="PhysicalBevel", type="BEVEL")
    bev.width = width_m
    bev.segments = segments
    bev.limit_method = "ANGLE"
    bev.angle_limit = 0.523599  # 30 degrees in radians
    bev.harden_normals = True
    bev.miter_outer = "MITER_ARC"

    # Ensure smooth shading so hardened bevel normals interpolate cleanly across flat faces
    for poly in obj.data.polygons:
        poly.use_smooth = True
```

Verify all scene objects with [`../scripts/mesh_linter.py`](../scripts/mesh_linter.py).
