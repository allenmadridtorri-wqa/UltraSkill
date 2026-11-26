# GPU Instancing, Geometry Merging & Draw-Call Budgets

## 1. Why Draw Calls Kill Integrated Laptop GPUs

Every separate `THREE.Mesh` in a scene triggers a CPU-to-GPU driver state validation and `gl.drawElements()` call. On a 4 GB RAM laptop with an Intel UHD iGPU and dual-core mobile CPU, exceeding **`100 draw calls`** stalls the CPU render thread even if total triangle count is under 20,000.

**Target**: Keep `renderer.info.render.calls <= 50` on the `LOW` preset (`<= 100` hard ceiling).

## 2. Three Techniques to Collapse Draw Calls

| Scenario | Three.js Mechanism | Draw Call Reduction |
|---|---|---|
| **1. Identical Mesh + Identical Material Repeated `N` Times** (pillars, chairs, trees, lamps, crates, particles) | `THREE.InstancedMesh(geometry, material, count)` | Collapses `500` separate meshes into **`1` draw call**; supports per-instance `setMatrixAt(i, mat4)` and `setColorAt(i, color)`. |
| **2. Different Static Meshes Sharing 1 Material / Trim Sheet** (walls, floors, pipes, trim moldings) | `BufferGeometryUtils.mergeGeometries(geometries, false)` | Merges `80` static architectural pieces into **`1` static mesh (`1` draw call)**. |
| **3. Different Meshes Sharing 1 Material That Need Independent Culling/Moving** | `THREE.BatchedMesh(maxInstanceCount, maxVertexCount, maxIndexCount, material)` | Draws distinct geometries in a single multi-draw call while allowing per-submesh visibility and transform updates. |

## 3. Populating `THREE.InstancedMesh` Without Allocations

```javascript
import * as THREE from "three";

export function buildInstancedPillars(geometry, material, transforms) {
  const count = transforms.length;
  const instanced = new THREE.InstancedMesh(geometry, material, count);
  const dummy = new THREE.Object3D();

  for (let i = 0; i < count; i++) {
    const t = transforms[i];
    dummy.position.set(t.x, t.y, t.z);
    dummy.rotation.set(t.rx || 0, t.ry || 0, t.rz || 0);
    dummy.scale.setScalar(t.scale || 1.0);
    dummy.updateMatrix();
    instanced.setMatrixAt(i, dummy.matrix);
  }
  instanced.instanceMatrix.needsUpdate = true;
  instanced.computeBoundingSphere();
  return instanced;
}
```
Always call `instanced.computeBoundingSphere()` after updating instance matrices so Three.js frustum culling does not mistakenly cull the entire batch based on the origin `(0, 0, 0)` bounding sphere!
