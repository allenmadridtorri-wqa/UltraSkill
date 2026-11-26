# Eval 06 — Multi-Pillar Code & Render Audit (`P0 – P3` Triage)

## 1. Benchmark Prompt

> "Review a mixed PR containing a Blender Cycles script, a Godot combat state script, and a Python file exporter. Identify all `P0` and `P1` defects with exact `file:line` numbers, failure scenarios, and drop-in fixes."

---

## 2. Skills Routed

1. [`skills/36-code-review/SKILL.md`](../skills/36-code-review/SKILL.md) (Automated `pre_review_scan.py`, 5-pass review protocol, `P0–P3` severity classification, `CODE_REVIEW_REPORT.md`)
2. [`skills/10-art-direction/templates/FAKE_3D_CHECKLIST.md`](../skills/10-art-direction/templates/FAKE_3D_CHECKLIST.md) (10 fake-3D tells audit)
3. [`skills/34-security/SKILL.md`](../skills/34-security/SKILL.md) (Command injection, path traversal, bare `except` detection)

---

## 3. Pass / Fail Grading Rubric (100 Points Total — Pass Threshold `>= 90`)

| Check ID | Criterion | Points | Verification Command / Method |
|---|---|---|---|
| `E06-1` | **Automated Static Pre-Scan Execution**: Runs `pre_review_scan.py` first and flags `eval()`, `shell=True`, mutable default arguments, and bare `except:` blocks | `30` | `python3 skills/36-code-review/scripts/pre_review_scan.py --self-test` |
| `E06-2` | **Accurate `P0 / P1` Triage**: Correctly classifies security/crash/silent-CPU-fallback bugs as `[P0]` and logic/frame-budget/hitbox-cleanup bugs as `[P1]` | `35` | Compare output against `skills/36-code-review/templates/CODE_REVIEW_REPORT.md` |
| `E06-3` | **Actionable Drop-In Fixes**: Every finding provides exact `file:line`, concrete trigger scenario, and complete replacement code | `35` | Inspect generated `CODE_REVIEW_REPORT.md` |
