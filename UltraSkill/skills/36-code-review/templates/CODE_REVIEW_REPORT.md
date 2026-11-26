# Technical Code & Pipeline Review Report (`CODE_REVIEW_REPORT.md`)

- **Target Reviewed**: `<PR / Directory / Script Paths>`
- **Pillar(s)**: `[ ] 3D | [ ] Game Dev | [ ] Coding`
- **Automated Pre-Scan**: `PASS (0 static errors)`
- **Final Verdict**: `[ ] APPROVED | [ ] APPROVED_WITH_NITS | [x] CHANGES_REQUESTED`

---

## 1. Executive Summary

Provide a 2–3 sentence technical assessment summarizing architectural soundness, hardware budget compliance (`4 GB RAM / 1 GB Intel UHD` & `Colab T4 OptiX`), and the count of blocking vs non-blocking findings:
- **Findings Count**: `1 x [P0]`, `1 x [P1]`, `1 x [P2]`, `1 x [P3]`

---

## 2. Findings (Ordered by Severity `P0 -> P3`)

### `[P0]` Unchecked Path Concatenation Allows Arbitrary File Overwrite
- **Location**: `src/exporter.py:84`
- **Failure Scenario**: Passing `--output-name "../../.bashrc"` resolves outside `exports/` and overwrites user dotfiles.
- **Fix**:
  ```python
  safe_target = (export_root / user_filename).resolve()
  if not safe_target.is_relative_to(export_root.resolve()):
      raise ValueError(f"Path traversal blocked: {user_filename}")
  ```

### `[P1]` Melee Hitbox Remains Active if Actor is Staggered Mid-Swing
- **Location**: `scripts/states/attack_state.gd:42`
- **Failure Scenario**: `weapon_hitbox.monitoring = true` is set on frame 6, but `disable_hitbox()` is only called inside `_on_animation_finished()`. If the actor takes stagger damage on frame 8, the hitbox stays permanently active in `Staggered` and `Idle` states.
- **Fix**: Move `weapon_hitbox.set_deferred("monitoring", false)` into `AttackState.exit(next_state: StringName)` so every transition out of `AttackState` guarantees cleanup.

### `[P2]` Missing Timeout on External FFmpeg Subprocess
- **Location**: `scripts/encode.py:29`
- **Impact**: A stalled pipe hangs the CI worker indefinitely. Add `timeout=120` to `subprocess.run(...)`.

### `[P3]` Nit: Clarify Unit in Variable Name
- **Location**: `scripts/camera_rig.py:15`
- **Suggestion**: Rename `focal` to `focal_length_mm` to match `sensor_width_mm`.

---

## 3. Verification Checklist Before Re-Review

- [ ] All `[P0]` and `[P1]` fixes applied with accompanying unit/regression tests.
- [ ] `python3 skills/36-code-review/scripts/pre_review_scan.py --path <target>` exits with `0`.
