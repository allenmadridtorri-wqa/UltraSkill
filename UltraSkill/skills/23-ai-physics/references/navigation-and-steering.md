# Navigation and Steering

Pathfinding occurs at two distinct scales: **Global Macro Pathfinding (NavMesh A\*)** at `4 Hz`, and **Local Micro Steering (Context Steering / Separation)** at `60 Hz`.

---

## 1. NavMesh Baking Parameters

| Parameter | Standard Humanoid Value | Reason |
|---|---|---|
| `cell_size` / `cell_height` | `0.15 m` / `0.10 m` | Balances voxel accuracy against memory footprint |
| `agent_radius` | `0.45 m` (`capsule_radius 0.40 m + 0.05 m`) | Prevents shoulder clipping on doorway frames |
| `agent_height` | `1.85 m` | Ensures low pipes/beams are marked non-walkable |
| `agent_max_climb` | `0.30 m` | Matches maximum stair step height |
| `agent_max_slope` | `45.0°` | Matches `CharacterBody3D.floor_max_angle` |

---

## 2. Throttled Path Queries

Never recalculate a full A* path (`target_position = player.global_position`) every single physics frame across 20 enemies.

### Repath Trigger Conditions
Recalculate the path for an agent **only** when BOTH are true:
1. At least **`0.25 seconds` (`4 Hz`)** have elapsed since this agent's last path query (staggered by `agent_id`).
2. The target has moved more than **`1.5 meters`** from the previous path's goal position (or `0.5 meters` when within `4.0 meters` of the target).

---

## 3. Context Steering (8-Ray Local Avoidance)

Raw NavMesh waypoints cause agents to walk in single-file lines and collide head-on in corridors. Instead of heavy RVO solvers, evaluate an **8-direction Context Map** on the XZ plane:

1. **Interest Map (`I[0..7]`)**:
   - For each of 8 compass directions $\vec{d}_k$, set $I_k = \max(0, \vec{d}_k \cdot \vec{v}_{\text{nav\_waypoint}})$.
   - For flanking/strafing agents (no attack token), bias $I_k$ toward perpendicular tangent vectors at `5.5 m` radius.
2. **Danger Map (`D[0..7]`)**:
   - Check neighbor agents within `1.8 m` radius from a spatial hash grid (no physics raycasts needed for agent-agent separation) and mark directions pointing toward close neighbors in $D_k$.
3. **Final Steering Direction**:
   - Subtract danger from interest: $W_k = \max(0, I_k - D_k)$ and blend the winning direction vector with exponential smoothing (`decay = 12.0`).

---

## 4. Anti-Stuck Recovery

Track the distance an agent has moved over a rolling `1.0 second` window while in a `Moving` state:
- If `distance_moved < 0.25 m` while `desired_speed > 2.0 m/s`:
  1. Force an immediate NavMesh path recalculation.
  2. Apply a `0.4 s` lateral sidestep impulse perpendicular to the blocked normal.
