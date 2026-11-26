# Hardware Presets: LOW (4 GB Laptop) to HIGH (Discrete GPU)

## 1. Hard Constraint: The 4 GB RAM / 1 GB Intel UHD Baseline

The user's local machine has **4 GB system RAM and 1 GB Intel UHD integrated graphics** (which shares system RAM bandwidth with the CPU). Any Three.js scene or WebGL app that defaults to `devicePixelRatio = 2.0`, 4K textures, multi-pass EffectComposer bloom/SSAO, and 2048px dynamic shadow cascades will drop to `< 5 FPS` or crash the browser tab.

Every interactive scene must implement [`../templates/quality_presets.json`](../templates/quality_presets.json) and expose a visible preset dropdown (`LOW`, `MEDIUM`, `HIGH`).

## 2. Preset Parameter Contract (Starting Values)

| Parameter | `LOW` (Default on iGPU / <= 4 GB RAM) | `MEDIUM` | `HIGH` |
|---|---|---|---|
| **Max Render Height (`px`)** | `720 px` (clamp canvas internal buffer to `1280x720`) | `1080 px` | Native viewport |
| **`renderer.setPixelRatio()`** | `1.0` | `Math.min(dpr, 1.5)` | `Math.min(dpr, 2.0)` |
| **WebGL Context `antialias`** | `false` | `true` | `true` |
| **WebGL `powerPreference`** | `'low-power'` or `'default'` | `'high-performance'` | `'high-performance'` |
| **Shadow Maps** | `enabled = false` (baked lightmaps + blob decals only) | `enabled = true`, `1` map @ `1024x1024` (`PCFShadowMap`) | `enabled = true`, `2` maps @ `2048x2048` (`PCFSoftShadowMap`) |
| **Material Shader Tier** | `MeshStandardMaterial` (or `MeshLambertMaterial` for distant props) with baked `lightMap` + `aoMap` | `MeshStandardMaterial` with PMREM env map | `MeshPhysicalMaterial` (clearcoat/transmission allowed on hero) |
| **Post-Processing Passes** | `0` (direct `renderer.render(scene, camera)` with `AgXToneMapping`) | Optional 1-pass bloom (`0.5x` resolution) | Bloom + SMAA + subtle vignette |
| **On-Demand Render Mode** | Pause `requestAnimationFrame` when camera and animations are stationary | Continuous `60 Hz` | Continuous `60 Hz` |

## 3. Automatic Hardware Detection Heuristic (`scene_bootstrap.js`)

```javascript
export function detectRecommendedPreset(gl) {
  const memGb = navigator.deviceMemory || 4;
  let rendererStr = "";
  const dbg = gl.getExtension("WEBGL_debug_renderer_info");
  if (dbg) {
    rendererStr = String(gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) || "");
  }
  const isIntegratedOrSoftware = /Intel|UHD|HD Graphics|Iris|SwiftShader|llvmpipe|Mesa/i.test(rendererStr);
  if (memGb <= 4 || isIntegratedOrSoftware) {
    return "LOW";
  }
  if (/RTX|Radeon RX|Apple M[2-9]\s*(Pro|Max|Ultra)/i.test(rendererStr)) {
    return "HIGH";
  }
  return "MEDIUM";
}
```
