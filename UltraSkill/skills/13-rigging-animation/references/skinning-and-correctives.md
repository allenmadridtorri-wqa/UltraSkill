# Skinning, Weight Painting & Corrective Shape Keys

## 1. Disciplined Weight Painting Rules

1. **Auto-Normalize Always On**: The sum of all deformation bone weights on any single vertex must equal `1.000`. Un-normalized weights cause vertices to lag behind the character when the root bone translates across the scene.
2. **4-Bone Influence Cap for Realtime (`glTF 2.0` / Three.js / Godot)**:
   - Standard GPU vertex skinning shaders bind a `vec4 JOINTS_0` and `vec4 WEIGHTS_0` attribute (`4` bones per vertex maximum).
   - Run `bpy.ops.object.vertex_group_limit_total(group_select_mode='BONE_DEFORM', limit=4)` followed by `bpy.ops.object.vertex_group_clean(group_select_mode='BONE_DEFORM', limit=0.005)` and `bpy.ops.object.vertex_group_normalize_all(lock_active=False)`.
3. **Rigid Accessories Must Be `100%` Weighted to One Bone**:
   - Belt buckles, armor plates, buttons, holsters, and eyeglasses must never receive smooth automatic gradient weights from the underlying abdomen or face—otherwise metal buckles bend like rubber during breathing. Assign `1.0` weight to a single socket bone or parent the rigid mesh directly to the bone.

## 2. Linear Blend Skinning vs Dual-Quaternion (`Preserve Volume`)

| Skinning Mode | Where Supported | Behavior & Rule |
|---|---|---|
| **Dual-Quaternion (`armature_mod.use_deform_preserve_volume = True`)** | Offline Blender Cycles OptiX | Prevents joint volume collapse when twisting shoulders, wrists, and hips. Enable on all organic character Armature modifiers in Cycles. |
| **Linear Blend Skinning (`use_deform_preserve_volume = False`)** | Standard Three.js `SkinnedMesh` and Godot 4 glTF imports | Interpolates vertex matrices linearly. Compensate for elbow/knee pinch using twist bones and exported morph-target corrective shape keys. |

## 3. Driver-Controlled Corrective Shape Keys (PSD / Pose-Space Deformation)

Even with clean quad topology, bending an elbow or knee past `90 deg` causes the inner crook to self-intersect and the outer cap (olecranon / patella) to round off:
1. Pose the joint to `115 deg` flexion.
2. Create a new Shape Key (`cor_elbow_bend_115_L`) and sculpt the compressed bicep-forearm contact bulge and sharp bony elbow tip with `CrazySpace` (`Use On Cage` + `Edit Mode` enabled on the Armature modifier).
3. Add a **Driver** to `cor_elbow_bend_115_L.value` reading the Rotational Difference (`ROTATIONAL_DIFF`) between `DEF-upper_arm.L` and `DEF-forearm.L`, mapped via linear generator from `0.0` at `45 deg` (`0.785 rad`) to `1.0` at `115 deg` (`2.007 rad`).
