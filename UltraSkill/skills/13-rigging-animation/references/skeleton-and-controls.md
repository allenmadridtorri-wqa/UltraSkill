# Skeleton Hierarchy, Joint Orientation & Control Rigs

## 1. Three-Tier Bone Layer Separation

Never animate directly on the deformation bones that hold vertex weights, and never export control curves into a game engine glTF:

| Bone Tier | Naming Prefix | Role | Export to glTF / Godot (`use_deform`) |
|---|---|---|---|
| **1. Deformation Skeleton** | `DEF-` (e.g., `DEF-spine.01`, `DEF-thigh.L`) | Single clean tree rooted at `DEF-root`; holds 100% of vertex skin weights. | `use_deform = True` (Exported) |
| **2. Mechanism / Helper Bones** | `MCH-` (e.g., `MCH-ik_stretch.L`, `MCH-twist_target.L`) | Internal IK chains, pole targets, twist drivers, and parent-switch sockets. | `use_deform = False` (Stripped on export) |
| **3. Animator Controls** | `CTRL-` (e.g., `CTRL-foot_ik.L`, `CTRL-hips`) | Custom wire shapes manipulated by the animator; zero vertex weights. | `use_deform = False` (Stripped on export) |

## 2. Joint Roll & Axis Conventions

Consistent bone roll prevents Gimbal lock and allows left-to-right pose mirroring (`Ctrl+C -> Ctrl+Shift+V`):
- **Primary Hinge Axis (`+X` or `+Z`)**: Recalculate bone roll (`Armature -> Bone Roll -> Recalculate Roll`) so the primary flexion axis of elbows, knees, and finger knuckles points strictly perpendicular to the limb plane.
- **Pre-Bend Angle for IK Solvers**: Never build arms or legs in a mathematically straight `180.00 deg` line in Edit Mode. Give the elbow and knee a `2.0 deg – 4.0 deg` natural bend in the rest pose so the Inverse Kinematics solver always knows which direction to fold without flipping 180 degrees mid-stride.
- **Lock Illegal Anatomical Axes**: Lock `Y` and `Z` Euler rotation on single-axis hinge joints (forearm elbow flexion, finger PIP/DIP knuckles, mechanical hydraulic hinges) so an animator or mocap retargeter cannot hyper-extend a knee sideways.

## 3. Twist Bone Distribution for Limbs

A single bone from elbow to wrist twists the wrist mesh like a candy wrapper when rotating the hand from palm-up to palm-down (`180 deg` pronation/supination):
- Subdivide the forearm deformation bone into `DEF-forearm.01.L` (elbow end) and `DEF-forearm.02.L` (wrist end).
- Drive `DEF-forearm.02.L` with a `DAMPED_TRACK` constraint aiming at the hand bone followed by a `COPY_ROTATION` (`Y` axis only, `Influence = 0.5–0.85`) from the hand bone so pronation twist distributes smoothly along the entire forearm length.
