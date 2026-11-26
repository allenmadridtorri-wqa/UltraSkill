# UltraSkill v1.0.0 Architecture

## 1. Three-Machine Execution Model

UltraSkill enforces a strict separation between authoring, offline GPU rendering, and native binary compilation so a developer on a budget laptop can ship photoreal 3D renders, playable games, and production software.

| Environment | Hardware Baseline | Assigned Workloads | Forbidden Workloads |
|---|---|---|---|
| **Local Laptop** | 4 GB RAM, 1 GB Intel UHD Graphics | Editing code/Markdown, running lightweight Python unit tests and validators, viewing rendered stills/MP4s, running Three.js or Godot 4 (Compatibility renderer) on the **LOW** preset. | Blender Cycles rendering, Mantaflow fluid/smoke baking, C++/Rust/Windows `.exe` cross-compilation, 4K texture authoring. |
| **Google Colab GPU** | NVIDIA Tesla T4 (15 GB VRAM) or better, Linux headless | Headless Blender Cycles rendering with **OptiX**, OpenVDB/Alembic simulation baking, Cycles lightmap baking for glTF export, FFmpeg ProRes/H.264 sequence assembly. | Interactive GUI editing without Drive sync, un-benchmarked multi-hour renders, silent CPU fallback. |
| **GitHub Actions CI** | Cloud x86_64 Windows, Linux, and macOS runners | Automated test suites, Windows `.exe` compilation (Godot exports, PyInstaller, C++, Rust), release archiving, and SHA-256 checksum generation. | Storing unencrypted secrets in workflow files or repository history. |

## 2. Package Topology (288 Files)

```text
UltraSkill/
├── SKILL.md                      # Root router (<200 lines)
├── ARCHITECTURE.md               # Hardware separation & package layout
├── BRAIN.md                      # Cross-pillar veteran decision rules
├── README.md                     # Quickstart & agent compatibility
├── CREDITS.md                    # FOSS licenses & structural attribution
├── CHANGELOG.md                  # Release history
├── MANIFEST.json                 # Exact 288-file inventory & batch ledger
├── install.py                    # Multi-agent workspace installer
├── skills/
│   ├── 00-director/              # Studio loop, quality gates, usage budget (15)
│   ├── 10-art-direction/         # Photo references, lenses, fake-3D tells (8)
│   ├── 11-modeling/              # Metric scale, bevels, topology, UVs, LODs (10)
│   ├── 12-materials-lighting/    # PBR energy, imperfections, physical rigs, AgX (12)
│   ├── 13-rigging-animation/     # Skeletons, weights, mocap cleanup, camera mass (10)
│   ├── 14-blender-pipeline/      # Cycles OptiX proof, presets, Colab resume, VRAM (16)
│   ├── 15-film-trailer/          # Beats, storyboard, cutting, -14 LUFS, FFmpeg (12)
│   ├── 16-vfx/                   # Particles, smoke/fire, fluids, fracture, EXR comp (12)
│   ├── 17-realtime-web-scenes/   # Three.js, glTF, baked lightmaps, LOW preset (14)
│   ├── 18-interactive-story/     # Branching graphs, 3D triggers, save state (11)
│   ├── 20-game-design/           # Core loop, tabular GDD, metrics, Monte Carlo (11)
│   ├── 21-engine-architecture/   # Fixed timestep, Godot/ECS, pooling, saves (9)
│   ├── 22-gameplay-systems/      # Controllers, cameras, hitstop, FSM, quests (13)
│   ├── 23-ai-physics/            # Behavior trees, attack tokens, navmesh (7)
│   ├── 24-networking-backend/    # Server authority, prediction, anti-cheat (7)
│   ├── 25-ui-audio/              # HUD safe zones, accessibility, audio buses, i18n (7)
│   ├── 26-optimization/          # Frame budgets, CPU/GPU bottleneck proof (9)
│   ├── 27-production-qa-release/ # Milestones, playtests, GitHub Actions builds (11)
│   ├── 30-architecture/          # System boundaries, data structures, APIs (9)
│   ├── 31-languages/             # Python, TS/JS, C++, C#, GDScript, GLSL, SQL, sh, Rust (10)
│   ├── 32-web-backend-data/      # Frontend, HTTP, auth, SQL migrations, caching (9)
│   ├── 33-testing-debugging/     # Test pyramid, deterministic bisect, logging (9)
│   ├── 34-security/              # Secrets, validation, authz, path traversal (7)
│   ├── 35-devops-ci/             # Git hygiene, GitHub Actions, packaging (10)
│   └── 36-code-review/           # Two-pass review, BLKR/MAJR severity, scans (6)
├── examples/                     # 6 end-to-end projects x 3 files each (18)
├── tools/                        # validate.py and pack.py (2)
└── evals/                        # 6 cross-pillar benchmark tasks (6)
```

## 3. Progressive Context Loading

AI coding agents degrade when flooded with irrelevant instructions. UltraSkill enforces three-tier progressive disclosure:

1. **Tier 1 — Router (`SKILL.md`)**: Loaded at session start (~150 lines). Maps the user's goal to 1–3 numbered skill directories.
2. **Tier 2 — Skill Contract (`skills/<id>/SKILL.md` + `skills/00-director/SKILL.md`)**: Each under 200 lines. Defines inputs, numbered steps, numeric defaults, failure modes, and links to specific reference files.
3. **Tier 3 — Deep Reference / Script / Template**: Loaded one file at a time only when executing the specific step that requires it, then unloaded or summarized in `ROUNDS.md`.

## 4. Verification Architecture

- **Static Package Integrity (`tools/validate.py`)**: Confirms file count (`<= 300`, exact match with `MANIFEST.json`), YAML frontmatter on every `SKILL.md`, line limit (`< 200` lines per `SKILL.md`), relative link resolution, absence of placeholder strings, Python AST parse validity, and JSON syntax.
- **Runtime Proof Scripts**:
  - `skills/14-blender-pipeline/scripts/optix_verify.py` proves actual NVIDIA OptiX execution and checks `nvidia-smi` before rendering.
  - `skills/00-director/scripts/check_gates.py` blocks delivery until all bars in `BARS.md` and `QUALITY.md` pass.
