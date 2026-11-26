# Secondary Motion, Overlap & Simulation Baking Rules

## 1. What Needs Secondary Dynamics

Even when a primary character or vehicle animation is rock-solid, rigid attachments (antennas, cables, holsters, coat tails, hair strands, ammo pouches) break realism if they freeze instantaneously when the parent bone stops.

## 2. Three Tiers of Secondary Motion (From Cheapest to Heaviest)

| Tier | Technique | Best For | Runtime & Colab Cost |
|---|---|---|---|
| **Tier 1: Damped-Track / Spring Bone Constraints** | 2–4 bone chain with `DAMPED_TRACK` or baked spring driver (`stiffness = 0.35`, `damping = 0.65`, starting value). | Antennas, ponytails, coat flaps, backpack straps, mechanical hoses, dangling cables. | Near-zero RAM/VRAM; bakes to standard bone keyframes in `< 2 s` via [`../scripts/bake_animation.py`](../scripts/bake_animation.py) and exports directly to glTF / Godot! |
| **Tier 2: Rigid Body Constraints (`GENERIC_SPRING`)** | Low-poly proxy hulls linked by `GENERIC_SPRING` rigid body constraints driving bone transforms. | Heavy vehicle suspension, swinging cranes, hanging chains, destructible signboards. | Bakes in `5–15 s`; deterministic after baking to keyframes. |
| **Tier 3: Cloth & Hair Solver (`Cloth` / `Hair Dynamics`)** | Vertex/curve simulation with collision proxies (`Quality Steps = 12–20`, `Collision Quality = 4–8`, `Distance = 0.002 m`). | Hero capes, loose gowns, flags in wind. | Requires disk point-cache (`.bphys` / Alembic `.abc`) saved to Google Drive before Colab rendering. |

## 3. Collision Proxy Discipline for Cloth

Never collide a 50,000-vertex cloth simulation against a 400,000-triangle subdivided character mesh:
1. Create a sealed, low-poly (`1,500 – 3,000` quad) **Collision Proxy Hull** parented/skinned to the same armature, slightly inflated (`+1.5 mm`) over the render body mesh.
2. Hide the Collision Proxy Hull from camera and shadow rays (`hide_render = True`) and put the Cloth `Collision` modifier exclusively on the proxy hull.
3. This cuts cloth simulation time by `5x to 10x` and prevents thin finger/collar vertices from snagging inside dense character geometry.

## 4. Mandatory Bake-Before-Upload Rule

Google Colab render jobs (`14-blender-pipeline/scripts/render_sequence.py`) jump directly to the first unfinished frame (`scene.frame_set(n)`) on session resume. Any unbaked dynamic spring, rigid body, or cloth modifier evaluated out-of-order at frame `180` will snap to its frame-1 rest state. **Always bake dynamics to explicit keyframes or a disk cache in Google Drive before rendering.**
