---
name: ultraskill-production-qa-release
description: Milestone gating (Prototype to Gold), silent playtesting protocol, severity-ranked bug triage, GitHub Actions cloud Windows builds for low-spec laptops, crash telemetry, and store release packaging.
---

# 27 — Production, QA & Cloud Release

This skill takes a game from playable greybox to shipped Gold Master: enforcing hard milestone gates, structured playtesting, deterministic bug triage, **GitHub Actions cloud Windows `.exe` builds** (so a 4 GB RAM laptop never compiles heavy C++/export templates locally), crash reporting, and store-ready release zips.

## When to use

- Planning or evaluating game production milestones (Prototype, Vertical Slice, Alpha, Beta, Release Candidate, Gold).
- Running a playtest session and logging actionable friction telemetry.
- Writing or triaging bug reports by severity (`S0 Blocker` through `S3 Polish`).
- Exporting Windows (`.exe` + `.pck`), Linux, or Web builds in the cloud via GitHub Actions.
- Setting up crash handlers, structured log rotation, and semantic hotfix patching.
- Running final pre-release packaging checks (icons, licenses, debug flag stripping, SHA-256 checksums) before publishing to Steam or Itch.io.

## Inputs

- Game project repository (`project.godot`, `export_presets.cfg`, or web/custom engine manifest).
- Milestone deliverables and target quality bars.

## Steps

1. **Gate Milestones Explicitly**:
   - Evaluate progress against the 6 production gates (Prototype -> Vertical Slice -> Alpha -> Beta -> RC -> Gold) and cut P2/P3 scope early using [references/milestones-and-scoping.md](references/milestones-and-scoping.md) and [templates/MILESTONE_GATE.md](templates/MILESTONE_GATE.md).
2. **Conduct Structured Playtests**:
   - Run silent observation playtests + automated funnel telemetry (`time_to_complete`, `death_heatmaps`, `stuck_events`) using [references/playtesting-protocol.md](references/playtesting-protocol.md).
3. **Triage & Verify Bugs**:
   - Record deterministic reproduction steps, seed/save attachments, and severity classifications (`S0–S3`) using [references/qa-and-bug-triage.md](references/qa-and-bug-triage.md) and [templates/BUG_REPORT.md](templates/BUG_REPORT.md).
4. **Build Windows Executables in the Cloud**:
   - Never run heavy cross-compilation or multi-gigabyte export templates locally on the 4 GB RAM laptop. Push a git tag (`v1.0.0`) to trigger headless Godot/Web builds on GitHub Actions using [references/cloud-windows-builds.md](references/cloud-windows-builds.md) and [templates/github_godot_release.yml](templates/github_godot_release.yml).
5. **Configure Crash Logs & Hotfix Patching**:
   - Enable rotating local crash logs (`user://logs/`), capture unhandled exceptions with seed + last 8 state machine transitions, and version `.pck` patch deltas using [references/crash-reporting-and-patching.md](references/crash-reporting-and-patching.md).
6. **Audit Final Release Artifact**:
   - Verify no debug console keys, orphaned assets, or missing third-party licenses remain in the release zip using [references/store-release-readiness.md](references/store-release-readiness.md) and [scripts/package_release_check.py](scripts/package_release_check.py).

## Numbers and defaults

| Parameter | Default Value | Tolerance / Notes |
|---|---|---|
| Milestone Buffer Reserve | `20%` of schedule | Reserved for unscheduled iteration and bug fixing |
| Playtest Soft-Lock Threshold | `0` soft-locks; `< 15%` players stuck `> 90 s` | Any area stalling `>= 25%` of testers requires level redesign |
| Bug Release Gate (RC -> Gold) | `0` open `S0` (Crash/Soft-Lock), `0` open `S1` (Major Broken Feature) | All `S2` workarounds documented |
| Cloud Build Timeout (GitHub Actions) | `15 minutes` max | Typical Godot 4 Windows + Web export completes in `2–4 min` |
| Crash Log Retention | `5` rotating log files, `<= 2 MB` each | Stored in OS user data directory (`user://logs/`) |
| Release Zip Integrity | SHA-256 checksum manifest + clean startup smoke check | Verified by `package_release_check.py` |

## Failure modes and fixes

- **Symptom**: Game reaches "Alpha" with 10 half-built levels and unpolished core movement.
  - **Fix**: Never enter Content Production (Alpha) before passing the **Vertical Slice Gate** (`1` complete 3-minute slice with final-bar controls, art, audio, and 60 FPS frame budget).
- **Symptom**: A Windows build exported on a developer laptop crashes on clean player PCs or fails because local RAM ran out during asset packing.
  - **Fix**: Offload all release exports to clean Ubuntu runners on GitHub Actions using [templates/github_godot_release.yml](templates/github_godot_release.yml), which pins exact engine and export template versions.
- **Symptom**: Shipped release build leaves a debug cheat key (`F9 = God Mode / Skip Level`) active for public players.
  - **Fix**: Guard all debug cheats behind `OS.is_debug_build()` and scan the release configuration with [scripts/package_release_check.py](scripts/package_release_check.py).

## Done check

- [ ] Milestone gate checklist (`MILESTONE_GATE.md`) is completed with zero open `S0/S1` defects.
- [ ] `.github/workflows/release.yml` builds Windows `.exe` + `.pck` and Web `.zip` artifacts automatically in the cloud.
- [ ] `python3 skills/27-production-qa-release/scripts/package_release_check.py --self-test` exits with code `0`.

## Related files

- [references/milestones-and-scoping.md](references/milestones-and-scoping.md)
- [references/playtesting-protocol.md](references/playtesting-protocol.md)
- [references/qa-and-bug-triage.md](references/qa-and-bug-triage.md)
- [references/cloud-windows-builds.md](references/cloud-windows-builds.md)
- [references/crash-reporting-and-patching.md](references/crash-reporting-and-patching.md)
- [references/store-release-readiness.md](references/store-release-readiness.md)
- [templates/MILESTONE_GATE.md](templates/MILESTONE_GATE.md)
- [templates/BUG_REPORT.md](templates/BUG_REPORT.md)
- [templates/github_godot_release.yml](templates/github_godot_release.yml)
- [scripts/package_release_check.py](scripts/package_release_check.py)
