---
name: ultraskill-ai-physics
description: Game AI decision architecture (Behavior Trees, Utility AI, Blackboard, Squad Attack Tokens), NavMesh pathfinding and local steering avoidance, 32-layer collision matrices, and stable ragdolls/raycast vehicles.
---

# 23 — AI & Physics Systems

This skill builds legible, tactical game AI and deterministic physics queries that run comfortably inside a **`2.0 ms` AI + `2.5 ms` Physics CPU budget** at 60 FPS on a 4 GB RAM laptop.

## When to use

- Designing enemy or companion AI using Behavior Trees (BT), Utility scoring, and shared Blackboards.
- Preventing "dogpiling" (10 enemies swinging simultaneously) via Squad Attack Token coordination.
- Setting up NavMesh baking, time-sliced path queries, and local steering/avoidance (RVO / context steering).
- Auditing or generating the 32-layer physics collision matrix and raycast/shapecast query masks.
- Implementing sleep-managed ragdolls or stable 4-wheel raycast vehicles.

## Inputs

- Enemy archetypes, combat roles, and spatial arena metrics from `skills/20-game-design/`.
- Character controller capsule dimensions (`radius = 0.4 m`, `height = 1.8 m`) from `skills/22-gameplay-systems/`.

## Steps

1. **Design the AI Decision Architecture**:
   - Choose a Behavior Tree (structured tactical sequences) or Utility AI (multi-need scoring) backed by a per-agent + squad Blackboard following [references/behavior-trees-and-utility-ai.md](references/behavior-trees-and-utility-ai.md) and [templates/behavior_tree_core.py](templates/behavior_tree_core.py).
2. **Enforce Squad Attack Tokens & Perception Slicing**:
   - Limit simultaneous melee attackers via a squad token pool (`max_tokens = 2`) and stagger line-of-sight perception raycasts across ticks (`10 Hz` per agent).
3. **Configure NavMesh & Local Steering**:
   - Bake navigation meshes matching agent capsule radius (`0.45 m` padded), throttle `get_next_path_position()` recalculations to `4–5 Hz`, and blend context-steering separation forces using [references/navigation-and-steering.md](references/navigation-and-steering.md).
4. **Generate the Collision Layer Matrix**:
   - Assign dedicated physics layers for `WorldStatic`, `PlayerBody`, `EnemyBody`, `PlayerHitbox`, `PlayerHurtbox`, `EnemyHitbox`, `EnemyHurtbox`, `Projectiles`, `Interactables`, and `CameraProbe` using [references/collision-layers-and-queries.md](references/collision-layers-and-queries.md) and [scripts/collision_matrix_gen.py](scripts/collision_matrix_gen.py).
5. **Stabilize Ragdolls & Vehicles**:
   - Enforce joint twist/swing limits, auto-sleep ragdolls after `2.5 s`, and use spring-damper raycast suspension for vehicles following [references/ragdolls-and-vehicles.md](references/ragdolls-and-vehicles.md).

## Numbers and defaults

| Parameter | Default Value | Tolerance / Notes |
|---|---|---|
| AI Perception Tick Rate | `10 Hz` (`100 ms` staggered across agents) | Never raycast line-of-sight for all 20 enemies on the same frame |
| NavMesh Path Recalc Rate | `4 Hz` (`250 ms`) | Or when target moves `> 1.5 m` from last path destination |
| NavMesh Agent Radius / Height | `0.45 m` / `1.85 m` | `+0.05 m` margin over physics capsule (`0.40 m` / `1.80 m`) |
| Squad Melee Attack Tokens | `2` concurrent tokens | Remaining enemies strafe at `4.5–6.5 m` ring until token frees |
| Vision Cone (FOV / Range) | `110°` horizontal / `18.0 m` | Close proximity sense `2.5 m` (`360°`) |
| Max Active Ragdolls (LOW Preset) | `3` concurrent ragdolls | Sleep and freeze physics joints after `2.5 s` or `< 0.08 m/s` |
| Vehicle Suspension Natural Freq | `1.8 – 2.4 Hz`, Damping Ratio `0.75` | Critical-ish damping prevents endless pogo oscillation |

## Failure modes and fixes

- **Symptom**: Frame time spikes by `+6 ms` every time a wave of 16 enemies spawns.
  - **Fix**: All 16 agents were initialized with `timer = 0.0`, causing their `10 Hz` perception raycasts and `4 Hz` NavMesh A* path queries to fire on the exact same physics tick. Initialize each agent's tick offset to `(agent_index % 6) * dt`.
- **Symptom**: Enemies snag on wall corners when following a NavMesh path.
  - **Fix**: Increase NavMesh `agent_radius` during baking to at least `capsule_radius + 0.05 m` (`0.45 m`) so path waypoints never hug raw geometry edges.
- **Symptom**: Eight melee enemies stack on top of the player and swing simultaneously, killing the player in 1 frame.
  - **Fix**: Implement a Squad Coordinator with `2` melee attack tokens and a local separation steering vector (`radius = 1.6 m`).
- **Symptom**: Ragdoll limbs explode or jitter violently when wedged against a wall.
  - **Fix**: Ensure adjacent ragdoll bones have self-collision disabled, clamp angular limits to anatomical ranges (`<= 45°–80°`), and freeze ragdoll bodies to static meshes after `2.5 s`.

## Done check

- [ ] AI perception and NavMesh repathing are time-sliced across frames (`<= 2.0 ms` total AI CPU budget).
- [ ] Squad coordinator enforces a maximum of `2` simultaneous melee attackers with clear attack telegraphs.
- [ ] Physics collision layers separate movement capsules from combat Hitboxes and Hurtboxes.
- [ ] `python3 skills/23-ai-physics/scripts/collision_matrix_gen.py --self-test` and `python3 skills/23-ai-physics/templates/behavior_tree_core.py --self-test` exit with code `0`.

## Related files

- [references/behavior-trees-and-utility-ai.md](references/behavior-trees-and-utility-ai.md)
- [references/navigation-and-steering.md](references/navigation-and-steering.md)
- [references/collision-layers-and-queries.md](references/collision-layers-and-queries.md)
- [references/ragdolls-and-vehicles.md](references/ragdolls-and-vehicles.md)
- [templates/behavior_tree_core.py](templates/behavior_tree_core.py)
- [scripts/collision_matrix_gen.py](scripts/collision_matrix_gen.py)
