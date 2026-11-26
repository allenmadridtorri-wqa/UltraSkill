# Deterministic State Persistence, Save Slots & Checkpoint Rewind

## 1. Never Serialize Raw 3D Scene Graphs (`THREE.Scene.toJSON()`)

Dumping a live Three.js or Godot scene tree to JSON writes megabytes of geometry buffers and transient animation matrices into `localStorage` (which is capped at `5 MB` in browsers). Instead, serialize only the **minimal canonical story state snapshot (`< 1 KB`)** and derive the 3D scene appearance deterministically from that snapshot.

## 2. Canonical Save Snapshot Schema (`story_runtime.js`)

```json
{
  "schema_version": "1.0.0",
  "story_id": "chronometer_chamber",
  "current_node_id": "node_core_decision",
  "turn_index": 4,
  "variables": {
    "inspected_chronometer": true,
    "coolant_valves_opened": 1,
    "containment_integrity": 85,
    "alarm_active": false
  },
  "visited_nodes": [
    "node_intro",
    "node_inspect_desk",
    "node_valve_check",
    "node_core_decision"
  ],
  "timestamp_utc": "2026-11-26T04:00:00.000Z"
}
```

## 3. Immutable History Stack for Instant Branch Rewind

During both development verification and player exploration, users want to undo a choice (`Rewind 1 Step`) without replaying from the title screen:

1. Before applying a choice's variable mutations (`effects`) and transitioning to `target`, push a deep-cloned snapshot of `{ current_node_id, variables, visited_nodes }` onto a bounded `historyStack` (`max 50 entries`).
2. When `rewind()` is invoked:
   - Pop the last snapshot from `historyStack`.
   - Restore `current_node_id` and `variables`.
   - Trigger `onNodeEntered(currentNode, variables)` so the 3D scene immediately moves the camera back to `currentNode.camera_mark` and reconciles all 3D lights and prop states (e.g., turning the red alarm light back off if `alarm_active` reverted to `false`).

## 4. Reconciling 3D Scene State from Variables

Always implement a single idempotent `sync3DWorldToState(variables, currentNode)` function rather than imperative one-way triggers:
- **Bad (Imperative)**: `if (choice === 'pull_lever') redLight.intensity = 5.0;` (breaks on Save Load and Rewind!).
- **Good (Declarative State Sync)**: `redLight.intensity = variables.alarm_active ? 5.0 : 0.0; leverMesh.rotation.x = variables.coolant_valves_opened > 0 ? 0.65 : -0.45;`
