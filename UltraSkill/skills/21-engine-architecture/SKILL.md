---
name: 21-engine-architecture
description: >-
  Game engine architecture skill for Godot 4 (default FOSS Compatibility mode
  for 4 GB laptops), custom web/native engines, fixed-timestep game loops, ECS
  vs scene hierarchies, asynchronous asset streaming, object pooling, event
  buses, and schema-versioned save serialization.
---

# 21-Engine-Architecture: Loops, Pooling, Scene Trees & Safe Serialization

A solid game architecture separates deterministic `60 Hz` simulation ticks from variable render frame rates, pre-allocates memory pools at load time so 4 GB laptops never hitch during combat, and serializes saves safely without arbitrary code execution.

## When to use

Load this skill whenever choosing a game engine or renderer mode, structuring a project's node/ECS hierarchy, designing the main loop and time dilation (hitstop/pause), building object pools or asset loaders, or implementing versioned save files.

## Inputs

- `GDD_ONE_PAGER.md` and `LEVEL_METRICS.md` from `20-game-design`.
- Hardware floor: **4 GB RAM laptop with 1 GB Intel UHD integrated graphics** (plus GitHub Actions for cloud Windows builds).

## Steps

1. **Select the Engine & Renderer Mode Matching the Hardware Constraint**:
   - Follow [`references/engine-selection-and-hardware.md`](references/engine-selection-and-hardware.md): default to **Godot 4.x locked to the `gl_compatibility` renderer** (or **Three.js / WebGL** for browser-native delivery). State the exact hardware requirements (`16–32 GB RAM`, dedicated RTX/Radeon GPU) if the user asks for Unreal Engine 5 or Unity HDRP.
2. **Enforce Fixed-Timestep Simulation (`60 Hz`) + Render Interpolation**:
   - Follow [`references/game-loop-and-time.md`](references/game-loop-and-time.md): run physics, movement, hitboxes, and AI inside the fixed `60 Hz` (`16.67 ms`) step (`_physics_process(delta)`), clamp maximum frame delta at `100 ms` (`0.1 s`) to prevent spiral-of-death lag spikes, and isolate hitstop time dilation from UI/menu clocks.
3. **Structure Composition Over Deep Inheritance**:
   - Follow [`references/ecs-vs-scene-hierarchy.md`](references/ecs-vs-scene-hierarchy.md) and [`references/event-bus-and-decoupling.md`](references/event-bus-and-decoupling.md): compose entities from focused child components (`HealthComponent`, `HitboxComponent`, `VelocityComponent`, `StateMachine`) communicating via typed signals rather than 6-level inheritance chains or brittle `get_node("../../..")` paths.
4. **Pre-Allocate Object Pools & Stream Assets Asynchronously**:
   - Follow [`references/memory-management-and-pooling.md`](references/memory-management-and-pooling.md) and [`references/asset-pipeline-and-streaming.md`](references/asset-pipeline-and-streaming.md): pre-warm fixed pools for projectiles, damage numbers, and spark particles at arena load so zero `instantiate()` calls or GC spikes occur during active combat.
5. **Implement Atomic, Schema-Validated Save Serialization**:
   - Follow [`references/serialization-and-save-migrations.md`](references/serialization-and-save-migrations.md) and validate all save files and forward migration paths with `python3 skills/21-engine-architecture/scripts/save_schema_validator.py`.

## Numbers and defaults

All values below are **starting values**:

| Architectural Parameter | Starting Value | Verification Method |
|---|---|---|
| **Fixed Physics Tick Rate** | `60 Hz` (`dt = 0.016667 s`, `max_physics_steps_per_frame = 4`) | `project.godot` / loop accumulator |
| **Godot 4 Renderer (4 GB Laptop)** | `renderer/rendering_method = "gl_compatibility"` | `project.godot` check |
| **Process RAM Ceiling (4 GB Laptop)** | `<= 1,200 MB` RSS (`<= 256 MB` VRAM textures) | OS process monitor / profiler |
| **Projectile / VFX Object Pool Size** | `64` projectiles, `32` floating damage labels, `48` impact bursts pre-allocated | Inspect pool init count |
| **Max Frame Delta Clamp** | `0.100 s` (`100 ms` cap before accumulator division) | Game loop source inspection |
| **Save File Format** | Pure versioned JSON (`schema_version: 1`) + SHA-256 integrity hash written via atomic `.tmp` rename | `save_schema_validator.py` |

## Failure modes and fixes

- **Godot 4 defaults to `forward_plus` (Vulkan) and crashes or crawls at 8 FPS on old Intel UHD drivers**: Always set `rendering/renderer/rendering_method="gl_compatibility"` and `rendering/renderer/rendering_method.mobile="gl_compatibility"` in `project.godot` for the 4 GB laptop baseline.
- **Loading a malicious `.tres` Godot Resource save file executes embedded GDScript**: Never use `ResourceLoader.load("user://save.tres")` for player save files—`.tres` files can contain inline `GDScript` sub-resources that execute arbitrary code on load! Always serialize saves as strict JSON verified by `save_schema_validator.py`.
- **120 ms frame hitch every time an enemy fires a burst of bullets**: `PackedScene.instantiate()` and shader compilation ran on the first shot. Pre-allocate a 64-slot ring pool and render 1 hidden warmup particle at scene boot.

## Done check

- Engine config defaults to `gl_compatibility` / `LOW` preset with `60 Hz` fixed physics.
- Hot update loops contain zero per-frame allocations or un-pooled instantiations.
- `save_schema_validator.py` exits with code `0` on current and legacy v1->v2 save payloads.

## Related files

- [`references/engine-selection-and-hardware.md`](references/engine-selection-and-hardware.md)
- [`references/game-loop-and-time.md`](references/game-loop-and-time.md)
- [`references/ecs-vs-scene-hierarchy.md`](references/ecs-vs-scene-hierarchy.md)
- [`references/asset-pipeline-and-streaming.md`](references/asset-pipeline-and-streaming.md)
- [`references/memory-management-and-pooling.md`](references/memory-management-and-pooling.md)
- [`references/event-bus-and-decoupling.md`](references/event-bus-and-decoupling.md)
- [`references/serialization-and-save-migrations.md`](references/serialization-and-save-migrations.md)
- [`scripts/save_schema_validator.py`](scripts/save_schema_validator.py)
