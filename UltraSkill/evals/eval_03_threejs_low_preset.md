# Eval 03 — Three.js Interactive Story Scene for 1 GB Intel UHD (`LOW` Preset)

## 1. Benchmark Prompt

> "Build a Three.js interactive 3D story scene with camera choreography, branching choices, and state rewind that runs at a smooth 60 FPS on my 4 GB RAM laptop with 1 GB Intel UHD integrated graphics."

---

## 2. Skills Routed

1. [`skills/17-realtime-web-scenes/SKILL.md`](../skills/17-realtime-web-scenes/SKILL.md) (`LOW` preset default, DPR `1.0`, `<= 150` draw calls, `<= 512 MB` VRAM, zero per-frame allocations)
2. [`skills/18-interactive-story/SKILL.md`](../skills/18-interactive-story/SKILL.md) (Acyclic/valid story graph, exponential-decay camera transitions, rewind history stack)

---

## 3. Pass / Fail Grading Rubric (100 Points Total — Pass Threshold `>= 90`)

| Check ID | Criterion | Points | Verification Command / Method |
|---|---|---|---|
| `E03-1` | **Defaults to `LOW` Preset (`DPR 1.0`, `720p`)**: Scene initializes on `LOW` preset with `maxDpr = 1.0`, draw calls `<= 150`, triangles `<= 150,000`, and VRAM `<= 512 MB` | `25` | `python3 skills/17-realtime-web-scenes/scripts/gltf_budget_check.py --help` |
| `E03-2` | **Zero Hot-Path Heap Allocations**: `requestAnimationFrame` loop reuses pre-allocated module-scoped scratch vectors rather than allocating `new THREE.Vector3()` per frame | `25` | Inspect `examples/04-threejs-story-scene/scene_story.js` |
| `E03-3` | **Validated Story Graph (Zero Dead-Ends)**: Every choice target exists, every node is reachable from `entry`, and condition flags are producible | `25` | `python3 skills/18-interactive-story/scripts/validate_story_graph.py --help` |
| `E03-4` | **Frame-Rate Independent Camera & Rewind**: Camera uses exponential decay `Math.exp(-decay * dt)` and supports deterministic step-by-step state rewind | `25` | Inspect `StorySceneController` in `scene_story.js` |
