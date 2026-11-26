# Camera Controls, Collision Bounds & Fast Raycasting

## 1. Damped Camera Controls & Physical Bounds

Never leave raw `OrbitControls` unrestricted so the user can orbit underneath the floor plane (`y < 0.05 m`) or zoom `500 meters` outside the room walls into a black void:

```javascript
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 0.8;         // Prevent clipping inside hero prop near-plane
controls.maxDistance = 9.5;         // Keep camera inside room enclosure
controls.minPolarAngle = 0.25;      // ~14 deg from ceiling
controls.maxPolarAngle = Math.PI * 0.48; // Prevent dipping below floor (90 deg = horizon)
```

For first-person or story-driven cameras (`18-interactive-story`), clamp the camera's world `(X, Y, Z)` inside an Axis-Aligned Bounding Box (`THREE.Box3`) inset by `0.25 m` from room walls (`camera.near = 0.1 m`, `camera.far = 100.0 m`; keeping `far / near <= 1000` prevents 24-bit Z-buffer depth fighting!).

## 2. Fast Raycasting Without Main-Thread Stalls

Calling `raycaster.intersectObjects(scene.children, true)` on every `pointermove` event traverses every triangle of every decorative mesh in the scene on the CPU—causing `25–80 ms` frame hitches on a 4 GB laptop.

### Three-Rule Raycast Optimization Contract
1. **Dedicated Interaction Layer (`Layer 1`) + Invisible Box Proxies**:
   - Leave high-poly visual meshes on `Layer 0` only.
   - Create a simple 12-triangle `BoxGeometry` or `SphereGeometry` collider proxy around each interactive prop, enable `proxy.layers.enable(1)`, and configure `raycaster.layers.set(1)`.
   - Now `raycaster.intersectObjects(interactiveProxies, false)` checks **60 triangles total** (`< 0.03 ms`!) instead of 150,000 visual triangles.
2. **Throttle Hover Raycasts to `<= 30 Hz` (`33 ms`)**:
   - Store the latest normalized pointer coordinates `(ndcX, ndcY)` inside the `pointermove` listener without running the raycast immediately.
   - Run the hover raycast at most once every `2` render frames (`30 Hz`) inside the main loop only if the pointer actually moved (`|dx| + |dy| > 0.001`).
3. **Always Provide Keyboard (`Tab` / `1..9` / `Enter`) Selection Fallback**:
   - Never rely exclusively on 3D canvas mouse picking; mirror every interactive 3D hotspot as an accessible HTML `<button>` or keyboard shortcut so both screen readers and automated browser tests can trigger interactions deterministically.
