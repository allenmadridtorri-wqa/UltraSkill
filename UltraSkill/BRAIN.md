# UltraSkill Brain: Veteran Decision Rules & Mental Models

This document captures how a 10-year 3D/VFX Supervisor, a 10-year Game Technical Director, and a 10-year Principal Software Engineer think, measure, diagnose failure, and decide what is ready to ship.

---

## Pillar 1: 3D, Lighting, Cycles OptiX & VFX

### How a 10-Year 3D Lead Decides
1. **Reference before polygons**: Never set a focal length, light ratio, or roughness value from memory. Collect real photographs shot with known lenses and lighting conditions first.
2. **Scale and camera anchor realism**: Real-world scale (`1 unit = 1.0 meter`) is non-negotiable because subsurface scattering radius, depth of field, volumetric density, and rigid-body gravity are physically parameterized in meters.
3. **Imperfection is in the roughness and normals, not the albedo**: Beginners paint noisy dirt into base color. Veterans keep base color within physically plausible PBR ranges (`0.04` charcoal to `0.80` fresh snow) and put 80% of the storytelling into roughness breakups, micro-bevels (`0.5 mm` to `3.0 mm`), and subtle surface warps.
4. **Light by subtraction and motivation**: Turn off all world fill. Add one motivated key light (sun, window, practical lamp), let indirect bounce provide fill, and use negative fill (black flags) to preserve contrast. View every lighting setup through **AgX** and **False Color**.

### What Usually Fails in 3D (and How to Diagnose It)
- **Razor-sharp 90-degree edges**: Nothing manufactured has a zero-radius corner. Without a bevel catchlight, objects read as 1990s CG polygons. *Fix*: Bevel modifier (`0.5 mm–5 mm`, 2–3 segments, Harden Normals).
- **Uniform specular reflections**: A plastic or metal surface with constant `roughness = 0.2` reflects light like a mathematical mirror. *Fix*: Layer fingerprint, wipe-mark, and dust-cavity masks across a narrow roughness band (e.g., `0.16` to `0.34`).
- **Floating contact**: Objects touching a floor without a contact gap, subtle indentation, or tight ambient occlusion shadow appear pasted on.
- **Temporal denoiser flicker**: Low sample counts + spatial denoising in animation cause boiling textures in shadows. *Fix*: Test a 24-frame motion strip at REVIEW preset, compare against a 2048-sample crop, raise minimum samples, or composite denoised passes carefully.
- **The Uncanny Five**: Digital humans (skin/eyes), groom hair, dynamic cloth, open water splashes, and close-up fire are the five hardest subjects in CG. When budget or T4 VRAM is constrained, frame them in silhouette, behind visor/glass, at medium distance, or as environmental accents rather than full-screen macro hero shots.

---

## Pillar 2: Game Development (A-to-AAA Technical Direction)

### How a 10-Year Game Technical Director Decides
1. **Prove the 30-second loop in greybox**: If moving, jumping, aiming, or striking a primitive box in an untextured room does not feel responsive in the first 30 seconds, 4K textures and orchestral music will not save the game.
2. **Lock spatial metrics before building levels**: Define jump height, sprint speed, door width, and cover height in a shared `LEVEL_METRICS.md` file. Every environment artist and gameplay programmer builds to those exact numbers.
3. **Frame time is a hard physical budget**:
   - **60 FPS** = `16.67 ms` per frame.
   - **30 FPS (LOW preset laptop baseline)** = `33.33 ms` per frame.
   - Always measure **p95 and p99 frame times** in milliseconds, never average FPS. An average of 60 FPS with a 120 ms garbage-collection spike every 3 seconds feels broken.
4. **Realtime vs Offline Honesty**: A browser or integrated GPU has roughly 0.001% of the time budget per frame that an offline Cycles OptiX frame gets on a Tesla T4. Never promise path-traced quality in WebGL; bake static GI lightmaps from Cycles and design art direction around clean silhouettes and controlled specular highlights.

### What Usually Fails in Games (and How to Diagnose It)
- **Sluggish controls**: No coyote time (`100 ms` grace after leaving a ledge) and no input buffering (`120 ms` jump/attack queue before landing). Players blame "unresponsive keys."
- **Swarming AI**: Every enemy attacks the player simultaneously. *Fix*: An Attack Token Manager that grants only 1–2 simultaneous melee attack tickets while remaining enemies circle or flank.
- **Unbounded allocations in the update loop**: Instantiating bullets, particles, or strings inside `_process(delta)` or `requestAnimationFrame` causes GC hitches and crashes 4 GB laptops. *Fix*: Pre-allocate fixed-size object pools at scene load.

---

## Pillar 3: Principal Software Engineering

### How a 10-Year Principal Engineer Decides
1. **Parse, don't guess, at system boundaries**: Validate every CLI flag, HTTP payload, file path, and JSON config at the outer edge before passing typed structures into pure domain functions.
2. **Decouple pure logic from I/O**: Business rules, frame budget math, manifest resume state, and combat equations belong in pure functions with zero filesystem, network, or engine dependencies so they can be unit-tested in `< 100 ms`.
3. **Loud failures over silent corruption**: If a required GPU device is missing, a migration checksum mismatches, or an input file is truncated, exit immediately with a non-zero status code and an actionable error message stating what failed and how to fix it.
4. **Scientific debugging**: Never shotgun random edits. Reproduce the bug deterministically, bisect the failure boundary, state a falsifiable hypothesis, confirm it with a test or log, write a regression test that fails, and apply the minimal fix.

---

## What We Refuse to Ship Across All Pillars

1. Silent fallback from GPU OptiX to CPU in Blender Cycles.
2. Untested multi-hour Colab render jobs without a 3-frame benchmark and Drive frame-by-frame persistence.
3. Realtime scenes or games without a working **LOW preset** for 4 GB RAM / 1 GB Intel UHD hardware.
4. Scripts with `TODO`, `...`, placeholder stubs, or missing `--help` flags.
5. Hardcoded secrets, path-traversal vulnerabilities, or unparameterized SQL queries.
6. Claims that an output was rendered, tested, or verified when it was not actually executed.
