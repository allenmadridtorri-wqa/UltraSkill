---
name: ultraskill-gameplay-systems
description: Responsive character controllers, coyote time and jump buffering, collision-aware cameras, hitbox/hurtbox combat with hit-stop, hierarchical state machines, inventory, quests, dialogue, and spawning.
---

# 22 — Gameplay Systems

This skill builds the moment-to-moment player mechanics that determine "game feel": sub-frame responsive movement, frustration-free jumping, non-clipping 3D cameras, crisp combat hit detection, hierarchical state machines, and data-driven inventory/quest/dialogue pipelines.

## When to use

- Implementing 2D or 3D character movement, jumping, dashing, slopes, and ledges.
- Building third-person orbit or first-person look cameras with spring-arm collision recovery.
- Implementing melee or ranged combat with separate Hitbox/Hurtbox layers, hit-stop, and knockback.
- Structuring player or enemy logic using a Hierarchical State Machine (HSM).
- Building action-mapped input abstraction with input buffering (`120 ms` queue).
- Designing data-driven inventory items, quest state graphs, dialogue trees, or wave spawners.

## Inputs

- Core loop and spatial metrics from `LEVEL_METRICS.md` ([../20-game-design/templates/LEVEL_METRICS.md](../20-game-design/templates/LEVEL_METRICS.md)).
- Target physics tick rate (`60 Hz`, `dt = 0.01667s`) from [../21-engine-architecture/references/game-loop-and-time.md](../21-engine-architecture/references/game-loop-and-time.md).
- Combat and item stat tables (`.json` or `.csv`).

## Steps

1. **Configure Input Abstraction & Buffering**:
   - Bind logical actions (`move_left`, `move_right`, `jump`, `attack`, `dodge`, `interact`) rather than physical keycodes, and maintain a rolling input buffer (`120 ms`) following [references/input-abstraction-and-buffering.md](references/input-abstraction-and-buffering.md).
2. **Build the Character Controller**:
   - Implement acceleration/deceleration curves, coyote time (`100 ms`), jump buffering (`120 ms`), variable jump height, and slope snapping (`max_angle = 45°`) using [references/character-controller-physics.md](references/character-controller-physics.md) and [templates/character_controller.gd](templates/character_controller.gd).
3. **Rig the Game Camera**:
   - Decouple camera rotation from physics jitter, apply critically damped smoothing, and enforce spring-arm wall collision whiskers using [references/game-camera-systems.md](references/game-camera-systems.md).
4. **Structure Gameplay States**:
   - Organize locomotion and action states (`Idle`, `Move`, `Airborne`, `Attack`, `Dodge`, `Stagger`) in a clean state machine using [references/hierarchical-state-machines.md](references/hierarchical-state-machines.md) and [templates/state_machine.gd](templates/state_machine.gd).
5. **Implement Combat Hitboxes & Game Feel**:
   - Separate `Hitbox` (deals damage) and `Hurtbox` (receives damage) collision layers, enforce explicit startup/active/recovery frame windows, and add hit-stop (`50–80 ms`) using [references/combat-hitboxes-and-game-feel.md](references/combat-hitboxes-and-game-feel.md).
6. **Wire Progression & World Systems**:
   - Build immutable item definitions and stackable slots ([references/inventory-and-items.md](references/inventory-and-items.md)), event-driven quest objectives ([references/quest-and-objective-systems.md](references/quest-and-objective-systems.md)), branching dialogue ([references/dialogue-and-interaction.md](references/dialogue-and-interaction.md)), and deterministic checkpoints ([references/spawning-and-checkpoints.md](references/spawning-and-checkpoints.md)).
7. **Audit Stat Tables**:
   - Validate all weapon, enemy, and item tables with [scripts/verify_stat_tables.py](scripts/verify_stat_tables.py).

## Numbers and defaults

| Parameter | Default Value | Tolerance / Notes |
|---|---|---|
| Ground Acceleration / Friction | `45.0 m/s²` / `38.0 m/s²` | Reaches `7.0 m/s` top speed in `~155 ms` (9 frames) |
| Air Control Multiplier | `0.65x` ground accel | Preserves jump momentum while allowing mid-air correction |
| Coyote Time Window | `100 ms` (`6` frames @ 60Hz) | Grace jump after walking off a ledge |
| Jump Buffer Window | `120 ms` (`7` frames @ 60Hz) | Early jump press triggers on landing frame |
| Gravity (Ascent / Descent) | `24.0 m/s²` / `36.0 m/s²` | `1.5x` fall gravity prevents floaty jumps |
| Variable Jump Cut Multiplier | `0.45x` vertical velocity | Applied when jump button is released early while `vy > 0` |
| Max Walkable Slope | `45°` | Snap length `0.25 m` prevents hopping down ramps |
| Hit-Stop Duration (Light / Heavy) | `45 ms` / `85 ms` | Freezes attacker + victim animation/physics on impact |
| Camera FOV (3rd Person / 1st Person) | `65°–75°` vertical (`90°–105°` horiz) | Sprint FOV boost `+6°` over `250 ms` |

## Failure modes and fixes

- **Symptom**: Jumping feels floaty and unresponsive.
  - **Fix**: Do not use real-world `9.8 m/s²` gravity for action games. Derive `gravity = (2 * jump_height) / (time_to_apex²)` (typically `22–30 m/s²` up, `34–45 m/s²` down) and apply `0.45x` velocity cut on early button release.
- **Symptom**: Player misses jumps at platform edges or when pressing jump 2 frames before landing.
  - **Fix**: Add `coyote_timer = 0.10` (counts down after leaving floor without jumping) and `jump_buffer_timer = 0.12` (triggers jump immediately on `is_on_floor()`).
- **Symptom**: One melee swing damages the same enemy 8 times across an 8-frame active window.
  - **Fix**: Maintain a `_hit_targetsThisSwing: Array[int]` set on the `Hitbox`; clear it when the attack state enters startup and ignore any `Hurtbox` whose owner ID is already in the set.
- **Symptom**: Camera clips through walls when backing into a corner.
  - **Fix**: Use a `SpringArm3D` with a sphere shape probe (`radius = 0.22 m`) rather than a single zero-thickness raycast.

## Done check

- [ ] Character controller implements coyote time (`100 ms`), jump buffer (`120 ms`), asymmetric fall gravity, and slope snapping (`45°`).
- [ ] State machine transitions deterministically with explicit `enter()`, `exit()`, and `physics_update(dt)` hooks.
- [ ] Hitboxes track already-hit entities per swing and trigger hit-stop + damage events without multi-hitting.
- [ ] `python3 skills/22-gameplay-systems/scripts/verify_stat_tables.py --self-test` exits with code `0`.

## Related files

- [references/character-controller-physics.md](references/character-controller-physics.md)
- [references/game-camera-systems.md](references/game-camera-systems.md)
- [references/combat-hitboxes-and-game-feel.md](references/combat-hitboxes-and-game-feel.md)
- [references/hierarchical-state-machines.md](references/hierarchical-state-machines.md)
- [references/input-abstraction-and-buffering.md](references/input-abstraction-and-buffering.md)
- [references/inventory-and-items.md](references/inventory-and-items.md)
- [references/quest-and-objective-systems.md](references/quest-and-objective-systems.md)
- [references/dialogue-and-interaction.md](references/dialogue-and-interaction.md)
- [references/spawning-and-checkpoints.md](references/spawning-and-checkpoints.md)
- [templates/character_controller.gd](templates/character_controller.gd)
- [templates/state_machine.gd](templates/state_machine.gd)
- [scripts/verify_stat_tables.py](scripts/verify_stat_tables.py)
