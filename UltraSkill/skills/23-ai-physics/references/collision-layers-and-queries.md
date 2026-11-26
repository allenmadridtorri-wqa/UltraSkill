# Collision Layers and Physics Queries

Putting every physics body on Layer 1 with Mask 1 causes broadphase O(N²) collision checks, cameras that clip on invisible trigger zones, and projectiles that hit their own shooter's movement capsule.

---

## 1. Standard 12-Layer Collision Architecture

distinguish **Layer** (*"What am I?"*) from **Mask** (*"What do I scan/collide against?"*):

| Bit (1-Indexed) | Layer Name | Layer Bitmask Hex | Active Collision Mask (What it collides with) |
|---|---|---|---|
| **1** | `WorldStatic` (Floors, Walls) | `0x001` | None (Static bodies don't actively scan) |
| **2** | `WorldDynamic` (Crates, Physics Props) | `0x002` | `WorldStatic`, `WorldDynamic`, `PlayerBody`, `EnemyBody`, `Projectiles` |
| **3** | `PlayerBody` (Movement Capsule) | `0x004` | `WorldStatic`, `WorldDynamic`, `EnemyBody`, `Triggers` |
| **4** | `EnemyBody` (Movement Capsule) | `0x008` | `WorldStatic`, `WorldDynamic`, `PlayerBody`, `EnemyBody` |
| **5** | `PlayerHurtbox` (Damage Receiver) | `0x010` | None (Passive receiver scanned by `EnemyHitbox`) |
| **6** | `EnemyHurtbox` (Damage Receiver) | `0x020` | None (Passive receiver scanned by `PlayerHitbox`) |
| **7** | `PlayerHitbox` (Melee / Player Attacks) | `0x040` | `EnemyHurtbox`, `WorldDynamic` (breakable props) |
| **8** | `EnemyHitbox` (Enemy Attacks) | `0x080` | `PlayerHurtbox` |
| **9** | `Projectiles` | `0x100` | `WorldStatic`, `WorldDynamic`, `PlayerHurtbox`, `EnemyHurtbox` |
| **10** | `Interactables` (Doors, Chests, NPCs) | `0x200` | None (Scanned by player interaction raycast) |
| **11** | `Triggers` (Checkpoints, Cutscene Zones) | `0x400` | `PlayerBody` |
| **12** | `CameraOccluder` | `0x800` | None (Scanned by camera spring-arm sphere-cast alongside `WorldStatic`) |

---

## 2. Asymmetric Monitoring Optimization

For `Hurtbox` areas (Layers 5 & 6) and `Interactable` areas (Layer 10):
- Set **`monitorable = true`** (so active Hitboxes and interaction sensors can detect them).
- Set **`monitoring = false`** and **`collision_mask = 0`** (so the engine does not waste CPU running overlap checks from every passive hurtbox every physics tick).

---

## 3. Direct Space State Queries (RayCasts & ShapeCasts)

1. **Always Supply an Explicit Collision Mask**:
   - When casting an AI line-of-sight ray, set `query.collision_mask = LAYER_WORLD_STATIC | LAYER_WORLD_DYNAMIC` (`0x003`). Never let AI sight rays hit invisible trigger volumes or weapon hitboxes.
2. **Continuous Collision Detection (CCD) for Fast Projectiles**:
   - Any projectile traveling faster than `capsule_radius * 2 * 60 Hz = 48.0 m/s` will tunnel through a `0.8 m` thick enemy in a single `16.67 ms` tick if tested only as a point overlap.
   - Instead of spawning heavy `RigidBody3D` nodes with CCD for bullets, step kinematic projectiles via a **Segment Raycast** from `prev_position` to `next_position` every physics tick.
