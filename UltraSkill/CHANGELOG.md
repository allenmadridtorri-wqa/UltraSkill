# Changelog

All notable changes to **UltraSkill** are documented in this file. This project adheres to Semantic Versioning (`MAJOR.MINOR.PATCH`).

## [1.0.0] - 2026-11-26

### Added
- **Root Package & Router (`8 files`)**:
  - `SKILL.md` top-level router enforcing progressive context loading and hardware constraints.
  - `ARCHITECTURE.md`, `BRAIN.md`, `README.md`, `CREDITS.md`, `CHANGELOG.md`, `MANIFEST.json` (exact 288-file inventory), and `install.py` multi-agent installer.
- **Studio Director (`skills/00-director`, `15 files`)**:
  - 5-round studio quality loop (`Brief -> Bars -> Plan -> Smallest Version -> Render/Run -> Inspect -> Score -> Fix Weakest Item -> Log`).
  - Templates (`BRIEF.md`, `BARS.md`, `ROUNDS.md`, `DECISIONS.md`, `QUALITY.md`) and automation scripts (`init_project.py`, `log_round.py`, `check_gates.py`).
- **3D, Cycles OptiX, Trailers, VFX & Realtime Web (`skills/10`–`18`, `95 files`)**:
  - `10-art-direction`: Photo reference methodology, physical lenses, composition values, 25 fake-3D tells, and the Uncanny Five rules.
  - `11-modeling`: Metric scale, bevel standards, hard-surface/organic topology, UVs, LODs, Geometry Nodes, and headless `mesh_linter.py`.
  - `12-materials-lighting`: PBR energy conservation, roughness imperfections, Random Walk SSS, physical light rigs, AgX color pipeline, and studio light generator.
  - `13-rigging-animation`: Joint conventions, weight painting, mocap foot-lock cleanup, physical camera mass rigs, and animation baker.
  - `14-blender-pipeline`: Headless Cycles **OptiX** GPU setup and `nvidia-smi` proof (`optix_verify.py`), `PREVIEW`/`REVIEW`/`FINAL` presets, 3-frame benchmark gate (>3h confirmation), Google Drive per-frame persistence and resume, and Tesla T4 15 GB VRAM auditing.
  - `15-film-trailer`: 60-second trailer beat sheet, animatic locking, editorial cutting, -14 LUFS audio normalization, and FFmpeg mastering scripts.
  - `16-vfx`: Particles, Mantaflow smoke/fire/fluids, Voronoi rigid-body fracture, volumetric holograms, multi-layer EXR AOVs, and OpenVDB budget estimator.
  - `17-realtime-web-scenes`: Three.js architecture, Cycles-to-glTF lightmap baking, resource disposal, and mandatory **LOW preset** for 4 GB RAM / 1 GB Intel UHD laptops.
  - `18-interactive-story`: Playable 3D camera choreography, DAG dialogue graphs, spatial triggers, and deterministic save state rewind.
- **Game Development (`skills/20`–`27`, `74 files`)**:
  - Complete coverage of core loops, Monte Carlo balance simulation, Godot 4 Compatibility architecture, coyote-time/jump-buffer controllers, ticketed behavior tree AI, server-authoritative networking, accessibility/audio buses, p99 frame-time profiling, and GitHub Actions cloud Windows builds.
- **Software Engineering (`skills/30`–`36`, `70 files`)**:
  - System architecture, 9 programming languages, HTTP/SQLite backend migrations, scientific root-cause debugging, secret scanning & path safety, GitHub Actions CI/CD, and BLKR/MAJR code review triage.
- **Examples, Tools & Evals (`26 files`)**:
  - 6 three-file reference projects (`examples/01`–`06`), 6 cross-pillar evaluations (`evals/`), `tools/validate.py`, and `tools/pack.py`.
