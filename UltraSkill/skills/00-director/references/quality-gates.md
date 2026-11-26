# Measurable Quality Gates Across Pillars

Every project must define 5–8 measurable bars in `BARS.md`. Use the starting values below and verify them with the paired script or inspection method.

## 1. Offline 3D & Cycles OptiX Gates

| Bar ID | Gate Name | Starting Value / Pass Threshold | Verification Method |
|---|---|---|---|
| `3D-01` | **OptiX Hardware Proof** | `compute_device_type == 'OPTIX'`, `scene.cycles.device == 'GPU'`, `>= 1` active OptiX device confirmed in `nvidia-smi` | Run `skills/14-blender-pipeline/scripts/optix_verify.py` on Colab GPU. |
| `3D-02` | **Metric Scale & Bevels** | `unit_scale == 1.0` (meters), all transforms applied (`scale == 1,1,1`), hero hard edges bevelled `0.5 mm – 5.0 mm` (starting value) | Run `skills/11-modeling/scripts/mesh_linter.py`. |
| `3D-03` | **PBR Energy & Roughness** | Dielectric albedo in `[0.04, 0.80]`, metallic in `{0.0, 1.0}` (except rusty transitions), zero constant-roughness hero materials | Run `skills/12-materials-lighting/scripts/audit_materials.py`. |
| `3D-04` | **Color & Dynamic Range** | View transform set to `AgX`, zero unmotivated ambient world fill, key-to-fill ratio `>= 2:1` (starting value), no clipped diffuse areas in False Color | Inspect AgX False Color pass and `apply_preset.py` log. |
| `3D-05` | **Denoiser vs Reference Crop** | Denoised frame preserves pore/scratch micro-detail when compared side-by-side against a `2048-sample` (starting value) border crop; zero temporal flicker over 24 frames | Record side-by-side comparison in `QUALITY.md`. |
| `3D-06` | **Fake-3D Audit** | `100%` of items in `FAKE_3D_CHECKLIST.md` marked PASS on approved `REVIEW` frame | Complete `skills/10-art-direction/templates/FAKE_3D_CHECKLIST.md`. |
| `3D-07` | **T4 VRAM & Time Budget** | Peak VRAM `<= 12.5 GB` (on 15 GB T4, starting value); estimated total time `<= 3.0 hours` (or user approval logged) | Run `vram_audit.py` and `benchmark_scene.py`. |

## 2. Realtime Web 3D & Game Development Gates

| Bar ID | Gate Name | Starting Value / Pass Threshold | Verification Method |
|---|---|---|---|
| `GM-01` | **LOW Preset Frame Budget** | `p95 <= 33.33 ms` (`>= 30 FPS`) on 1 GB Intel UHD / 4 GB RAM laptop at `1280x720`, `pixelRatio = 1.0`, shadows off | Run `skills/26-optimization/scripts/analyze_frame_times.py`. |
| `GM-02` | **Draw Call & Memory Ceiling** | LOW preset `<= 100` draw calls (`<= 50` for web scenes, starting value), `<= 256 MB` GPU textures, `<= 1.5 GB` process RAM | Run `gltf_budget_check.py` and inspect renderer info telemetry. |
| `GM-03` | **Controller Responsiveness** | Coyote time `80–120 ms` (starting value), jump/action buffer `100–150 ms` (starting value), deterministic fixed physics step `60 Hz` | Inspect controller constants and unit/playtest log. |
| `GM-04` | **Combat / Economy Balance** | Monte Carlo TTK within `+-15%` (starting value) of target design duration over `1000` simulated encounters | Run `skills/20-game-design/scripts/balance_simulator.py`. |
| `GM-05` | **Accessibility & Audio** | Full keyboard/gamepad nav, remappable actions, colorblind-safe cues, master/music/SFX/voice sliders, trailer/game audio `-14 LUFS +- 1 LU` (`<= -1.0 dBTP`) | Run `check_loc_strings.py` and `loudness_check.py`. |

## 3. Software Engineering Gates

| Bar ID | Gate Name | Starting Value / Pass Threshold | Verification Method |
|---|---|---|---|
| `SW-01` | **Zero-Placeholder Policy** | `0` occurrences of `TODO`, `FIXME`, `...` stub bodies, or missing `--help` CLI handlers | Run `tools/validate.py` and `pre_review_scan.py`. |
| `SW-02` | **Deterministic Unit Suite** | `100%` tests passing, zero network/sleep dependencies in unit tests, total unit runtime `< 5.0 s` (starting value) | Run `skills/33-testing-debugging/scripts/run_test_suite.py`. |
| `SW-03` | **Security & Secret Hygiene** | `0` hardcoded secrets, parameterized SQL only, `shell=False` subprocess calls, verified path-traversal containment | Run `skills/34-security/scripts/secret_scanner.py`. |
| `SW-04` | **Code Review Severity Gate** | `0` Blocker (`BLKR`) and `0` Major (`MAJR`) findings open | Complete `skills/36-code-review/templates/CODE_REVIEW_REPORT.md`. |
