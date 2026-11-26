# Spatial 3D Triggers, Look-At Cones & Accessible Hotspots

## 1. Dual-Criteria Spatial Activation (Distance + View Cone)

In a 3D walkable or orbitable story scene, an interaction prompt ("Inspect Chronometer `[E]`") should activate only when **both** proximity and camera look direction agree:

$$d = \|\vec{P}_{\text{hotspot}} - \vec{P}_{\text{camera}}\| \le R_{\text{interact}}, \qquad \frac{(\vec{P}_{\text{hotspot}} - \vec{P}_{\text{camera}}) \cdot \vec{F}_{\text{camera}}}{d} \ge \cos(\theta_{\text{cone}})$$

- **Starting values**:
  - $R_{\text{interact}} = 2.4\text{ m}$ (for room-scale inspection) or $6.0\text{ m}$ (for orbit-camera table scenes).
  - $\theta_{\text{cone}} = 35^\circ$ ($\cos 35^\circ \approx 0.819$).
  - When multiple hotspots satisfy the inequality simultaneously, score each candidate by $S = \frac{\cos\theta}{d}$ and highlight only the single highest-scoring hotspot.

## 2. Synchronized 3D World-to-Screen HTML Overlay Buttons

Never draw interaction labels onto a 3D texture inside the WebGL canvas:
1. Small text inside a 720p `LOW` preset canvas blurs and cannot be read by screen readers or clicked by automated accessibility snapshots.
2. Project the 3D hotspot's world coordinate $\vec{P}_{\text{world}}$ into Normalized Device Coordinates (NDC) once per frame and position a native HTML `<button class="hotspot-marker" aria-label="Inspect Chronometer">` over the canvas:

```javascript
export function projectWorldToScreen(worldVec3, camera, widthPx, heightPx, outVec3) {
  outVec3.copy(worldVec3).project(camera);
  // outVec3.z > 1.0 means the 3D point is behind the camera frustum near/far plane
  const visible = outVec3.z >= -1.0 && outVec3.z <= 1.0;
  const xPx = (outVec3.x * 0.5 + 0.5) * widthPx;
  const yPx = (-outVec3.y * 0.5 + 0.5) * heightPx;
  return { visible, xPx, yPx };
}
```

## 3. Diegetic Visual Cue on the 3D Prop

When a hotspot is hovered or focused via `Tab`, give the 3D prop a subtle physical response in addition to the UI label:
- Pulse a warm rim/emissive highlight (`material.emissiveIntensity = 0.25`) or elevate a small floating ring marker (`+0.04 m`) above the prop so the player sees exactly which physical object in the scene will be examined.
