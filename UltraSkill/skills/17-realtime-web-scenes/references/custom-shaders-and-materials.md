# Custom GLSL Shaders, `onBeforeCompile` & GPU Cost Discipline

## 1. Prefer `onBeforeCompile` Over Raw `ShaderMaterial` for Lit Surfaces

Writing a standalone `THREE.ShaderMaterial` from scratch loses Three.js fog, PMREM environment reflections, shadow receiving, instancing matrices, and AgX tone-mapping chunks. Whenever you need vertex wind animation, holographic scanlines, or height-based moss blending on a lit object, extend `MeshStandardMaterial` via `material.onBeforeCompile`:

```javascript
import * as THREE from "three";

export function createWindFoliageMaterial(baseOptions, timeUniform) {
  const mat = new THREE.MeshStandardMaterial(baseOptions);
  mat.customProgramCacheKey = () => "ultraskill_wind_foliage_v1";

  mat.onBeforeCompile = (shader) => {
    shader.uniforms.uTime = timeUniform;
    shader.vertexShader = `uniform float uTime;\n` + shader.vertexShader;
    shader.vertexShader = shader.vertexShader.replace(
      "#include <begin_vertex>",
      `
      #include <begin_vertex>
      float swayMask = max(0.0, position.y);
      transformed.x += sin(uTime * 1.8 + position.z * 2.5) * 0.04 * swayMask;
      `
    );
  };
  return mat;
}
```

## 2. Four Shader Rules for 1 GB Intel UHD Survival

1. **Always Define `customProgramCacheKey`**: Without a stable cache key function, Three.js recompiles duplicate GLSL programs for every mesh sharing the `onBeforeCompile` logic, causing a `300 ms – 1500 ms` shader-compilation freeze on load.
2. **Animate via Shared Uniforms on the GPU, Never Vertex Buffer Uploads**:
   - Updating `geometry.attributes.position.needsUpdate = true` every frame copies megabytes of vertex arrays over the PCIe/RAM bus.
   - Instead, mutate a single shared `{ value: elapsedSeconds }` uniform object in JavaScript and compute wave/wind/pulse offsets inside the vertex shader.
3. **Avoid Dynamic Branches & Heavy Raymarching in Fragment Shaders**:
   - On integrated GPUs, a 32-step volumetric raymarching loop executed across `1280x720 = 921,600` pixels requires `29 million` texture/noise evaluations per frame (`< 8 FPS`).
   - Replace per-pixel 3D noise loops with a single pre-baked `256x256` tileable noise texture lookup or compute smooth values in the vertex shader (`varying`) and interpolate across triangles for free.
4. **Minimize Alpha-Blend Overdraw**:
   - Overlapping 15 semi-transparent smoke/particle quads covering the screen forces the iGPU to blend the full frame buffer 15 times (`15x` fill-rate cost). On `LOW` preset, cap overlapping transparent particle quads to `<= 3` layers and trim quad polygons tightly around the opaque sprite core.
