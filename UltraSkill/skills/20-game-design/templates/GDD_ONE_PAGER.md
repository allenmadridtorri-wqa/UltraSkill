# Game Design Document (One-Page Contract)

- **Project Slug**: `<PROJECT_SLUG>`
- **Genre & Camera Perspective**: `Top-Down / Third-Person / First-Person Tactical Action`
- **Target Engine & Renderer**: `Godot 4.x (gl_compatibility renderer) or Three.js WebGL (LOW Preset Baseline)`
- **Target Hardware Baseline**: `4 GB RAM laptop, 1 GB Intel UHD Graphics (>= 30 FPS LOW / 60 FPS MEDIUM)`

## 1. Three Falsifiable Razor Pillars

1. **Commitment Over Spam**: Every attack and dash has fixed startup and recovery frames; reading enemy telegraphs (`>= 400 ms`) beats button mashing.
2. **Readable Spatial Tactics**: Arena geometry uses strict `LEVEL_METRICS.md` heights (`1.25 m` low cover, `2.50 m` full cover) and ticketed AI (`max 2` simultaneous melee attackers).
3. **Budget-Hardware First**: Zero dynamic shadow maps on `LOW`; all projectiles and VFX use pre-allocated fixed pools (`<= 100` draw calls).

## 2. Three Nested Core Loops

| Horizon | Duration | Player Action -> System Response -> Reward |
|---|---|---|
| **Micro Loop** | `0.5 – 3.0 s` | Read enemy windup -> Dash (`120 ms` i-frames) or Strike -> `60 ms` hitstop + knockback + energy shard drop. |
| **Tactical Loop** | `45 – 90 s` | Enter locked arena -> Eliminate Ranged Suppressor first, then clear Swarmers -> Unlock chamber exit & collect core upgrade. |
| **Session Loop** | `15 – 25 min` | Clear 3 sector chambers -> Spend shards at workbench sink -> Defeat sector boss -> Save checkpoint. |

## 3. Complete Input Map (Keyboard/Mouse + Gamepad)

| Action ID | Keyboard / Mouse | Gamepad (South/West Layout) | Buffer Window (`60 Hz`) |
|---|---|---|---|
| `move_axes` | `W / A / S / D` or `Arrow Keys` | `Left Stick` (`0.18` radial deadzone) | Continuous |
| `aim_vector` | `Mouse Cursor / Delta` | `Right Stick` | Continuous |
| `action_primary` | `Left Click` or `J` | `West Button (X / Square)` | `8 frames` (`133 ms`) |
| `action_dash` | `Space` or `Right Click` | `South Button (A / Cross)` | `8 frames` (`133 ms`, `100 ms` coyote) |
| `action_interact` | `E` or `Enter` | `North Button (Y / Triangle)` | `6 frames` (`100 ms`) |
| `ui_pause` | `Escape` or `P` | `Start / Options` | Immediate |

## 4. Scope Ceiling for Version 1.0

- **Total Playable Arenas**: `3` combat chambers + `1` safe workbench hub.
- **Player Abilities**: `1` primary 3-hit combo, `1` i-frame dash, `1` heavy charged pulse.
- **Enemy Archetypes**: `1` Melee Swarmer, `1` Ranged Suppressor, `1` Shield Elite.
