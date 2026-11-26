# Rigid-Body Destruction, Voronoi Fracture & Activation Constraints

## 1. Why Uniform Voronoi Fractures Look Fake

Running a uniform 100-point random Cell Fracture over a concrete pillar produces 100 equal-sized styrofoam cubes that fall apart all at once like a Jenga tower.

### Three Rules of Believable Structural Fracture
1. **Clustered Impact Density**:
   - Concentrate `70%` of fracture seed points within a `0.25 m` radius of the impact point (using a child particle system or grease-pencil/vertex density cloud) and keep outer structural slabs large (`0.40 m – 1.20 m`).
2. **Material-Specific Aspect Ratio (Anisotropy)**:
   - **Concrete / Stone**: Isotropic jagged chunks (`Scale X=1, Y=1, Z=1`) + displaced inner cleavage faces.
   - **Wood Planks / Splinters**: Stretch the fracture object by `8x` along the wood grain axis before fracturing, then scale back by `0.125x` (`Ctrl+A` apply scale after) so Voronoi cells form long fibrous splinters.
   - **Tempered / Laminated Glass**: Radial spiderweb ring vertices combined with tiny `4–8 mm` diced cuboids near the strike center.
3. **Distinct Inner-Face Material (`Material Index = 1`)**:
   - Outer weathered concrete is smooth, painted, or dirty (`albedo 0.35, roughness 0.55`). Freshly fractured interior concrete is brighter, rough, porous, and embedded with aggregate pebbles (`albedo 0.48, roughness 0.85, high micro-bump`). Always assign a second material slot to internal fracture faces.

## 2. Preventing Frame-1 Explosions & Controlling Activation

1. **Zero-Margin Convex Hulls**:
   - Select all shards -> set Rigid Body `Shape = 'CONVEX_HULL'`, `Margin = 0.0004 m` (`0.4 mm`), `Friction = 0.75`, `Bounciness = 0.15`.
2. **Deactivation Until Impact**:
   - Enable `Dynamics -> Deactivation -> Start Deactivated = True` on all shards so the wall stands 100% motionless with zero crack jitter until an active collider (projectile or hidden animated kinetic sphere) strikes it.
3. **Breakable Glue Constraints (`FIXED` Constraints)**:
   - Connect adjacent shards (`Object -> Rigid Body -> Connect -> Type: FIXED`) with `Breakable = True`.
   - Vary `Threshold` by distance from the impact center (`Threshold = 15` at impact core, `85` in mid-zone, `400+` on load-bearing base columns) so a hole punches cleanly through the impact zone while the rest of the wall remains standing.
4. **Bake to Keyframes (`bake_animation.py`)**:
   - Once the rigid-body simulation passes playblast review, run `bpy.ops.rigidbody.bake_to_keyframes()` (or [`../../13-rigging-animation/scripts/bake_animation.py`](../../13-rigging-animation/scripts/bake_animation.py)) so Google Colab renders exact deterministic shard transforms on every frame.
