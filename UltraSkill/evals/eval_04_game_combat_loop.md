# Eval 04 — Responsive 60 FPS Game Combat Loop & Cloud Windows Build

## 1. Benchmark Prompt

> "Implement a 3D action game character controller, hierarchical state machine, and arena wave director in Godot 4 with coyote time, jump buffering, hit-stop, squad attack tokens, and a GitHub Actions workflow that builds the Windows `.exe` in the cloud."

---

## 2. Skills Routed

1. [`skills/21-engine-architecture/SKILL.md`](../skills/21-engine-architecture/SKILL.md) (Fixed `60 Hz` physics step, object pooling, atomic SHA-256 save migrations)
2. [`skills/22-gameplay-systems/SKILL.md`](../skills/22-gameplay-systems/SKILL.md) (`100 ms` coyote time, `120 ms` jump buffer, HSM with guaranteed `exit()`, hit-stop)
3. [`skills/23-ai-physics/SKILL.md`](../skills/23-ai-physics/SKILL.md) (Squad Attack Tokens `max = 2`, 12-layer collision matrix)
4. [`skills/27-production-qa-release/SKILL.md`](../skills/27-production-qa-release/SKILL.md) (GitHub Actions headless Windows + Web release workflow)

---

## 3. Pass / Fail Grading Rubric (100 Points Total — Pass Threshold `>= 90`)

| Check ID | Criterion | Points | Verification Command / Method |
|---|---|---|---|
| `E04-1` | **Kinematic Jump & Forgiveness Windows**: Controller derives gravity/velocity from `(jump_height, time_to_apex)`, enforces `100 ms` coyote time + `120 ms` jump buffer, and disables floor snap on jump frame | `25` | Inspect `skills/22-gameplay-systems/templates/character_controller.gd` |
| `E04-2` | **Squad Attack Token Coordination**: AI coordinator limits concurrent melee attackers to `2` and guarantees token release on stagger/death | `25` | `python3 skills/23-ai-physics/templates/behavior_tree_core.py --self-test` |
| `E04-3` | **12-Layer Collision Separation**: Passive `Hurtbox` layers have `collision_mask = 0` and never friendly-fire their own actor | `25` | `python3 skills/23-ai-physics/scripts/collision_matrix_gen.py --self-test` |
| `E04-4` | **Cloud Windows Release Validation**: GitHub Actions workflow exports Windows `.exe` + `.pck` in the cloud and release zip passes `package_release_check.py` | `25` | `python3 skills/27-production-qa-release/scripts/package_release_check.py --self-test` |
