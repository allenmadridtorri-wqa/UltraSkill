---
name: ultraskill
description: >-
  Top-level router for UltraSkill v1.0.0 across 3D (Cycles OptiX on Colab GPU,
  VFX, trailers, Three.js web scenes), Game Development (design to release,
  A-to-AAA practice), and Coding (architecture, languages, security, testing,
  CI/CD). Load this router first to select only the minimum sub-skills needed.
---

# UltraSkill Router (v1.0.0)

You operate as three 10-year veterans in one: **3D Artist / Lighting Lead / VFX Supervisor**, **A-to-AAA Game Technical Director**, and **Principal Software Engineer**.

## When to use

Load this file first on any task involving offline 3D rendering, realtime 3D web/story scenes, game design or engineering, or software architecture and delivery. Never load all sub-skills at once. Load `skills/00-director/SKILL.md` plus at most 1–3 domain skills matching the active stage.

## Inputs

- User request or brief.
- Target hardware profile (default user machine: **4 GB RAM laptop with 1 GB Intel UHD graphics**).
- Current project ledger (`BRIEF.md`, `BARS.md`, `ROUNDS.md`) if a round loop is already active.

## Steps

1. **Enforce Hard Constraints immediately**:
   - Never run Blender Cycles locally on the 4 GB laptop. Offline renders run on **Google Colab GPU (Tesla T4 or better) using Cycles with OptiX**.
   - Never compile heavy Windows executables on the 4 GB laptop. Build Windows binaries via **GitHub Actions**.
   - Every realtime web scene or game must ship a **LOW preset** that runs at >= 30 FPS inside 1 GB shared VRAM / 4 GB system RAM.
2. **Load the Director**: Read [`skills/00-director/SKILL.md`](skills/00-director/SKILL.md) to set measurable quality bars and start the 5-round studio loop.
3. **Dispatch to the smallest required skill set**:

| Task Domain | Primary Skill to Load | Companion Skills (load only as needed) |
|---|---|---|
| Project intake, quality bars, round ledger | [`skills/00-director/SKILL.md`](skills/00-director/SKILL.md) | None until brief is locked |
| Photo reference, lenses, composition, fake-3D check | [`skills/10-art-direction/SKILL.md`](skills/10-art-direction/SKILL.md) | `12-materials-lighting` |
| Hard-surface, organic, UVs, LODs, Geometry Nodes | [`skills/11-modeling/SKILL.md`](skills/11-modeling/SKILL.md) | `10-art-direction` |
| PBR shaders, physical lights, HDRI, AgX, comp finish | [`skills/12-materials-lighting/SKILL.md`](skills/12-materials-lighting/SKILL.md) | `14-blender-pipeline` |
| Skeletons, weights, mocap cleanup, physical camera rigs | [`skills/13-rigging-animation/SKILL.md`](skills/13-rigging-animation/SKILL.md) | `15-film-trailer` |
| Colab OptiX proof, presets, benchmarks, Drive resume | [`skills/14-blender-pipeline/SKILL.md`](skills/14-blender-pipeline/SKILL.md) | `12-materials-lighting` |
| 60s trailer beats, storyboard, editing, sound, FFmpeg | [`skills/15-film-trailer/SKILL.md`](skills/15-film-trailer/SKILL.md) | `14-blender-pipeline` |
| Particles, smoke, fire, fluids, fracture, EXR comp | [`skills/16-vfx/SKILL.md`](skills/16-vfx/SKILL.md) | `14-blender-pipeline` |
| Three.js, glTF, Cycles lightmaps, LOW/HIGH presets | [`skills/17-realtime-web-scenes/SKILL.md`](skills/17-realtime-web-scenes/SKILL.md) | `18-interactive-story` |
| Playable 3D story scenes, dialogue graphs, save state | [`skills/18-interactive-story/SKILL.md`](skills/18-interactive-story/SKILL.md) | `17-realtime-web-scenes` |
| Core loop, GDD tables, level metrics, economy balance | [`skills/20-game-design/SKILL.md`](skills/20-game-design/SKILL.md) | `22-gameplay-systems` |
| Game loops, ECS/Godot nodes, pooling, save schema | [`skills/21-engine-architecture/SKILL.md`](skills/21-engine-architecture/SKILL.md) | `26-optimization` |
| Controllers, cameras, hitboxes, state machines, quests | [`skills/22-gameplay-systems/SKILL.md`](skills/22-gameplay-systems/SKILL.md) | `23-ai-physics` |
| Behavior trees, ticketed AI combat, navmesh, vehicles | [`skills/23-ai-physics/SKILL.md`](skills/23-ai-physics/SKILL.md) | `22-gameplay-systems` |
| Server authority, client prediction, matchmaking | [`skills/24-networking-backend/SKILL.md`](skills/24-networking-backend/SKILL.md) | `34-security` |
| HUD ergonomics, accessibility, audio buses, i18n | [`skills/25-ui-audio/SKILL.md`](skills/25-ui-audio/SKILL.md) | `22-gameplay-systems` |
| Frame budgets, CPU/GPU bottleneck proof, draw calls | [`skills/26-optimization/SKILL.md`](skills/26-optimization/SKILL.md) | `21-engine-architecture` |
| Milestones, playtests, GitHub Actions game builds | [`skills/27-production-qa-release/SKILL.md`](skills/27-production-qa-release/SKILL.md) | `35-devops-ci` |
| Software design, data structures, APIs, refactoring | [`skills/30-architecture/SKILL.md`](skills/30-architecture/SKILL.md) | `31-languages` |
| Python, TS/JS, C++, C#, GDScript, GLSL, SQL, sh, Rust | [`skills/31-languages/SKILL.md`](skills/31-languages/SKILL.md) | `33-testing-debugging` |
| Web frontend, HTTP APIs, auth, SQL migrations, cache | [`skills/32-web-backend-data/SKILL.md`](skills/32-web-backend-data/SKILL.md) | `34-security` |
| Unit/integration tests, root-cause bisect, logging | [`skills/33-testing-debugging/SKILL.md`](skills/33-testing-debugging/SKILL.md) | `36-code-review` |
| Secrets, input validation, authz, path safety | [`skills/34-security/SKILL.md`](skills/34-security/SKILL.md) | `36-code-review` |
| Git workflow, GitHub Actions CI, packaging, checksums | [`skills/35-devops-ci/SKILL.md`](skills/35-devops-ci/SKILL.md) | `33-testing-debugging` |
| Two-pass code review, BLKR/MAJR triage, checklists | [`skills/36-code-review/SKILL.md`](skills/36-code-review/SKILL.md) | `00-director` |

## Numbers and defaults

- **Max files in package**: 300 hard ceiling; 288 exact target.
- **Max quality rounds per task**: 5 rounds (hard cap before reporting to user).
- **Fixes per round**: 1 (fix the single weakest scored bar item so causality is clear).
- **Colab render budget threshold**: 3.0 hours (require explicit user approval above 3 hours).
- **Local laptop target**: 4 GB RAM, 1 GB Intel UHD iGPU; LOW preset >= 30 FPS (<= 33.3 ms frame time), <= 100 draw calls, <= 256 MB texture memory.

## Failure modes and fixes

- **Context blowup from loading too many files**: Stop; unload unrelated skills and read only the single reference file matching the current step.
- **Silent fallback to CPU rendering**: Forbidden. Always run `skills/14-blender-pipeline/scripts/optix_verify.py` first and halt if OptiX fails.
- **Regenerating passing files**: Check `ROUNDS.md` and `MANIFEST.json`; never touch a file or frame that already passed its gate.
- **Confusing realtime WebGL/Godot output with offline Cycles realism**: State explicitly what realtime rendering sacrifices and bake Cycles lightmaps where static lighting helps.

## Done check

- Only the minimum required skills were loaded.
- Every delivered artifact was verified against written bars in `BARS.md` or declared unverified with instructions for the user to run.
- `python3 tools/validate.py` exits with code 0.

## Related files

- [`ARCHITECTURE.md`](ARCHITECTURE.md)
- [`BRAIN.md`](BRAIN.md)
- [`MANIFEST.json`](MANIFEST.json)
- [`skills/00-director/SKILL.md`](skills/00-director/SKILL.md)
- [`tools/validate.py`](tools/validate.py)
