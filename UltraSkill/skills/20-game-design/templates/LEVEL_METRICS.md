# Standardized Character Movement & Spatial Level Metrics

All environment meshes (`11-modeling`), character controllers (`22-gameplay-systems`), and NavMesh agents (`23-ai-physics`) must build strictly to these metric dimensions (`1.0 unit = 1.0 meter`).

## 1. Character Collision & Locomotion Envelope (`60 Hz` Fixed Step)

| Metric Name | Value (Starting Values) | Derived / Engineering Notes |
|---|---|---|
| **Player Capsule Diameter / Radius** | `0.80 m` / `0.40 m` | NavMesh `agent_radius = 0.45 m` (`+0.05 m` wall clearance). |
| **Player Standing / Crouched Height** | `1.80 m` / `1.10 m` | Eye camera height: `1.62 m` standing, `0.95 m` crouched. |
| **Max Walk / Sprint Speed** | `4.50 m/s` / `7.20 m/s` | Ground acceleration `38.0 m/s^2` (`~0.12 s` to top walk speed); friction deceleration `45.0 m/s^2`. |
| **Dash Speed / Duration / Cooldown** | `16.0 m/s` for `0.167 s` (`10 f` = `2.67 m` dash distance) | Invulnerability frames (`i-frames`): frames `1..8` (`133 ms`); cooldown `0.75 s` (`45 f`). |
| **Jump Apex Height / Time to Apex** | `1.35 m` / `0.38 s` (`23 frames`) | Upward gravity $g_{\text{up}} = \frac{2 h}{t^2} = 18.7\text{ m/s}^2$, initial $v_0 = 7.1\text{ m/s}$, downward gravity $g_{\text{down}} = 26.0\text{ m/s}^2$. |
| **Coyote Time / Jump Buffer Window** | `100 ms` (`6 frames`) / `133 ms` (`8 frames`) | Allows jumping up to 6 frames after leaving a ledge and queuing a jump 8 frames before touchdown. |
| **Max Step-Up Height / Max Walkable Slope** | `0.30 m` / `45.0 deg` | Stairs must use `<= 0.20 m` riser and `>= 0.30 m` tread depth (or a smooth `32 deg` invisible collision ramp!). |

## 2. Environment Architecture Grid (`0.50 m` Horizontal / `0.25 m` Vertical Snap)

| Structure | Width (`X` m) | Depth (`Y` m) | Height (`Z` m) | Rule |
|---|---:|---:|---:|---|
| **Standard Doorway** | `1.50 m` | `0.25 m` | `2.25 m` | Minimum clear portal for player and Swarmer AI. |
| **Combat / Boss Doorway** | `2.50 m` | `0.50 m` | `3.00 m` | Required for Shield Elite AI and co-op sightlines. |
| **Single Utility Corridor** | `2.00 m` | Modular `4.00 m` | `2.75 m` | Traversal only; no multi-enemy combat spawns inside `2.0 m` halls. |
| **Combat Corridor** | `4.00 m` | Modular `4.00 m` | `3.50 m` | Minimum width for dashing past a melee attacker. |
| **Low Crouch / Vault Cover** | `2.00 m` | `0.50 m` | `1.25 m` | Protects crouched player (`1.10 m`); clear line-of-fire when standing (`1.62 m` eye height). |
| **High Full Cover Pillar** | `1.50 m` | `1.50 m` | `2.50 m` | Minimum `3.00 m` clear floor gap between adjacent cover pillars. |
| **Elevated Catwalk / Ledge** | `2.50 m` | Modular `4.00 m` | `+2.50 m` (`2` flights of `1.25 m`) | Accessible via `1.00 m` jump-up blocks or `30 deg` ramp (`4.33 m` horizontal run). |
