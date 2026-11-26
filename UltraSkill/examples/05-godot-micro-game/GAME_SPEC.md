# Example 05 — Godot 4 Micro-Arena Action Game (`GAME_SPEC.md`)

This golden-master worked example demonstrates how UltraSkill links **Game Design (`20`) -> Engine Architecture (`21`) -> Gameplay Systems (`22`) -> AI & Physics (`23`) -> Optimization (`26`) -> Cloud Windows Release (`27`)** into a complete, deterministic 3D combat micro-arena (*"Iron Bastion"*).

---

## 1. Core Loop & Combat Metrics

- **30-Second Core Loop**:
  1. Read incoming enemy melee/ranged telegraph (`150–350 ms` startup window).
  2. Dodge-roll (`140 ms` buffered, `220 ms` i-frames) or land a 3-hit melee combo (`Hit-Stop = 45 ms` light / `85 ms` finisher).
  3. Collect dropped energy cells to charge the Bastion Beacon before the 3-wave timer expires.

| Metric | Value | Verified By |
|---|---|---|
| **Player Capsule / Top Speed** | `radius = 0.40 m`, `height = 1.80 m`, `max_speed = 7.0 m/s` | `skills/22-gameplay-systems/templates/character_controller.gd` |
| **Coyote Time / Jump Buffer** | `100 ms` / `120 ms` | Zero missed platform ledge jumps |
| **Squad Melee Attack Tokens** | `2` concurrent tokens across up to `12` active enemies | Prevents unreadable enemy dogpiling |
| **Object Pooling (`NodePool`)** | `24` enemy projectiles + `16` hit-spark emitters pre-allocated | **`0 KB`** per-frame heap allocation during combat |
| **`LOW` Preset Budget (720p)** | `p95 = 12.8 ms` (`60 FPS`), `94` draw calls, `310 MB` VRAM | Fits 4 GB RAM laptop with 1 GB Intel UHD graphics |

---

## 2. Cloud Windows Build Workflow

To export `IronBastion-v1.0.0-win64.zip` without installing heavy Windows export templates on the 4 GB RAM laptop:
- Copy `skills/27-production-qa-release/templates/github_godot_release.yml` to `.github/workflows/release.yml` and push tag `v1.0.0`.
