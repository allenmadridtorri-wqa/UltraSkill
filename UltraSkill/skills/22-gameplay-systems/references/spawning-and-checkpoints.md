# Spawning and Checkpoints

Wave spawners and checkpoint respawn systems must enforce **hard entity caps** (to protect 60 FPS on 4 GB RAM machines), validate **clearance & line-of-sight** before placing enemies, and restore **consistent world state** on player death.

---

## 1. Wave & Encounter Spawner Architecture

1. **Active Entity Cap**:
   - Enforce `MAX_ACTIVE_ENEMIES = 12` (LOW preset) to `24` (HIGH preset).
   - If a wave definition requests 20 enemies, spawn the first `12` from the `NodePool` and queue the remaining `8` as reinforcements that spawn as active enemies are defeated.
2. **Spawn Point Validation Rules**:
   - **Physics Clearance**: Query a capsule overlap test at the spawn transform before activating the enemy so two enemies never spawn inside each other.
   - **Anti-Pop-In Rule**: Prefer spawn markers that are either outside the player's camera frustum (`dot(cam_forward, dir_to_spawn) < 0.2`), behind an occluder wall, or accompanied by a `0.6s` portal/drop-in telegraph effect.
   - **Minimum Safe Distance**: Never spawn a hostile unit within `5.0 meters` of the player's current position.

---

## 2. Encounter Lock & Arena Gates

When the player enters a combat arena trigger:
1. Move the player inside the threshold before raising arena barriers so the player cannot get trapped inside the barrier collision geometry.
2. Subscribe to `entity_defeated` for all spawned wave units.
3. Include a **Fail-Safe Watchdog Timer** (`every 2.0 seconds`): if an enemy falls out of the world (`position.y < -100.0`) or gets stuck out-of-bounds for `> 10s`, kill or teleport that enemy back into the arena so the arena door never soft-locks shut.

---

## 3. Deterministic Checkpoint Respawn Protocol

When the player dies and respawns at the last activated checkpoint:
1. **What Resets**:
   - Player HP, Stamina, and primary healing charges restored to checkpoint baseline.
   - All uncompleted arena waves reset to un-triggered; all active projectiles and pooled hazards returned to `PoolManager`.
   - Dynamic platforms, elevators, and temporary puzzle switches in the current zone reset to their initial transforms (otherwise an elevator left at the top floor strands a player who respawns at the bottom floor).
2. **What Persists**:
   - Unlocked shortcuts (one-way doors, kicked-down ladders), defeated bosses, opened unique chests, and completed quest flags stored in `world_flags`.
