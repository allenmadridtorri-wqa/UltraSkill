# Procedural Scattering & Geometry Nodes Architecture

## 1. Realistic Scatter Rules (Breaking the CG Grid)

Humans and nature never distribute debris, foliage, rocks, or rivets uniformly. When building Geometry Nodes scatter graphs, enforce five realism rules:

1. **Poisson Disk Minimum Distance**: Always use `Distribute Points on Faces` in `POISSON` mode rather than pure `RANDOM` mode so solid props (rocks, trees, bolts) never intersect each other's cores (`Distance Min = 1.2 * object_radius`, starting value).
2. **Cluster Masking (Noise Density Map)**: Multiply the point `Density Factor` by a 2-octave `Noise Texture` passed through a sharp `Map Range` (`from_min = 0.42, from_max = 0.68`) so weeds and pebbles form natural patches with bare clearings in between.
3. **Slope & Cavity Filtering**:
   - Extract the surface `Normal` dot product with world up `(0, 0, 1)`:
     - Dust, snow, and fallen leaves settle only where $\vec{N} \cdot \vec{Z} > 0.75$ (flat upward surfaces).
     - Loose scree and pebbles slide off steep cliffs ($\vec{N} \cdot \vec{Z} < 0.55$) and collect in concave valley troughs.
4. **Blended Normal Alignment**:
   - Rocks and debris align `100%` to the ground surface normal (`Align Euler to Vector -> Z to Normal`).
   - Trees and tall grass grow toward the sun (world `+Z`), not perpendicular to a 40-degree hill. Blend the surface normal and world `(0, 0, 1)` by a factor of `0.15 – 0.30` before aligning rotation.
5. **Scale and Full-360 Z-Rotation Jitter**:
   - Rotate every instance randomly around its local `Z` axis (`0` to `2 * pi` radians), add `+-0.08` rad (`~4.5 deg`) X/Y wobble, and vary uniform scale using a bell-curve or power distribution (`0.65` to `1.35`, with smaller debris outnumbering large hero boulders `8:1`).

## 2. Camera Frustum Culling for Colab T4 VRAM Protection

For large terrain shots, cull scatter points outside the active camera view before `Instance on Points`:
- Transform point positions into camera normalized device coordinates (or check angle against the camera forward vector `dot(normalize(P - CamPos), CamForward) > cos(FOV * 0.65)`).
- Keep all points within `3.0 meters` of the camera even if behind the lens so nearby off-screen objects still cast shadows and appear in glossy reflections.
