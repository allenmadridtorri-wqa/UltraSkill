# Three.js Scene Architecture, Lifecycle & Resource Disposal

## 1. WebGL Does Not Garbage-Collect GPU Memory Automatically

In JavaScript, removing a `THREE.Mesh` from the scene (`scene.remove(mesh)`) frees its JS wrapper object, **but its vertex buffers, index buffers, shader programs, and textures remain allocated in GPU VRAM forever** until `.dispose()` is explicitly called. On a 1 GB Intel UHD laptop, two un-disposed scene reloads will trigger `webglcontextlost`.

## 2. Mandatory Recursive Disposal Function

Include this exact disposal utility in every Three.js application (bundled in [`../templates/scene_bootstrap.js`](../templates/scene_bootstrap.js)):

```javascript
export function disposeHierarchy(rootObject) {
  if (!rootObject) return;
  rootObject.traverse((node) => {
    if (node.geometry) {
      node.geometry.dispose();
    }
    if (node.material) {
      const materials = Array.isArray(node.material) ? node.material : [node.material];
      for (const mat of materials) {
        for (const key of Object.keys(mat)) {
          const val = mat[key];
          if (val && typeof val === "object" && typeof val.dispose === "function") {
            val.dispose();
          }
        }
        mat.dispose();
      }
    }
  });
}
```

## 3. Render Loop Hygiene & Zero-Allocation Tick Rules

Never allocate new objects (`new THREE.Vector3()`, `new THREE.Matrix4()`, `new THREE.Color()`, or array `.map()`) inside `requestAnimationFrame`:
- Pre-allocate scratch math primitives at module scope:
  ```javascript
  const _scratchVec3 = new THREE.Vector3();
  const _scratchQuat = new THREE.Quaternion();
  const _scratchMat4 = new THREE.Matrix4();
  ```
- Clamp `delta` time from `THREE.Clock` (`const dt = Math.min(clock.getDelta(), 0.1)`) so switching browser tabs for 30 seconds and returning does not launch physics or camera interpolation across the solar system on the first resumed frame.

## 4. Handling `webglcontextlost` and `webglcontextrestored`

Attach listeners to `renderer.domElement`:
```javascript
renderer.domElement.addEventListener("webglcontextlost", (event) => {
  event.preventDefault();
  cancelAnimationFrame(rafId);
  console.warn("[UltraSkill] WebGL context lost; pausing render loop and switching to LOW preset.");
});
```
