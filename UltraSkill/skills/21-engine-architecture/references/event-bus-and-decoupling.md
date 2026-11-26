# Event Bus and Decoupling

Hardcoding node paths (`get_node("../../UI/TopBar/HealthBar").update_hp(hp)`) makes scenes brittle: renaming a UI container crashes combat code. Use the **"Call Down, Signal Up"** rule for local hierarchies and a typed **Domain Event Bus** for cross-system communication.

---

## 1. Communication Hierarchy Rules

| Relationship | Mechanism | Example |
|---|---|---|
| **Parent -> Child** | Direct method call (`child.set_weapon(sword)`) | Player controller configuring its child `WeaponMount` |
| **Child -> Parent** | Local Signal (`hitbox.hit_landed.connect(_on_hit)`) | `HitboxComponent` notifying its owning `Enemy` root |
| **Sibling -> Sibling** | Orchestrated by common Parent | Parent receives `HealthComponent.died`, calls `AnimComponent.play_death()` |
| **System -> System** (UI, Audio, Achievements, Analytics) | Typed Global Event Bus (`Events.combat.emit(...)`) | Enemy death updating HUD score, triggering SFX, and advancing quest counter |

---

## 2. Typed Domain Event Bus Architecture

Avoid a single monolithic `EventBus` with 200 untyped signals. Partition events by domain with strict payload contracts:

```gdscript
# autoload/events.gd
extends Node

# Combat Domain
signal damage_dealt(target_id: int, amount: int, is_crit: bool, world_pos: Vector3)
signal entity_defeated(entity_id: int, archetype: StringName, killer_id: int)

# Progression & Economy Domain
signal currency_changed(currency_type: StringName, old_value: int, new_value: int)
signal objective_updated(quest_id: StringName, step_index: int, completed: bool)

# System & Lifecycle Domain
signal quality_preset_changed(preset_name: StringName)
signal pause_state_changed(is_paused: bool)
```

---

## 3. Preventing "Signal Spaghetti" and Infinite Loops

1. **Events Report Facts, Not Commands**:
   - Good: `entity_defeated(entity_id, archetype, killer_id)` (past-tense fact; listeners decide how to react).
   - Bad: `request_open_door_and_play_sound(door_id)` (imperative command disguised as a global event).
2. **No Cascading Mutation Cycles**:
   - Listener A must never emit an event that synchronously triggers Listener B to re-emit Listener A's event.
   - Enforce a recursion depth guard (`MAX_EVENT_DEPTH = 4`) in custom event dispatchers.
3. **Deterministic Listener Cleanup**:
   - In engines without automatic disconnection on destroy (such as JavaScript/TypeScript `EventEmitter`), return an `unsubscribe` closure on registration and call it in `dispose()`:
   ```javascript
   const unsub = eventBus.on("damage_dealt", onDamage);
   // On teardown:
   unsub();
   ```

---

## 4. Service Locator / Dependency Injection Lite

When systems need read access to shared registries (e.g., querying the `AudioDirector` or `SaveManager`), register at most **5–7 global Autoload singletons**:
1. `GameLoop` (Top-level state machine: Boot -> Title -> Playing -> Paused -> GameOver)
2. `Events` (Domain event signals)
3. `SaveManager` (Atomic save/load + schema migrations)
4. `AudioDirector` (Bus mixing, pooled SFX playback, music crossfades)
5. `InputRouter` (Action mapping, device detection, input buffer)
6. `PoolManager` (Shared transient pools for VFX/projectiles)
