---
name: 18-interactive-story
description: >-
  Playable 3D interactive narrative skill combining Three.js or Godot cameras,
  branching dialogue DAG graphs, spatial hotspots, hybrid Cycles-prerendered
  backdrops, and deterministic versioned save states with rewind.
---

# 18-Interactive-Story: Playable 3D Scenes, Branching Graphs & Save State

An interactive story scene lets the player explore a 3D environment, inspect physical clues, trigger camera-choreographed conversations, and make choices with lasting state consequences—while running at `>= 30 FPS` on a 4 GB RAM / 1 GB Intel UHD laptop.

## When to use

Load this skill whenever building playable 3D story chapters, narrative exploration games, interactive product/museum walkthroughs, branching dialogue trees, spatial hotspots, or checkpoint rewind systems.

## Inputs

- Realtime 3D scene setup and `LOW` preset configuration from `17-realtime-web-scenes`.
- Optional Cycles OptiX prerendered backdrop stills or lightmaps from `14-blender-pipeline`.
- Narrative outline or passage draft.

## Steps

1. **Author & Validate the Branching Story Graph (`story_graph.json`)**:
   - Structure all narrative nodes, state flags (`boolean`, `integer`, `string`), precondition guards (`requires`), and choice mutations (`effects`) using [`templates/story_graph.json`](templates/story_graph.json) and [`references/story-graph-architecture.md`](references/story-graph-architecture.md).
   - If converting from Markdown/Twine passages, run `python3 skills/18-interactive-story/scripts/export_twine_to_json.py`.
   - Always run `python3 skills/18-interactive-story/scripts/validate_story_graph.py --input story_graph.json` to prove zero dead-end nodes, zero broken target IDs, and zero undeclared state variables.
2. **Wire Spatial 3D Triggers & Accessible Hotspots**:
   - Follow [`references/spatial-triggers-and-hotspots.md`](references/spatial-triggers-and-hotspots.md): pair every 3D clickable prop or proximity trigger with an accessible HTML `<button>` / keyboard shortcut (`1..9`, `Tab`, `Enter`) so users and automated verification browsers can play the entire story without pixel-hunting on a canvas.
3. **Choreograph Seamless Camera Transitions**:
   - Follow [`references/camera-choreography.md`](references/camera-choreography.md): smoothly damp-interpolate (`cubic-bezier` or exponential decay $\alpha = 1 - e^{-\lambda \Delta t}$) the 3D camera between free exploration, macro prop inspection, and over-the-shoulder dialogue marks.
4. **Use Hybrid Cycles Backdrops When Maximum Photorealism Is Required on 4 GB Laptops**:
   - Follow [`references/hybrid-prerendered-backdrops.md`](references/hybrid-prerendered-backdrops.md) and [`references/pacing-and-environmental-storytelling.md`](references/pacing-and-environmental-storytelling.md) to combine camera-projected Cycles OptiX renders with lightweight realtime 3D hotspots and dynamic props.
5. **Persist Deterministic Save States & Support Branch Rewind**:
   - Load [`templates/story_runtime.js`](templates/story_runtime.js) and follow [`references/state-persistence-and-rewind.md`](references/state-persistence-and-rewind.md) so every choice appends an immutable checkpoint snapshot that can be saved, exported, or rewound during testing.

## Numbers and defaults

All values below are **starting values**:

| Parameter | Starting Value | Verification Method |
|---|---|---|
| **Max Words per Dialogue Node** | `<= 45 words` (`2–3` short sentences; never a scrolling essay wall) | `validate_story_graph.py` |
| **Choices per Decision Node** | `2 – 4` distinct choices (`>= 1` fallback choice always available) | `validate_story_graph.py` |
| **Camera Transition Duration** | `0.8 s – 1.6 s` (`damping lambda = 4.5 – 6.5 s^-1`) | Inspect camera lerp in `scene_story.js` |
| **Hotspot Proximity Activation Radius** | `1.5 m – 2.8 m` (`dot(camForward, toTarget) >= 0.55`) | Inspect spatial trigger threshold |
| **Save History Ring Buffer** | `50` checkpoint snapshots (`< 64 KB` JSON in `localStorage`) | `story_runtime.js` state ledger |

## Failure modes and fixes

- **Soft-lock dead end where all choices on a node have false preconditions**: Always include at least one unconditional fallback choice (`"requires": {}`) on every non-terminal node, and enforce this automatically with `validate_story_graph.py`.
- **Wall-of-text exposition fatigue**: Replace 300-word lore dumps with a 3D inspectable prop change (a cracked gauge, a bloodstain, a flickering terminal light) plus a 25-word observation; see [`references/pacing-and-environmental-storytelling.md`](references/pacing-and-environmental-storytelling.md).
- **Camera clips through a table during transition from hallway to desk close-up**: Do not lerp linearly through solid obstacles; interpolate along a 2-segment quadratic Bezier arc elevated `+0.3 m` above obstacle height.

## Done check

- `validate_story_graph.py` exits with code `0` (`0` unreachable nodes, `0` broken targets, `0` soft-lock nodes).
- Every 3D hotspot and dialogue option is operable via both mouse/touch and keyboard (`Tab`/`Enter`/`1..4`).
- Save, load, and 1-step rewind restore both narrative variables and 3D camera/prop states deterministically.

## Related files

- [`references/story-graph-architecture.md`](references/story-graph-architecture.md)
- [`references/spatial-triggers-and-hotspots.md`](references/spatial-triggers-and-hotspots.md)
- [`references/camera-choreography.md`](references/camera-choreography.md)
- [`references/state-persistence-and-rewind.md`](references/state-persistence-and-rewind.md)
- [`references/pacing-and-environmental-storytelling.md`](references/pacing-and-environmental-storytelling.md)
- [`references/hybrid-prerendered-backdrops.md`](references/hybrid-prerendered-backdrops.md)
- [`templates/story_graph.json`](templates/story_graph.json)
- [`templates/story_runtime.js`](templates/story_runtime.js)
- [`scripts/validate_story_graph.py`](scripts/validate_story_graph.py)
- [`scripts/export_twine_to_json.py`](scripts/export_twine_to_json.py)
