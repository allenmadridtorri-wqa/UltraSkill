# The Scientific Root-Cause Debugging Method

When code breaks, amateur developers guess and randomly tweak lines until the symptom disappears ("shotgun debugging"). Veteran engineers follow a strict **5-Step Scientific Debugging Protocol** that finds the true root cause in minutes.

---

## 1. The 5-Step Protocol

### Step 1: Stabilize & Reproduce Deterministically
- Turn an intermittent complaint (*"Sometimes frame verification fails"*) into a **100% repeatable 1-command reproduction** (`python3 verify_frames.py --input repro_case/`).
- Lock all variables: fixed RNG seed, fixed input payload, exact environment flags. If you cannot reproduce a bug on demand, you cannot prove you fixed it.

### Step 2: Binary Search the Fault Boundary (Wolf Fence Algorithm)
Instead of stepping through 2,000 lines in a debugger line-by-line:
- Check the data state halfway through the pipeline (`Stage 3 of 6`).
  - Is the data already corrupted at Stage 3? The bug is in Stages `1–3`.
  - Is the data still clean at Stage 3? The bug is in Stages `4–6`.
- In `3–4` halving steps ($\log_2 N$), you narrow a 16-module pipeline down to the exact 20-line function that corrupted the invariant.
- For regressions across Git history, use `git bisect start` + `git bisect run python3 test_repro.py` to find the exact offending commit automatically.

### Step 3: Form a Falsifiable Hypothesis
- State your hypothesis explicitly before touching code:
  *"Hypothesis: `verify_frames.py` fails on frame `1000` because the regex `r'_(\d{3})\.exr$'` only matches 3-digit padding instead of 4+ digits."*
- Predict what a diagnostic print/assertion at that line will output if your hypothesis is true.

### Step 4: Write the Failing Regression Test First
- Encode the reproduction input (`frame_1000.exr`) as an automated unit test.
- Run the test and watch it **FAIL** for the exact expected reason.

### Step 5: Apply the Minimal Fix & Audit Sibling Bugs
- Apply the fix and watch the regression test **PASS**.
- **Sibling Audit**: Ask *"Where else in this codebase did we make the same 3-digit regex assumption?"* (`grep -rn`) and fix all sibling occurrences in the same commit.
