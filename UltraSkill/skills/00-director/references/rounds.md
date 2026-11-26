# The 5-Round Iterative Studio Loop

## 1. Why Rounds Are Capped and Single-Variable

Unstructured iteration fails in two ways:
1. **Multi-variable thrashing**: Changing light intensity, camera lens, denoiser, and material roughness simultaneously makes it impossible to know which change improved or degraded the output.
2. **Unbounded token and GPU burn**: Re-running 10+ blind rounds consumes context windows and Colab GPU quota without converging.

UltraSkill enforces a strict **5-round maximum** with **one weakest-item fix per round**.

## 2. Round Progression By Pillar

| Round | Offline 3D / VFX / Trailer | Realtime Web 3D / Game | Software / CLI / Backend |
|---|---|---|---|
| **Round 1** | Blocking, metric scale check (`mesh_linter.py`), camera composition, clay/grey shader `PREVIEW` (960x540) still. | Greybox controller or scene bootstrap with LOW preset active; verify 30-second loop and resource disposal. | Pure-logic core module + deterministic `unittest` suite passing in `< 1 s` (starting value). |
| **Round 2** | Motivated physical lighting + PBR materials + AgX check (`audit_materials.py`); render `PREVIEW` still. | Add core interaction (combat/AI tokens or story graph triggers); verify metrics/state transitions. | Add CLI/HTTP boundary validation, persistence/migrations, and integration tests. |
| **Round 3** | Run Fake-3D checklist on `REVIEW` (1920x1080) still + high-sample reference crop; fix single weakest realism tell. | Add baked Cycles lightmaps / UI HUD / audio buses; run frame-time or glTF budget script. | Run security scan (`secret_scanner.py`) and code review scan (`pre_review_scan.py`); fix top defect. |
| **Round 4** | Motion/animation 24-frame strip check for temporal flicker + 3-frame Colab benchmark (`benchmark_scene.py`). | Polish game feel (hitstop, camera damping, accessibility toggles) and fix weakest p99 frame-time or UX bar. | Add GitHub Actions CI workflow, packaging checksums, and fix weakest edge-case bar. |
| **Round 5** | Final compositor film finish (grain/glare/grade) and `FINAL` render sequence assembly (`check_gates.py`). | Final smoke check across LOW and HIGH presets + release archive audit (`package_release_check.py`). | Final regression test run + gate sign-off (`check_gates.py`). |

## 3. Rules Inside Every Round

1. **Inspect real output**: Never score a round from imagination. Look at the rendered image, the `mesh_linter.py` output, the `unittest` report, or the frame-time percentiles.
2. **Score all bars (0–5)**:
   - `5`: Exceeds target; zero visible or measured flaws.
   - `4`: Passes bar threshold; shippable quality.
   - `3`: Noticeable flaw or minor threshold miss; requires a round fix.
   - `1–2`: Major defect or failed metric.
   - `0`: Not yet tested or Blocker (`BLKR`) failure.
3. **Pick the single weakest item**: Sort bars by ascending score. Select the lowest-scoring bar (tie-break by highest pipeline upstream impact: scale/geometry before materials, materials before lighting, lighting before post-processing).
4. **Never lower quality bars silently**: If a scene misses a T4 VRAM or render-time budget, optimize instancing, texture sizes, or volume bounds—never silently switch to CPU, drop from 1080p to 540p for delivery, or disable shadows without user approval.
5. **Hard Stop at Round 5**: If any bar remains `< 4` after Round 5, stop iterating, run `log_round.py`, and report the exact scores and trade-offs to the user.
