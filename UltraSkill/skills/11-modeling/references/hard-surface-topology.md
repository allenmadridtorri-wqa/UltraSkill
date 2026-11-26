# Hard-Surface Topology, Booleans & Panel Detailing

## 1. Two Valid Workflows: Sub-D vs Bevel + Weighted Normals

Choose the topology workflow based on whether the surface curves organically in two axes or consists of planar/cylindrical machined faces:

| Workflow | Best For | Rules & Pitfalls |
|---|---|---|
| **1. Bevel Modifier + Weighted Normals (Mid-Poly)** | Architecture, sci-fi corridors, industrial machinery, weapons, crates, furniture. | Keep flat faces as clean N-gons or quads surrounded by a quad support ring; let `Bevel (segments=2..3, harden_normals=True)` + `WeightedNormal (keep_sharp=True)` lock flat face normals so large polygons never bow or shade with dark gradients. |
| **2. Subdivision Surface (`Catmull-Clark`)** | Automotive body panels, aerospace hulls, ergonomic consumer electronics, curved lenses. | All-quad topology (`4` edges per vertex; poles of `3` or `5` edges placed only on flat areas away from curved rim highlights). Never place a 5-pole on a curved specular crest—it creates a permanent star pinch in glossy reflections. |

## 2. Cleaning Up Boolean Cuts on Curved Cylinders

Cutting a hole into a cylinder with a Boolean modifier creates unmatched vertex counts that pinch smooth shading:

1. **Match Cylinder Segment Density to the Cutter**: Before cutting a circular hole of radius $r$ into a cylinder of radius $R$, set the main cylinder segment count so its vertical edges align with the cutter's circumference vertices (`32`, `48`, or `64` segments, starting value).
2. **Isolate the Cut with an Inset Offset Loop**: Select the boolean intersection loop, inset/offset by `1.5 mm – 3.0 mm` (`I` or Bevel weight), and merge any vertices closer than `0.3 mm` (`Merge by Distance`) so the Bevel modifier has a clean quad moat around the hole.
3. **Data Transfer Normals for Hero Curvature**: If shading still wavers around a complex cut on a curved hull, keep an uncut duplicate of the base cylinder hidden from render and project its vertex normals onto the cut mesh using a `DataTransfer` modifier (`Face Corner Data -> Custom Normals`).

## 3. Panel Gaps, Fasteners & Functional Seams

Real manufactured objects cannot be cast as a single monolithic shell—they must be assembled and serviced:
- **Shadow Gaps**: Separate housing shells with a `0.8 mm – 2.0 mm` gap backed by a dark inner lip (`2.0 mm – 4.0 mm` deep). In Cycles path tracing, a real physical recess bounces zero light back, creating an authentic dark seam line that changes thickness with viewing angle (unlike a painted black line).
- **Fastener Scale**: Use standard metric socket head cap screws (`M3 = 5.5 mm` head diameter, `M4 = 7.0 mm`, `M6 = 10.0 mm`, `M8 = 13.0 mm`), instanced via shared mesh data (`obj.data`) and rotated to random angles (`0–360 deg`).
