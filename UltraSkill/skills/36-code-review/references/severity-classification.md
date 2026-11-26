# Severity Classification (`P0 – P3`)

Every code review finding must carry an explicit severity tag so authors immediately know what blocks a release versus what is an optional suggestion.

---

## 1. The Four Severity Tiers

| Tag | Name | Criteria | Concrete Examples |
|---|---|---|---|
| **`[P0]`** | **Critical Blocker** | Exploitable security vulnerability, crash/exception on valid input, data loss/save corruption, OOM on target hardware (`4 GB RAM` / `16 GB T4`), or silent fallback from OptiX GPU to CPU rendering | Unparameterized SQL f-string; `zip.extractall()` without path check; missing `.tmp` atomic save; Cycles rendering on `CPU` device in Colab |
| **`[P1]`** | **Major Defect** | Incorrect business/gameplay logic, unhandled boundary edge case, memory/VRAM leak, frame budget violation (`p95 > 16.67 ms` on LOW), race condition, or missing regression test for a bug fix | Melee hitbox damages same enemy 6 times in 1 swing; `new THREE.Vector3()` inside `requestAnimationFrame`; truncated `.exr` skipped on resume |
| **`[P2]`** | **Moderate Issue** | Coupling domain logic to I/O, missing structured error context, suboptimal $O(N \log N)$ where $O(N)$ is simple, or incomplete docstring/CLI `--help` | Business calculation opens SQLite directly instead of taking a data struct; error log omits `frame_num` |
| **`[P3]`** | **Minor Nit** | Local variable naming improvement, minor comment clarification, optional micro-cleanup | Prefix with `Nit: Rename 'd' to 'duration_sec' for clarity` |

---

## 2. Verdict Decision Matrix

- **`CHANGES_REQUESTED`**: Any `[P0]` or `[P1]` finding is present, or `> 3` unaddressed `[P2]` findings accumulate.
- **`APPROVED_WITH_NITS`**: Zero `[P0]` and zero `[P1]` findings; only minor `[P2]`/`[P3]` suggestions that can be applied before merge without re-review.
- **`APPROVED`**: Zero `[P0]`, `[P1]`, or `[P2]` defects; all automated validators and tests pass.
