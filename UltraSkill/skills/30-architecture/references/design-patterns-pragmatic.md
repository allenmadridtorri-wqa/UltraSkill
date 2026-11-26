# Pragmatic Design Patterns

Design patterns are vocabulary for solving recurring structural problems—never a goal in themselves. Use the simplest construct (often a plain function or dictionary table) that solves the problem cleanly.

---

## 1. High-Value Patterns & Lightweight Idioms

| Pattern | When It Earns Its Keep | Lightweight Implementation (Python / TS / GDScript) |
|---|---|---|
| **Strategy** | Swapping algorithms at runtime (e.g., `LOW`/`MEDIUM`/`HIGH` quality presets, tax/damage calculators, export formats) | A dictionary mapping `mode_name -> callable(ctx)` or a protocol with 1 method |
| **Adapter** | Wrapping a third-party SDK, Blender `bpy`, or OS CLI (`ffmpeg`) behind a narrow internal interface | Thin class translating domain types to external CLI/SDK calls |
| **Command** | Undo/redo stacks, deterministic input replay logs, transactional job queues | Immutable struct `{type, payload, execute(), undo()}` |
| **State Machine** | Player locomotion, network connection lifecycle, order/quest status | Explicit state table with `enter()`, `exit()`, `step()` hooks |
| **Observer / Event Bus** | Decoupling combat/domain facts from UI, audio, and telemetry listeners | Typed signal / pub-sub emitter where payloads are immutable facts |
| **Builder / Options Struct** | Constructing complex configurations with > 5 optional parameters | Typed `dataclass` / `TypedDict` with validated defaults |

---

## 2. Anti-Patterns to Reject Immediately

1. **Speculative Abstract Factory (`AbstractManagerFactoryProvider`)**:
   - Never create an interface or factory when there is only **one** concrete implementation (unless a lightweight fake is required for deterministic offline testing of an external network service).
2. **God Object (`GameManager` / `AppUtils` with 3,000 lines)**:
   - Any class exceeding `400 lines` or touching more than one cohesive state domain must be split by responsibility (`SaveService`, `AudioService`, `EncounterDirector`).
3. **Deep Inheritance Trees (`> 2` levels deep)**:
   - Deep `Entity -> Actor -> Character -> BipedalCharacter -> ArmedEnemy -> BossEnemy` hierarchies break whenever an entity needs half of one branch's behavior (e.g., a stationary turret that needs `ArmedEnemy` targeting without `BipedalCharacter` movement). Prefer **flat composition of data/behavior components**.
