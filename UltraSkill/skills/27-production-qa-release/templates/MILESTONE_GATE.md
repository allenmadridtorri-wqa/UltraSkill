# Milestone Gate Sign-Off (`MILESTONE_GATE.md`)

- **Project**: `<Game Title>`
- **Target Gate**: `[ ] Prototype | [ ] Vertical Slice | [ ] Alpha | [ ] Beta | [ ] Release Candidate | [ ] Gold Master`
- **Version / Git Tag**: `<v0.4.0-alpha>`
- **Date**: `<YYYY-MM-DD>`

---

## 1. Core Gameplay & Loop Verification

- [ ] **30-Second Core Loop**: Player movement (`coyote time 100ms`, `jump buffer 120ms`), camera collision recovery, and primary action verb feel responsive with zero input drops.
- [ ] **Start-to-Finish Flow**: Player can boot from `Title Screen -> Gameplay -> Pause/Settings -> Victory/GameOver -> Return to Title` without console errors.
- [ ] **Save & Load Integrity**: Atomic save (`.tmp -> .bak -> .json`) with SHA-256 verification passes round-trip reload and schema migration tests.

---

## 2. Performance & Low-Spec Hardware Compliance (4 GB RAM / 1 GB Intel UHD)

- [ ] **`LOW` Preset Frame Time**: `p95 <= 16.67 ms` (`60 FPS`), `p99 <= 22.0 ms` verified by `analyze_frame_times.py`.
- [ ] **Draw Call & Polygon Budget**: Peak draw calls `<= 150`, visible triangles `<= 150,000` on `LOW` preset.
- [ ] **Memory Ceiling**: Peak GPU VRAM `<= 512 MB`, system RAM `<= 1,800 MB`.
- [ ] **Zero Leak Soak**: 20 consecutive level reloads produce `0` orphan nodes and `< 2%` memory drift.

---

## 3. Quality, Audio & Accessibility

- [ ] **Full Gamepad & Keyboard Navigation**: Every menu screen and modal maintains valid focus (`gui_get_focus_owner() != null`).
- [ ] **Audio Bus Hierarchy**: `Master` limiter at `-1.0 dBTP`, `Voice` sidechain ducks `Music`/`SFX`, repeating SFX randomized.
- [ ] **Accessibility & Localization**: Subtitles (`>= 24px` @ 1080p with dark plate), camera shake slider (`0–100%`), and localization table check (`check_loc_strings.py`) pass.

---

## 4. Defect & Packaging Gate

| Severity | Open Count | Allowed Max for Current Gate | Status |
|---|---|---|---|
| **`S0` (Crash / Soft-Lock / Data Loss)** | `0` | `0` (All Gates) | PASS |
| **`S1` (Major Broken Feature / `< 45 FPS`)** | `0` | `0` (VS, RC, Gold) / `<= 3` (Alpha) | PASS |
| **`S2` (Moderate / Workaround Exists)** | `2` | `<= 5` (RC) / Documented (Gold) | PASS |
| **`S3` (Minor Polish / Typo)** | `4` | Tracked in backlog | PASS |

- [ ] **Cloud Release Pipeline**: GitHub Actions workflow builds Windows `.exe` + `.pck` and Web `.zip` cleanly and passes `package_release_check.py`.
