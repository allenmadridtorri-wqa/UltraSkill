# Eval 01 — Hyperrealistic Cycles Studio Still on Colab OptiX GPU

## 1. Benchmark Prompt

> "Create a photorealistic macro product still of a brushed stainless-steel espresso portafilter resting on a dark walnut counter with subtle water droplets. My laptop only has 4 GB RAM and 1 GB Intel UHD graphics, so generate a complete headless Blender Python script ready for Google Colab GPU (`Tesla T4`) and a local dry-run validator."

---

## 2. Skills Routed

1. [`skills/00-director/SKILL.md`](../skills/00-director/SKILL.md) (Hardware routing: local dry-run JSON vs Colab T4 OptiX render)
2. [`skills/10-art-direction/SKILL.md`](../skills/10-art-direction/SKILL.md) (`85mm` macro lens, `f/4.0`, 10-tell fake-3D elimination)
3. [`skills/11-modeling/SKILL.md`](../skills/11-modeling/SKILL.md) (`1 unit = 1.0 m`, bevels `>= 0.3 mm` with `3+` segments)
4. [`skills/12-materials-lighting/SKILL.md`](../skills/12-materials-lighting/SKILL.md) (PBR dielectric clamp `[0.02, 0.85]`, 3-point softbox lighting, `AgX`)
5. [`skills/14-blender-pipeline/SKILL.md`](../skills/14-blender-pipeline/SKILL.md) (`CYCLES` + `OPTIX` + `OPENIMAGEDENOISE`, `16-bit OpenEXR`)

---

## 3. Pass / Fail Grading Rubric (100 Points Total — Pass Threshold `>= 90`)

| Check ID | Criterion | Points | Verification Command / Method |
|---|---|---|---|
| `E01-1` | **OptiX GPU Enforced & CPU Disabled**: Script sets `compute_device_type = 'OPTIX'`, enables GPU (`use = True`), disables CPU (`use = False`), and raises `RuntimeError` if no GPU is found | `25` | Inspect AST / run `examples/01-cycles-studio-still/audit_still.py --self-test` |
| `E01-2` | **No Local Heavy Render Triggered**: Script runs cleanly in `--dry-run` / `--self-test` mode on a 4 GB RAM laptop in `< 1s` without requiring local Cycles | `20` | `python3 examples/01-cycles-studio-still/build_still_scene.py --self-test` |
| `E01-3` | **AgX + 16-bit OpenEXR + OIDN**: `view_transform = 'AgX'`, `file_format = 'OPEN_EXR'`, `color_depth = '16'`, `denoiser = 'OPENIMAGEDENOISE'` with Albedo+Normal passes | `20` | Verified in scene spec JSON |
| `E01-4` | **Physical Scale & Bevels**: All hard-surface meshes have metric dimensions and bevel radii `>= 0.2 mm` (`>= 2` segments) | `20` | Verified by `audit_still.py` |
| `E01-5` | **PBR Energy Conservation**: Dielectric base colors within `[0.02, 0.85]` linear RGB; binary metallic (`0.0` or `1.0`); non-zero roughness variation | `15` | Verified by `audit_still.py` |
