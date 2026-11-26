# Measurable Quality Bars

Every bar must be scored from `0` to `5` after inspecting real output.
- **Pass rule**: Every bar score `>= 4`, and `0` Blocker (`BLKR`) defects open.
- **Iteration rule**: In each round, fix **only the single lowest-scoring bar**.

| Bar ID | Category | Measurable Pass Condition (Starting Values) | Verification Command / Artifact | Current Score (0-5) | Status |
|---|---|---|---|---:|---|
| `BAR-01` | Hardware / Constraint Compliance | OptiX GPU proven on Colab (`optix_verify.py`), or LOW preset `<= 33.33 ms` on 4 GB laptop, or zero-dependency CLI passes `--help` | `python3 skills/14-blender-pipeline/scripts/optix_verify.py` | 4 | PASS |
| `BAR-02` | Structural / Scale Integrity | Real-world metric scale (`1.0 m`), applied transforms, bevels `0.5-5.0 mm`, or clean module boundaries and schema validation | `python3 skills/11-modeling/scripts/mesh_linter.py` | 4 | PASS |
| `BAR-03` | Material / Logic Fidelity | PBR albedo `[0.04, 0.80]`, varied roughness, AgX color; or deterministic unit tests covering core rules and boundaries | `python3 skills/12-materials-lighting/scripts/audit_materials.py` | 4 | PASS |
| `BAR-04` | Visual / Functional Realism | 100% pass on `FAKE_3D_CHECKLIST.md` and denoiser vs 2048-sample crop check; or 30-second playable loop / CLI contract test | `QUALITY.md` inspection | 4 | PASS |
| `BAR-05` | Budget & Safety Gate | Peak VRAM `<= 12.5 GB` on T4, render time `<= 3.0 h`, zero secrets, zero `BLKR`/`MAJR` review defects | `python3 skills/00-director/scripts/check_gates.py` | 4 | PASS |
