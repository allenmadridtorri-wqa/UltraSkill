# Inter-Skill Handoff Contracts

When a project moves from one skill to the next, the upstream skill must hand off a verified artifact rather than raw unvalidated work.

## 1. 3D & VFX Pipeline Handoffs

```text
[00-director] -> [10-art-direction] -> [11-modeling] -> [12-materials-lighting]
      -> [13-rigging-animation] -> [16-vfx] -> [14-blender-pipeline] -> [15-film-trailer]
```

| From Skill | To Skill | Required Handoff Artifact & Gate |
|---|---|---|
| `00-director` | `10-art-direction` | Approved `BRIEF.md` and `BARS.md` with target resolution, aspect ratio, and hardware ceiling. |
| `10-art-direction` | `11-modeling` | `SHOT_LIST.md` with camera focal lengths (e.g., `35mm`, `50mm`, `85mm`), f-stops, and hero/background asset breakdown so modelers do not over-detail background props. |
| `11-modeling` | `12-materials-lighting` | Clean geometry passing `mesh_linter.py` (`1.0 m` scale, transforms applied, bevels present, non-overlapping UVs). |
| `12-materials-lighting` | `14-blender-pipeline` | Materials passing `audit_materials.py`, physical lights placed, `AgX` view transform set, zero flat fill. |
| `13-rigging-animation` | `14-blender-pipeline` | Baked keyframe actions (`bake_animation.py`), zero foot sliding, physical camera rig motion curve checked. |
| `16-vfx` | `14-blender-pipeline` | Simulation budget checked (`sim_budget_estimator.py`), OpenVDB/Alembic caches baked to Drive, EXR AOV passes configured (`setup_vfx_passes.py`). |
| `14-blender-pipeline` | `15-film-trailer` | Verified frame sequences (`verify_frames.py` exit code `0`) in 16-bit PNG or OpenEXR on Google Drive. |
| `14-blender-pipeline` | `17-realtime-web-scenes` | Cycles-baked diffuse/AO lightmaps (`bake_lightmap_blender.py`) and glTF passing `gltf_budget_check.py`. |

## 2. Game Development Pipeline Handoffs

```text
[00-director] -> [20-game-design] -> [21-engine-architecture] -> [22-gameplay-systems]
      -> [23-ai-physics] / [24-networking-backend] -> [25-ui-audio] -> [26-optimization] -> [27-production-qa-release]
```

| From Skill | To Skill | Required Handoff Artifact & Gate |
|---|---|---|
| `20-game-design` | `21-engine-architecture` | `GDD_ONE_PAGER.md` and `LEVEL_METRICS.md` with player speed, jump envelope, and TTK numbers verified via `balance_simulator.py`. |
| `21-engine-architecture` | `22-gameplay-systems` | Fixed-timestep loop (`60 Hz`), object pool manager, and versioned save schema (`save_schema_validator.py`). |
| `22-gameplay-systems` | `23-ai-physics` | Working player controller, hitbox/hurtbox collision bitmasks (`collision_matrix_gen.py`), and state machine signals. |
| `25-ui-audio` | `26-optimization` | Accessible HUD, audio bus layout, and localization table passing `check_loc_strings.py`. |
| `26-optimization` | `27-production-qa-release` | `PERF_REPORT.md` proving LOW preset `p95 <= 33.33 ms` on 4 GB RAM / 1 GB Intel UHD target (`analyze_frame_times.py`). |

## 3. Software Engineering Pipeline Handoffs

```text
[00-director] -> [30-architecture] -> [31-languages] / [32-web-backend-data]
      -> [33-testing-debugging] -> [34-security] -> [36-code-review] -> [35-devops-ci]
```

| From Skill | To Skill | Required Handoff Artifact & Gate |
|---|---|---|
| `30-architecture` | `31-languages` / `32-web-backend-data` | `ADR_TEMPLATE.md` defining module boundaries, pure-logic core, I/O adapters, and error contracts. |
| `31-languages` | `33-testing-debugging` | Runnable modules with `--help`, strict types, and zero placeholders. |
| `33-testing-debugging` | `34-security` | Unit and integration test suite passing via `run_test_suite.py`. |
| `34-security` | `36-code-review` | Clean `secret_scanner.py` output and boundary validation audit. |
| `36-code-review` | `35-devops-ci` | `CODE_REVIEW_REPORT.md` with `0` BLKR and `0` MAJR issues, ready for CI packaging and `checksum_manifest.py`. |
