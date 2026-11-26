---
name: 00-director
description: >-
  Studio director skill that governs project intake, measurable quality bars,
  the 5-round iterative studio loop (fixing only the single weakest item per
  round), usage budget limits, inter-skill handoffs, and final shipping gates.
  Load at the start of every multi-step 3D, game, or coding project.
---

# 00-Director: Studio Quality Loop & Production Control

You run production like a veteran supervisor: no work starts without a brief and measurable bars, every round inspects real output, only the single weakest item is changed per round, and rounds halt at the cap of 5.

## When to use

Load this skill at the start of any 3D render, trailer, VFX shot, interactive scene, game build, or software deliverable, and return to it after each execution round to score output and log progress.

## Inputs

- Raw user request.
- Hardware profile (default: 4 GB RAM / 1 GB Intel UHD laptop + Colab Tesla T4 OptiX GPU + GitHub Actions CI).
- Existing ledger files (`BRIEF.md`, `BARS.md`, `ROUNDS.md`, `DECISIONS.md`, `QUALITY.md`) if resuming.

## Steps

1. **Scaffold the project ledger**:
   - Run `python3 skills/00-director/scripts/init_project.py --name <slug> --output <dir>` or copy the 5 templates from `templates/`.
2. **Execute the 9-step Quality Loop**:
   1. **Brief**: Fill out [`templates/BRIEF.md`](templates/BRIEF.md) using [`references/intake.md`](references/intake.md). Lock target medium, delivery resolution/platform, hardware boundary, and non-goals.
   2. **Measurable bars**: Fill out [`templates/BARS.md`](templates/BARS.md) using [`references/quality-gates.md`](references/quality-gates.md). Every bar must have a numeric or observable pass condition.
   3. **Plan**: Record architectural or artistic choices in [`templates/DECISIONS.md`](templates/DECISIONS.md) and select the next skill via [`references/handoffs.md`](references/handoffs.md).
   4. **Smallest version**: Build the smallest verifiable unit first (a single PREVIEW still frame before animation, a greybox 30-second loop before full levels, or a pure-logic unit test before full CLI/UI).
   5. **Render or run**: Execute the script, test suite, or Colab OptiX render. Never claim execution if it could not run locally.
   6. **Inspect the real output**: Examine actual rendered pixels, frame-time CSVs, test output, or AST/linter reports. Complete [`templates/QUALITY.md`](templates/QUALITY.md).
   7. **Score against bars**: Score every bar in `BARS.md` (0–5 scale, pass threshold >= 4, no Blocker defects).
   8. **Fix the weakest item only**: Identify the single lowest-scoring bar in `BARS.md`. Apply one targeted fix so cause and effect remain isolated. Never lower quality settings silently to pass a performance or render-time gate.
   9. **Log it**: Append the round entry to [`templates/ROUNDS.md`](templates/ROUNDS.md) via `python3 skills/00-director/scripts/log_round.py`.
3. **Enforce round cap and shipping check**:
   - Stop immediately when all bars pass, or when **Round 5** finishes. At Round 5, report current scores, remaining gap, and recommended next options to the user.
   - Before declaring done, run `python3 skills/00-director/scripts/check_gates.py` and follow [`references/shipping.md`](references/shipping.md).

## Numbers and defaults

- **Default round cap**: `5` rounds maximum before mandatory user report (starting value).
- **Changes per round**: `1` (the single weakest scored bar item).
- **Minimum bar pass score**: `4 / 5` on every bar, with `0` Blocker (`BLKR`) defects.
- **Max active domain skills loaded simultaneously**: `3` (plus `00-director`) to protect context budget; see [`references/usage-budget.md`](references/usage-budget.md).
- **Colab GPU approval gate**: `3.0 hours` estimated total render time (calculated from a 3-frame benchmark).

## Failure modes and fixes

- **Shotgun editing multiple variables in one round**: If lighting, camera focal length, and shader roughness all change at once, you cannot tell which change broke the image. Revert and fix only the lowest-scored bar.
- **Animating before a still passes**: Rendering 240 frames before 1 keyframe passes the Fake-3D checklist wastes hours of Colab T4 quota. Lock stills at `PREVIEW` and `REVIEW` first.
- **Silent quality downgrade**: Dropping resolution, disabling motion blur, or falling back to CPU without user consent is a Blocker defect. Halt and ask the user.
- **Regenerating already-passing files or frames**: Check `ROUNDS.md` and `render_manifest.json`; skip verified artifacts.

## Done check

- `BRIEF.md`, `BARS.md`, `ROUNDS.md`, `DECISIONS.md`, and `QUALITY.md` are populated with real observations.
- `python3 skills/00-director/scripts/check_gates.py --ledger <dir>` exits with code `0`.
- Final report explicitly separates checks executed locally from checks the user must run on Colab or GitHub Actions.

## Related files

- [`references/intake.md`](references/intake.md)
- [`references/rounds.md`](references/rounds.md)
- [`references/quality-gates.md`](references/quality-gates.md)
- [`references/usage-budget.md`](references/usage-budget.md)
- [`references/handoffs.md`](references/handoffs.md)
- [`references/shipping.md`](references/shipping.md)
- [`templates/BRIEF.md`](templates/BRIEF.md)
- [`templates/BARS.md`](templates/BARS.md)
- [`templates/ROUNDS.md`](templates/ROUNDS.md)
- [`templates/DECISIONS.md`](templates/DECISIONS.md)
- [`templates/QUALITY.md`](templates/QUALITY.md)
- [`scripts/init_project.py`](scripts/init_project.py)
- [`scripts/log_round.py`](scripts/log_round.py)
- [`scripts/check_gates.py`](scripts/check_gates.py)
