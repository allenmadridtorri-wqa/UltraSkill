# Three.js Lighting, PMREM Environments & AgX Tone Mapping

## 1. Aligning Three.js Color Management with Blender Cycles AgX

To make `.glb` assets exported from Blender look consistent inside Three.js (r160+):

```javascript
import * as THREE from "three";

renderer.outputColorSpace = THREE.SRGBColorSpace;
// Prefer AgXToneMapping (available in modern Three.js); fall back to ACESFilmicToneMapping
renderer.toneMapping = THREE.AgXToneMapping ?? THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
```

## 2. Image-Based Lighting (IBL) via `PMREMGenerator`

Never light a PBR `MeshStandardMaterial` using only a `DirectionalLight` and an `AmbientLight`—metals (`metalness = 1.0`) have zero diffuse component and appear **pitch black** without an environment reflection map (`scene.environment`).

### Generating a Low-Memory Procedural or HDRI Environment Map
If loading an external `.hdr` file is too heavy for a fast web boot, generate a physical studio/room environment texture procedurally in `< 5 ms` using `THREE.RoomEnvironment` or a small equirectangular canvas passed through `PMREMGenerator`:

```javascript
import * as THREE from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

export function applyStudioEnvironment(renderer, scene) {
  const pmremGenerator = new THREE.PMREMGenerator(renderer);
  pmremGenerator.compileEquirectangularShader();
  const roomEnv = new RoomEnvironment();
  const envRenderTarget = pmremGenerator.fromScene(roomEnv, 0.04);
  scene.environment = envRenderTarget.texture;
  // Dispose intermediate setup objects immediately to free VRAM
  roomEnv.dispose?.();
  pmremGenerator.dispose();
  return envRenderTarget;
}
```

## 3. Direct Light & Shadow Map Discipline

Every active light in Three.js adds a loop iteration to every fragment shader in the scene, and every shadow-casting light re-renders the scene geometry from the light's viewpoint:
- **`LOW` Preset**: `0` shadow-casting lights (`renderer.shadowMap.enabled = false`). Use `1` `HemisphereLight` (sky/ground bounce) + `1` non-shadow `DirectionalLight` for specular catchlights, paired with baked Cycles lightmaps (`material.lightMap`) or a soft fake shadow decal plane under moving objects.
- **`MEDIUM` / `HIGH` Preset**: At most **`1` shadow-casting `DirectionalLight` or `SpotLight`**. Tighten the orthographic shadow camera frustum (`light.shadow.camera.left/right/top/bottom = +-8.0 m`, `near = 0.5`, `far = 25.0`, `bias = -0.0005`, `normalBias = 0.02`) so `100%` of the `1024x1024` or `2048x2048` shadow map covers the visible play area.
