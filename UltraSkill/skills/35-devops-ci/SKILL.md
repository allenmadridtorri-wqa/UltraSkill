---
name: ultraskill-devops-ci
description: Trunk-based Git hygiene, automated GitHub Actions CI/CD pipelines, cloud build offloading for 4 GB RAM laptops, deterministic packaging and SHA-256 checksum manifests, reproducible containers, and zero-downtime releases with fast rollback.
---

# 35 — DevOps, CI/CD & Cloud Offload

This skill automates source control, continuous integration, deterministic packaging, and cloud compilation—specifically designed so a developer on a **4 GB RAM laptop with 1 GB Intel UHD integrated graphics** runs lightweight local validation (`< 2 seconds`) while offloading heavy Windows C++/Godot compilation, container builds, and full test matrices to **GitHub Actions cloud runners**.

## When to use

- Setting up Git branching, commit conventions, `.gitignore`, or `.gitattributes` (Git LFS for 3D/game binaries).
- Authoring GitHub Actions workflows for Python, TypeScript/Web, or cross-platform release builds.
- Offloading heavy compilation, packaging, or headless browser/engine tests from a low-spec laptop to the cloud.
- Generating deterministic `.zip` / `.tar.gz` release packages with a verified `SHA256SUMS.txt` manifest.
- Writing multi-stage, non-root `Dockerfile` configurations for reproducible environments.
- Executing safe production releases with automated smoke checks and `< 60-second` rollbacks.

## Inputs

- Repository structure, test commands, and target build artifacts.
- Local hardware constraints (`4 GB RAM` laptop) and target cloud runner (`ubuntu-24.04` / `windows-2022`).

## Steps

1. **Configure Git Workflow & Binary Hygiene**:
   - Enforce short-lived feature branches (`< 2 days`), atomic conventional commits, and `.gitattributes` LFS tracking for large binary assets (`.blend`, `.exr`, `.glb`, `.ogg`) using [references/git-workflow-and-hygiene.md](references/git-workflow-and-hygiene.md).
2. **Build Fast, Deterministic GitHub Actions Pipelines**:
   - Configure lockfile-cached CI pipelines with explicit timeouts (`timeout-minutes: 10`), minimal permissions (`contents: read`), and concurrency cancellation using [references/github-actions-pipelines.md](references/github-actions-pipelines.md), [templates/github_ci_python.yml](templates/github_ci_python.yml), and [templates/github_ci_web.yml](templates/github_ci_web.yml).
3. **Offload Heavy Builds from the 4 GB RAM Laptop**:
   - Keep local workflows restricted to lightweight editors, Python stdlib linters, and `LOW` preset previews while delegating Windows `.exe` builds, Docker builds, and multi-OS matrices to GitHub Actions using [references/cloud-builds-for-low-spec-laptops.md](references/cloud-builds-for-low-spec-laptops.md).
4. **Package Artifacts & Generate SHA-256 Manifests**:
   - Strip reproducible timestamps where needed, follow Semantic Versioning (`MAJOR.MINOR.PATCH`), and generate cryptographic checksum manifests using [references/packaging-and-distribution.md](references/packaging-and-distribution.md) and [scripts/checksum_manifest.py](scripts/checksum_manifest.py).
5. **Harden Containers & Release Rollbacks**:
   - Use pinned multi-stage Docker images running as non-root `UID 10001` ([references/containers-and-reproducibility.md](references/containers-and-reproducibility.md)) and verify every release with automated post-deploy smoke checks and instant rollback procedures ([references/release-and-rollback.md](references/release-and-rollback.md)).

## Numbers and defaults

| Parameter | Default Target | Hard Limit / Rule |
|---|---|---|
| Local Pre-Push Validation Time | `<= 3.0 seconds` | Runs pure Python AST, unit tests, and secret scanner (`< 80 MB` RAM) |
| CI Pipeline Total Duration | `<= 5 minutes` | Hard `timeout-minutes: 10–15` on every job to prevent hung runners |
| Pull Request Size | `150–400` lines changed | `<= 600` lines (excluding generated lockfiles) for effective review |
| Container Runtime User | Non-root `UID 10001` | Never run production application processes as `root` (`UID 0`) |
| Rollback Recovery Time (`MTTR`) | `<= 60 seconds` | Immutable previous version artifact ready for immediate re-point |

## Failure modes and fixes

- **Symptom**: Pushing 5 rapid commits to a PR queues up 15 redundant CI jobs and exhausts GitHub Actions minutes.
  - **Fix**: Add a top-level `concurrency:` block with `cancel-in-progress: true` keyed on `${{ github.workflow }}-${{ github.ref }}`.
- **Symptom**: Committing five 80 MB `.blend` and `.exr` files directly to standard Git bloats `.git/` to 2 GB and fails GitHub's `100 MB` file limit.
  - **Fix**: Track binary authoring extensions via Git LFS in `.gitattributes` (`*.blend filter=lfs diff=lfs merge=lfs -text`) or store heavy raw renders on mounted Google Drive (`UltraSkill_Colab_Renders/`).
- **Symptom**: Running `docker build` or a full Webpack/Vite + TypeScript production build locally freezes the user's 4 GB RAM laptop.
  - **Fix**: Never require local Docker Desktop on a 4 GB RAM laptop. Run `python3 tools/validate.py` and `unittest` locally, and trigger heavy builds via `git push` or `gh workflow run` on GitHub Actions.

## Done check

- [ ] CI workflow files specify `timeout-minutes`, `permissions: contents: read`, dependency caching, and `concurrency` cancellation.
- [ ] All release artifacts have a verified `SHA256SUMS.txt` manifest generated by `checksum_manifest.py`.
- [ ] `python3 skills/35-devops-ci/scripts/checksum_manifest.py --self-test` exits with code `0`.

## Related files

- [references/git-workflow-and-hygiene.md](references/git-workflow-and-hygiene.md)
- [references/github-actions-pipelines.md](references/github-actions-pipelines.md)
- [references/cloud-builds-for-low-spec-laptops.md](references/cloud-builds-for-low-spec-laptops.md)
- [references/packaging-and-distribution.md](references/packaging-and-distribution.md)
- [references/containers-and-reproducibility.md](references/containers-and-reproducibility.md)
- [references/release-and-rollback.md](references/release-and-rollback.md)
- [templates/github_ci_python.yml](templates/github_ci_python.yml)
- [templates/github_ci_web.yml](templates/github_ci_web.yml)
- [scripts/checksum_manifest.py](scripts/checksum_manifest.py)
