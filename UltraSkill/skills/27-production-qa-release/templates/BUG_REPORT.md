# Deterministic Bug Report (`BUG_REPORT.md`)

- **Bug ID**: `BUG-2026-042`
- **Title**: `<Concise [Subsystem] Symptom Summary — e.g., [Combat] Player remains stuck in DodgeRoll i-frames if staggered on exit frame>`
- **Severity**: `[ ] S0 Blocker/Crash | [x] S1 Major | [ ] S2 Moderate | [ ] S3 Minor Polish`
- **Build Version / Commit**: `v0.9.2-rc1 (commit 8f3a1c2)`
- **Platform & Preset**: `Windows 10 / 4 GB RAM / Intel UHD 620 — LOW Preset (1280x720)`
- **Reproducibility**: `[x] 100% Deterministic | [ ] Frequent (>50%) | [ ] Intermittent (<25%)`

---

## 1. Environment & Diagnostic State (`F12` Snapshot)

```json
{
  "zone_id": "arena_courtyard_02",
  "rng_seed": 948102,
  "player_pos": [18.42, 0.0, -31.15],
  "state_history_last_4": [
    {"from": "Move", "to": "AttackCombo1", "tick": 4102},
    {"from": "AttackCombo1", "to": "DodgeRoll", "tick": 4118},
    {"from": "DodgeRoll", "to": "Staggered", "tick": 4134},
    {"from": "Staggered", "to": "Idle", "tick": 4160}
  ]
}
```

---

## 2. Minimal Reproduction Steps

1. Load attached save snapshot `bug_2026_042_save.json` (or spawn in `arena_courtyard_02` with `seed = 948102`).
2. Press `Attack` (`LMB`), then buffer `Dodge` (`Left Shift`) during the recovery cancel window (`tick 4118`).
3. Allow the `warden_mech` shockwave (which bypasses normal i-frames) to hit the player on the final frame of `DodgeRoll` (`tick 4134`).

---

## 3. Expected vs Actual Behavior

- **Expected**: `DodgeRoll.exit("Staggered")` runs unconditionally and re-enables `PlayerHurtbox.monitorable = true`.
- **Actual**: `apply_shockwave_stagger()` overwrote `current_state_name = &"Staggered"` directly instead of calling `state_machine.transition_to(&"Staggered")`, bypassing `DodgeRoll.exit()` and leaving the player permanently invulnerable.

---

## 4. Root Cause & Verification Test

- **Root Cause**: Direct field mutation on `state_machine.current_state_name` inside `ShockwaveHazard._on_area_entered`.
- **Fix**: Route all forced interrupts through `state_machine.transition_to(&"Staggered", {"force": true})` and make `current_state_name` private/read-only.
- **Regression Test Added**: `tests/test_state_machine_interrupts.py::test_exit_hook_called_on_forced_stagger`.
