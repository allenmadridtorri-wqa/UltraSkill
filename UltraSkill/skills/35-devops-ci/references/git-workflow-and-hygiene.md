# Git Workflow and Repository Hygiene

A clean Git history is a searchable engineering lab notebook: every commit compiles, passes tests, and explains *why* a change was made.

---

## 1. Trunk-Based Development & Atomic Commits

1. **Short-Lived Branches (`main` + `< 2 day` feature branches)**:
   - Branch off `main` (`feat/optix-resume-guard`, `fix/dodge-exit-iframes`), keep changes focused on a single concern (`<= 400 lines`), and merge back via fast CI-verified Pull Requests.
2. **Conventional Commit Messages**:
   - Format: `<type>(<scope>): <imperative summary under 72 chars>`
   - Types: `feat`, `fix`, `perf`, `refactor`, `test`, `docs`, `ci`, `chore`.
   - Examples:
     - `fix(blender-pipeline): delete truncated exr files before colab frame resume`
     - `perf(optimization): batch modular arena pillars into MultiMeshInstance3D`

---

## 2. Mandatory `.gitignore` & `.gitattributes` Rules

### Canonical Multi-Pillar `.gitignore`
```gitignore
# Secrets & Environment
.env
.env.*
!.env.example
*.pem
*.key

# 3D & Render Intermediates
*.blend1
*.blend2
renders/
sim_cache/

# Game Engine Caches
.godot/
build/
dist/

# Coding & OS Artifacts
__pycache__/
*.py[cod]
.venv/
node_modules/
.DS_Store
Thumbs.db
```

### Line Endings & Git LFS (`.gitattributes`)
Ensure shell scripts (`.sh`) and Python scripts (`.py`) always checkout with `LF` line endings even on Windows laptops (preventing `/usr/bin/env: 'python3\r': No such file or directory`):
```gitattributes
* text=auto eol=lf
*.sh text eol=lf
*.py text eol=lf
*.gd text eol=lf
*.bat text eol=crlf
*.blend filter=lfs diff=lfs merge=lfs -text
*.glb filter=lfs diff=lfs merge=lfs -text
```
