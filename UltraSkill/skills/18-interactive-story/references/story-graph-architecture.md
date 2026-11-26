# Branching Story Graph Architecture & Guarded State Machines

## 1. Never Hardcode Narrative Branches in Nested `if/else` UI Callbacks

Embedding dialogue strings and branching flags inside UI click handlers or 3D mesh callbacks makes it impossible to check for dead ends, localize strings (`25-ui-audio`), or rewind save states. Represent the entire interactive story as a declarative JSON Directed Graph ([`../templates/story_graph.json`](../templates/story_graph.json)) executed by a pure state machine ([`../templates/story_runtime.js`](../templates/story_runtime.js)).

## 2. The Hub-and-Spoke (Foldback) Graph Topology

Pure binary branching ($2^N$ leaves after $N$ choices) explodes content scope—10 consecutive binary branches require `1,024` unique scenes. Veterans use **Foldback (Diamond / Hub-and-Spoke) Architecture**:

```text
[Start Node]
   ├── Choice A (sets flag: inspected_valve = true, pressure += 10) ──┐
   └── Choice B (sets flag: bypassed_alarm = true)                  ──┼──> [Chokepoint Beat 1]
                                                                               ├── Guarded Branch (requires: inspected_valve == true)
                                                                               └── Default Branch (always available)
```

- **State Variables Carry the Memory**: Instead of duplicating the entire scene graph after a choice, choices mutate typed state variables (`variables: { pressure: 40, has_key: false, trust: 1 }`). Downstream chokepoint nodes inspect those variables to unlock specialized choices, alter camera framing, or select the ending (`ending_intact` vs `ending_breach`).

## 3. Node Schema Contract (`story_graph.json`)

Every node in `nodes` must declare:
- `id` (`string`): Unique snake_case identifier.
- `speaker` (`string`): Speaker or environment label.
- `text` (`string`): `<= 45 words` of concise dialogue or environmental observation.
- `camera_mark` (`string`): Target 3D camera viewpoint ID (`cam_wide`, `cam_chronometer_macro`, `cam_door`).
- `scene_cue` (`string`, optional): Lighting or 3D prop animation trigger (`ignite_warning_lights`, `open_hatch`).
- `terminal` (`boolean`): `true` only on valid story ending nodes.
- `choices` (`array`): On any node with `terminal: false`, at least **1 choice must have an empty `"requires": {}`** so the player can never get soft-locked!

Verify all graph invariants with [`../scripts/validate_story_graph.py`](../scripts/validate_story_graph.py).
