# Pillar-Specific Review Checklists

Use these domain-specific checklists during **Passes 1–4** depending on which UltraSkill pillar(s) the code touches.

---

## 1. 3D Pillar Checklist (`skills/10` – `18`)

- [ ] **OptiX GPU Proof**: Does the Colab/Blender script explicitly enable `compute_device_type = 'OPTIX'`, activate only the NVIDIA GPU (`use = True`) while disabling CPU (`use = False`), and fail fast if no OptiX GPU is found?
- [ ] **AgX Color Management**: Is `view_transform = 'AgX'` set for renders and `Linear` raw space enforced on Normal, Roughness, Metallic, and Displacement texture nodes?
- [ ] **Physical PBR & Bevels**: Are dielectric base colors clamped inside `[0.02, 0.85]`, metallic values binary `0.0` or `1.0`, and every hard edge beveled (`>= 0.5 mm`)?
- [ ] **Colab Resilience**: Are frames rendered to `16-bit OpenEXR (DWAA/ZIP)` with pre-resume verification (`size >= 32 KB` + magic bytes `\x76\x2f\x31\x01`) so disconnects never corrupt a sequence?
- [ ] **Three.js `LOW` Preset**: Does the web scene initialize on `LOW` preset (`720p`, `DPR 1.0`, `<= 150` draw calls, `<= 150k` triangles, `<= 512 MB` VRAM) for 1 GB Intel UHD GPUs and dispose geometries/textures on teardown?

---

## 2. Game Development Pillar Checklist (`skills/20` – `27`)

- [ ] **Frame-Rate Independence & Feel**: Do physics run in fixed `dt` (`60 Hz`), camera damping use exponential decay `exp(-decay * dt)`, and jumps include coyote time (`100 ms`) + jump buffering (`120 ms`)?
- [ ] **Zero Hot-Path Allocations**: Are projectiles, VFX sparks, and enemies acquired from a `NodePool` with a complete `on_pool_reset()` hook rather than `instantiate()` / `queue_free()` during combat?
- [ ] **State Machine & Hitbox Safety**: Do state machines guarantee `exit()` runs on forced stagger/death interrupts (disabling active weapon hitboxes and releasing Squad Attack Tokens)?
- [ ] **Collision & UI Hygiene**: Are passive `Hurtbox` areas set to `monitoring = false`, and do all menus maintain non-null gamepad/keyboard focus?

---

## 3. Coding Pillar Checklist (`skills/30` – `36`)

- [ ] **Security Boundaries**: Zero hardcoded secrets, 100% parameterized SQL (`?`), `subprocess.run(..., shell=False, timeout=...)`, and `Path.resolve().is_relative_to(base_dir)`.
- [ ] **SQLite & Concurrency**: Are `WAL`, `foreign_keys = ON`, and `busy_timeout = 5000` enabled, and are all queues/caches explicitly bounded (`maxsize`)?
- [ ] **Deterministic Tests**: Do tests cover valid, boundary, and malformed inputs using `tempfile.TemporaryDirectory()` with zero `time.sleep()` or external network dependencies?
