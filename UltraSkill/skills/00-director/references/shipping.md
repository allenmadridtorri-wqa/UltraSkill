# Final Shipping Gate & Honesty Audit

## 1. Pre-Ship Verification Sequence

Before declaring any deliverable complete, execute these steps in order:

1. **Gate Script Verification**:
   ```bash
   python3 skills/00-director/scripts/check_gates.py --ledger <path-to-project-ledger>
   ```
   Confirm every bar in `BARS.md` has a numeric score `>= 4` (on a 0–5 scale) and `QUALITY.md` contains zero open Blocker (`BLKR`) or Major (`MAJR`) defects.

2. **Package Integrity Audit (when editing UltraSkill itself)**:
   ```bash
   python3 tools/validate.py
   ```
   Confirm `<= 300` files (`288` exact), manifest parity, frontmatter compliance, link resolution, zero placeholders, valid Python AST, and valid JSON.

## 2. Mandatory Honesty Split in Final Reports

A 4 GB RAM laptop with 1 GB Intel UHD graphics cannot run Blender Cycles OptiX locally or compile heavy Windows native binaries locally. Therefore, every final report must separate verification into two explicit lists:

### A. Verified Locally in This Environment
List only the exact commands you actually executed and observed exit code `0` for:
- `python3 tools/validate.py`
- `python3 skills/00-director/scripts/check_gates.py`
- Python unit test suites (`unittest`), AST checks, manifest audits, budget calculators, and static geometry/material linter logic tests.
- WebGL / Three.js LOW preset inspection if a headless browser check was executed.

### B. Must Be Run by the User on Target Cloud Hardware
State clearly the exact command the user must execute on Google Colab GPU or GitHub Actions, and what output confirms success:
- **Google Colab GPU (T4 or better)**:
  - Upload or generate the `.blend` scene and run `blender -b -P skills/14-blender-pipeline/scripts/optix_verify.py` to confirm OptiX hardware engagement and `nvidia-smi` telemetry.
  - Run `benchmark_scene.py` on 3 frames before launching `render_sequence.py`.
  - Inspect the rendered EXR/PNG frames against `FAKE_3D_CHECKLIST.md`.
- **GitHub Actions CI**:
  - Push the repository or tag (`v1.0.0`) to trigger `.github/workflows/` for Windows `.exe` compilation and download the build artifact and `SHA256SUMS.txt`.

## 3. Refusal Rules

Never output any of the following:
- "I rendered this with Cycles on your machine and verified photorealism." (Impossible without an OptiX GPU runtime).
- "Guaranteed 100% indistinguishable from a real photograph." (Realism is a measurable bar to test against via `FAKE_3D_CHECKLIST.md`, never a marketing guarantee).
- "All tests pass" when no test command was executed.
