---
name: ultraskill-code-review
description: Systematic multi-pass code and asset review covering severity classification (P0 Blocker to P3 Nit), cross-pillar checklists (3D, Game Dev, Coding), automated pre-review static scanning, and actionable review reports.
---

# 36 — Severity-Ranked Code & Pipeline Review

This skill executes rigorous, evidence-based technical reviews across all three UltraSkill pillars (3D, Game Dev, Coding): running automated static pre-scans first, evaluating code/scenes through a 5-pass inspection protocol, classifying findings by severity (`P0 Blocker` through `P3 Nit`), and supplying exact line numbers and drop-in fixes.

## When to use

- Reviewing a pull request, commit diff, Blender automation script, Three.js scene, Godot gameplay system, or backend service before merge or release.
- Auditing an existing repository for security vulnerabilities, performance bottlenecks, fake-3D tells, or missing test coverage.
- Producing a structured `CODE_REVIEW_REPORT.md` with clear merge gate verdicts (`APPROVED`, `APPROVED_WITH_NITS`, `CHANGES_REQUESTED`).

## Inputs

- Target files, directory, or Git diff to review.
- Relevant pillar quality bars (`FAKE_3D_CHECKLIST.md`, `PERF_REPORT.md`, `MILESTONE_GATE.md`).

## Steps

1. **Run the Automated Pre-Review Scanner First**:
   - Execute [scripts/pre_review_scan.py](scripts/pre_review_scan.py) on the target path to catch syntax errors, bare `except:` blocks, `shell=True` calls, `TODO`/`FIXME` placeholders, oversized functions, and missing type hints before human/agent inspection begins.
2. **Execute the 5-Pass Review Method**:
   - Follow [references/review-method-and-triage.md](references/review-method-and-triage.md) in strict priority order:
     - **Pass 1**: Architecture, Boundaries & Hardware Fit (`4 GB RAM / 1 GB Intel UHD` compliance, Colab OptiX offload).
     - **Pass 2**: Security & Data Integrity (SQLi, Path Traversal, Secrets, Atomic Saves).
     - **Pass 3**: Correctness, Concurrency & Edge Cases (`NaN`, off-by-one, timeouts, state machine `exit()` hooks).
     - **Pass 4**: Performance & Resource Budgets (`16.67 ms` frame budget, draw calls, VRAM, $O(N^2)$ loops).
     - **Pass 5**: Test Coverage, Readability & Maintainability.
3. **Classify Findings by Severity (`P0 – P3`)**:
   - Assign every defect an objective severity level using [references/severity-classification.md](references/severity-classification.md).
4. **Verify Pillar-Specific Checklists**:
   - Cross-check domain rules for 3D (`OptiX`, `AgX`, bevels), Game Dev (`coyote time`, pooling, squad tokens), and Coding (`WAL` mode, parameterized SQL) using [references/pillar-review-checklists.md](references/pillar-review-checklists.md).
5. **Emit the Actionable Review Report**:
   - Format the final verdict using [templates/CODE_REVIEW_REPORT.md](templates/CODE_REVIEW_REPORT.md) with `file:line`, failure scenario, and concrete code fix for every finding.

## Numbers and defaults

| Severity Tier | Merge Gate Impact | Allowed Count for `APPROVED` |
|---|---|---|
| **`P0` — Critical Blocker** | Security exploit, crash, data corruption, OOM on 4 GB RAM / T4 VRAM, fake/silent CPU fallback | **`0`** |
| **`P1` — Major Defect** | Broken edge case, missing test for bug fix, `p95 > 16.67 ms` on LOW preset, race condition | **`0`** |
| **`P2` — Moderate Improvement** | Suboptimal abstraction, missing log context, minor duplication | Documented or fixed (`<= 3`) |
| **`P3` — Minor Nit / Polish** | Naming clarity, comment wording (prefix with `Nit:`) | Non-blocking |

## Failure modes and fixes

- **Symptom**: Reviewer spends 20 comments debating variable naming while missing a SQL injection or a per-frame memory leak on line 45.
  - **Fix**: Always execute Passes 1–4 (Architecture, Security, Correctness, Performance) and automated pre-scans **before** looking at style or naming (`Pass 5`).
- **Symptom**: Review feedback is vague (*"This function looks slow or unsafe"*), leaving the author guessing how to fix it.
  - **Fix**: Every `P0`/`P1`/`P2` finding in `CODE_REVIEW_REPORT.md` must include: (1) exact `file:line`, (2) concrete input or sequence that triggers the bug, and (3) a ready-to-apply code replacement.

## Done check

- [ ] `pre_review_scan.py` has been executed on all changed files with `0` critical static violations.
- [ ] All findings are ranked `P0` through `P3` with `file:line`, impact explanation, and concrete fix code.
- [ ] Merge gate verdict is `CHANGES_REQUESTED` if any `P0` or `P1` finding remains open.
- [ ] `python3 skills/36-code-review/scripts/pre_review_scan.py --self-test` exits with code `0`.

## Related files

- [references/review-method-and-triage.md](references/review-method-and-triage.md)
- [references/severity-classification.md](references/severity-classification.md)
- [references/pillar-review-checklists.md](references/pillar-review-checklists.md)
- [templates/CODE_REVIEW_REPORT.md](templates/CODE_REVIEW_REPORT.md)
- [scripts/pre_review_scan.py](scripts/pre_review_scan.py)
