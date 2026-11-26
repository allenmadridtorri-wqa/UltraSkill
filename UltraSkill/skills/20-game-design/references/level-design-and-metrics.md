# Spatial Level Design, Sightlines & Movement Metrics

## 1. Lock Metrics Before Greyboxing (`LEVEL_METRICS.md`)

If a level designer builds cover blocks at `1.05 m`, `1.25 m`, and `1.45 m` randomly, the player can never tell at a glance which wall stops bullets when crouching (`1.10 m` eye height) and which ledge can be vaulted (`1.20 m` max vault).

### Standardized Spatial Metric Grid (Starting Values)
Snap all greybox level geometry to a **`0.50 m` horizontal grid** and **`0.25 m` vertical grid**:

| Architectural Element | Exact Metric Dimension | Gameplay Function |
|---|---|---|
| **Player Collision Capsule** | `0.80 m` width (`0.40 m` radius) x `1.80 m` standing / `1.10 m` crouched | Baseline unit ($1\text{W} = 0.80\text{ m}$). |
| **Standard Doorway Opening** | `1.50 m` wide x `2.25 m` tall (`2.0 m` wide for AI co-op / boss doors) | Prevents shoulder snagging at sprint speed (`7.2 m/s`) and keeps third-person camera from clipping the lintel. |
| **Narrow Maintenance / Stealth Hall** | `2.00 m` wide x `2.75 m` tall | 1 entity wide; forces commitment. |
| **Two-Way Combat Corridor** | `4.00 m` wide x `3.50 m` tall | Allows dodging past a charging melee enemy with a `1.2 m` lateral dash. |
| **Low Vaultable / Crouch Cover** | `1.25 m` tall x `0.50 m` thick | Blocks enemy line-of-sight while crouched; allows standing aim-over and 1-button vault. |
| **High Full-Body Cover Wall** | `2.50 m` tall x `0.50 m` thick | Complete line-of-sight and splash blocker; cannot be jumped over without a boost platform. |
| **Standard / Max Jump Gap** | `3.00 m` comfortable walk jump / `4.25 m` max sprint+coyote jump | Never place a lethal pit wider than `3.75 m` (`88%` of theoretical max jump) so a `50 ms` late press does not kill the player! |

## 2. Combat Arena Topology: The 3-Lane + Flank Loop

Never design a combat encounter in a dead-end rectangular closet where the player backs into a corner and funnels all enemies through one doorway:
1. **Figure-8 / Circular Outer Loop**: Every combat arena (`16 m x 20 m` to `28 m x 32 m`, starting value) must have a continuous circular outer traversal loop so a kiting player can never get corner-trapped.
2. **Elevation Valence (`+2.50 m` High Ground)**: Include at least one elevated catwalk or ledge accessible via two separate ramps/jump pads so ranged enemy archetypes have a vantage point and the player has a tactical flanking route.
3. **Landmark Weenies & Lighting Breadcrumbs**: Light the exit doorway or primary objective with a distinct warm/cool contrast (`+1.5 EV` brighter than ambient walls) visible from the arena entrance so the player never gets lost after a 360-degree camera spin in combat.
