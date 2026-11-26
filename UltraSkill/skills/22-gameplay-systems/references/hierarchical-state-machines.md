# Hierarchical State Machines (HSM)

Replacing nested `if is_jumping and not is_attacking and not is_stunned and stamina > 0:` booleans with an explicit State Machine eliminates impossible state combinations (e.g., attacking while dead or sliding while playing the idle animation).

---

## 1. Flat FSM vs Hierarchical State Machine (HSM)

In a flat Finite State Machine, shared transitions (e.g., taking stagger damage while in `Idle`, `Walk`, `Run`, or `Jump`) must be duplicated across every state. An **HSM** groups sub-states under parent super-states:

```text
RootActorState
├── Alive
│   ├── Grounded (handles Jump input & floor loss -> Airborne)
│   │   ├── Idle
│   │   ├── Move (Walk / Sprint)
│   │   └── Crouch
│   ├── Airborne (handles landing -> Grounded)
│   │   ├── JumpAscent
│   │   └── FallDescent
│   └── CombatAction (locks normal locomotion)
│       ├── AttackCombo1
│       ├── AttackCombo2
│       └── DodgeRoll (grants i-frames)
├── Staggered (auto-returns to Grounded/Airborne after stun timer)
└── Dead (terminal state; disables hurtbox)
```

---

## 2. State Lifecycle Contract

Every state object implements five deterministic methods:

1. `enter(prev_state: StringName, msg: Dictionary = {}) -> void`:
   - Trigger animations, reset state-local timers, enable/disable specific hitboxes or i-frames.
2. `exit(next_state: StringName) -> void`:
   - Guaranteed cleanup hook: always disable active weapon hitboxes and restore altered collision masks here so interrupted attacks never leave a permanent active hitbox.
3. `handle_input(event: InputEvent) -> void`:
   - Process discrete buffered actions.
4. `update(dt: float) -> void`:
   - Visual/cosmetic per-frame updates.
5. `physics_update(dt: float) -> void`:
   - Kinematic velocity calculation and transition checks.

---

## 3. State Transition Rules & Guard Invariants

1. **Single Transition Per Tick**:
   - If `physics_update` triggers `transition_to("DodgeRoll")`, return immediately (`return`) after calling `transition_to()` so remaining lines in the old state do not overwrite the new state's velocity.
2. **Guaranteed `exit()` Cleanup**:
   - Even when an external event forces an interrupt (`apply_stagger()`), the state machine must route through `current_state.exit("Staggered")` before entering `Staggered`.
3. **Transition History Ring Buffer**:
   - Keep the last `8` transitions (`[prev_state, next_state, tick_number]`) in a ring buffer on the state machine. When debugging a movement or combat bug, printing the last 8 state transitions pinpoints the exact frame an invalid transition fired.
