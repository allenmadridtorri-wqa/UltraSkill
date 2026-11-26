# GLSL Shaders (WebGL2 `#version 300 es`, Three.js, Godot `gdshader`)

Shaders run on the GPU across millions of pixels every 16.67 ms. On the baseline 1 GB Intel UHD integrated GPU, fragment shader discipline determines whether a scene runs at 60 FPS or 15 FPS.

---

## 1. Precision & Uniform Discipline

1. **Explicit Precision Qualifiers (WebGL2 / Mobile)**:
   - Vertex shader: `precision highp float;` (prevents world-position vertex snapping/jitter far from origin).
   - Fragment shader: `precision highp float;` for world lighting / normals, `mediump` (`fp16`) for simple color tints and LUT lookups.
2. **Group Uniforms by Update Frequency**:
   - Global per-frame uniforms (`u_time`, `u_camera_pos`, `u_sun_dir`) belong in shared Uniform Buffer Objects (UBOs) or global shader parameters.
   - Per-instance variations (`hit_flash`, `team_tint`) belong in **Per-Instance Attributes / Uniforms** (`instance uniform vec4` in Godot 4, `attribute vec4 instanceColor` in Three.js) so 200 instanced meshes render in **1 draw call**.

---

## 2. Branchless Math & Anti-Aliased Procedural Edges

1. **Never Use Hard `if (uv.x > 0.5)` Edges in Fragment Shaders**:
   - Hard boolean thresholds (`step(0.5, x)`) create jagged stair-stepped pixel aliasing that shimmers violently when the camera moves.
   - Use screen-space partial derivatives (`fwidth()`) with `smoothstep()` for sub-pixel anti-aliased edges:
   ```glsl
   float aa_step(float threshold, float val) {
       float fw = fwidth(val) * 0.75;
       return smoothstep(threshold - fw, threshold + fw, val);
   }
   ```
2. **Avoid Undefined Math Inputs (`NaN` / `Inf` Poisoning)**:
   - A single `NaN` pixel produced by a fragment shader propagates through the Bloom downsample pyramid and turns the entire screen into a black square!
   - Always clamp before unsafe operations:
     - `pow(max(x, 0.0001), y)` (`pow(0.0, 0.0)` or negative base is undefined in GLSL!).
     - `normalize(v + vec3(1e-6, 0.0, 0.0))` or check `dot(v, v) > 1e-8` before normalizing a difference vector.
     - `clamp(dot(N, L), 0.0, 1.0)`.
