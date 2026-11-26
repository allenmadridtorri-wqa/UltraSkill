# UltraSkill v1.0.0

**UltraSkill** is a portable, 288-file engineering and production skill package for AI coding agents. It encodes 10-year veteran practices across three pillars:

1. **3D & VFX (`skills/10`–`18`)**: Photorealistic modeling, PBR materials, motivated physical lighting, AgX color management, **Blender Cycles with OptiX on Google Colab GPUs**, cinematic 60-second trailers, VFX simulations, and Three.js interactive web story scenes.
2. **Game Development (`skills/20`–`27`)**: Core loop design, tabular GDDs, spatial level metrics, Godot 4 / custom engine architecture, character controllers, ticketed combat AI, server-authoritative networking, accessibility, frame-time optimization, and GitHub Actions cross-platform builds.
3. **Software Engineering (`skills/30`–`36`)**: System architecture, 9 core languages, full-stack web & SQL data migrations, deterministic unit testing, defensive security, CI/CD release automation, and severity-ranked code reviews.

---

## Hardware Constraint Model

UltraSkill is engineered for developers working on a **4 GB RAM laptop with 1 GB Intel UHD integrated graphics**:

- **Local Laptop**: Edits text/code, runs fast standard-library Python validators and unit tests, previews rendered stills/videos, and runs Three.js or Godot 4 (Compatibility mode) using the mandatory **LOW** hardware preset.
- **Google Colab GPU (T4 or better)**: Executes all Blender Cycles rendering using **OptiX**, verifies GPU engagement via `nvidia-smi`, benchmarks 3 representative frames before long jobs, and streams finished EXR/16-bit PNG frames directly to Google Drive with automatic resume.
- **GitHub Actions**: Compiles Windows `.exe`, Linux, and Web release packages in the cloud so the local laptop never runs heavy native toolchains.

---

## Quickstart

### 1. Validate the Package
Run the zero-dependency validator from the `UltraSkill/` directory:

```bash
python3 tools/validate.py
```

### 2. Install into a Project or Agent Environment
Use `install.py` to copy UltraSkill into your workspace and print loading instructions for **Antigravity IDE**, **Google AI Studio**, **Claude**, and **ChatGPT**:

```bash
python3 install.py --target /path/to/your/project --agent all
```

### 3. Initialize a Studio Project Loop
Scaffold a project tracking folder (`BRIEF.md`, `BARS.md`, `ROUNDS.md`, `DECISIONS.md`, `QUALITY.md`):

```bash
python3 skills/00-director/scripts/init_project.py --name "chronometer-still" --output ./studio_ledger
```

### 4. Pack a Distributable Archive
Create `UltraSkill-1.0.0.zip` after validation passes:

```bash
python3 tools/pack.py
```

---

## Portable Loading Across AI Tools

| Environment | Recommended Setup |
|---|---|
| **Antigravity IDE** | Install into `<project>/.agents/skills/UltraSkill/` (or `~/.gemini/config/skills/UltraSkill/`). The agent reads `SKILL.md` frontmatter automatically and loads sub-skills on demand. |
| **Google AI Studio** | Keep `UltraSkill/` in the workspace root (Build mode) or attach `UltraSkill/SKILL.md` plus only the active sub-skill folder (`skills/<id>/`) in System Instructions / prompt context. |
| **Claude (Claude Code / Projects)** | For Claude Code, place in `<project>/.claude/skills/UltraSkill/`. For Claude Web/Desktop Projects, upload `SKILL.md`, `skills/00-director/SKILL.md`, and the 1–2 relevant domain `SKILL.md` files. |
| **ChatGPT (Codex / Projects / Code Interpreter)** | For Codex/CLI agents supporting `.agents/skills/`, copy to `<project>/.agents/skills/UltraSkill/`. In ChatGPT Code Interpreter, upload `UltraSkill-1.0.0.zip` and instruct it to read `SKILL.md` first. |

---

## Repository Navigation

- [`SKILL.md`](SKILL.md) — Top-level skill router.
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — Three-machine model and 288-file structure.
- [`BRAIN.md`](BRAIN.md) — Veteran heuristics, diagnostics, and non-negotiable standards.
- [`MANIFEST.json`](MANIFEST.json) — Complete 288-file manifest.
- [`CREDITS.md`](CREDITS.md) — Open-source attributions and license disclosures.
- [`CHANGELOG.md`](CHANGELOG.md) — Version history.
