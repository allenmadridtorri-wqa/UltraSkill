# QA and Bug Triage

A bug report that says *"Combat broke in level 2"* is unfixable noise. A veterinary-grade QA workflow enforces **deterministic reproduction payloads** and strict **`S0–S3` severity triage**.

---

## 1. Severity Classification Matrix (`S0 – S3`)

| Severity | Definition | Examples | Release Policy |
|---|---|---|---|
| **`S0` — Blocker / Crash** | Crash to desktop, progress soft-lock, save corruption, data loss, or security vulnerability | Game crashes on boss death; arena door stays locked after wave cleared; save file truncated | **Zero tolerance**: blocks Alpha, Beta, RC, and Gold gates immediately |
| **`S1` — Major Functional** | Core mechanic broken, frame rate drops `< 45 FPS` on target preset, or severe visual/audio failure with no obvious workaround | Dodge i-frames don't activate after reloading a save; French localization missing on main menu | **Blocks RC and Gold**: must be fixed before shipping |
| **`S2` — Moderate / Minor** | Noticeable defect in non-critical path or cosmetic/UI glitch with an easy workaround | Enemy ragdoll clips partway into a crate; quest journal scroll bar resets position on tab switch | Fix in Beta if low-risk, or schedule for Day-7 patch |
| **`S3` — Trivial / Polish** | Minor typo, 2px alignment offset, rare texture seam in an out-of-bounds corner | Typo in lore codex entry #14 | Triage at producer discretion |

---

## 2. Deterministic Reproduction Capture (`F12` Bug Snapshot)

In development and QA builds, bind a single hotkey (`F12`) that writes a self-contained diagnostic bundle (`user://bug_snapshots/bug_YYYYMMDD_HHMMSS.json`):
1. Exact **Git Commit SHA** and **Game Version**.
2. Active **RNG Seed** (`seed`) and **Zone / Level ID**.
3. Player transform (`position`, `rotation`, `velocity`) and current **State Machine history** (last 8 transitions).
4. Active entities list (counts, positions, current BT/FSM states).
5. Current **Save Payload snapshot** (`payload` JSON) so an engineer can load directly into the exact room state in 2 seconds.
6. Last `50` lines of structured log output and current `p95` frame-time / VRAM telemetry.

---

## 3. Regression Soak Testing

Before tagging any Release Candidate:
- Run an automated **30-minute headless or bot soak test** that cycles `Title -> Load Level -> Spawn Wave -> Defeat Wave -> Save -> Reload -> Unload` 50 times in a row.
- Assert `orphan_node_count == 0` and total process RAM drift `< 5%` between Cycle #5 and Cycle #50.
