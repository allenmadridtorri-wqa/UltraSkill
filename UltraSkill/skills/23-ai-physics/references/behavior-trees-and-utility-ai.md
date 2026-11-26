# Behavior Trees and Utility AI

Great game AI is **not** an unbeatable aimbot; great game AI is **legible**. The player must immediately understand what an enemy knows, what it intends to do next, and why it chose that action.

---

## 1. Behavior Tree (BT) Node Primitives

Every node in a Behavior Tree ticks and returns one of three statuses: **`SUCCESS`**, **`FAILURE`**, or **`RUNNING`**.

| Node Type | Execution Rule | Typical Usage |
|---|---|---|
| **Sequence (`->`)** | Ticks children left-to-right; stops and returns `FAILURE` on first child failure, or `RUNNING` on running child | `[HasLineOfSight] -> [AcquireAttackToken] -> [AimTelegraph] -> [FireShot]` |
| **Selector / Fallback (`?`)** | Ticks children left-to-right; stops and returns `SUCCESS` on first child success | `[SelfPreservationBranch] ? [CombatEngageBranch] ? [InvestigateBranch] ? [PatrolBranch]` |
| **Decorator** | Wraps 1 child (`Inverter`, `Cooldown`, `TimeLimit`, `BlackboardGuard`) | `Cooldown(3.5s) -> [ThrowGrenade]` |
| **Action / Leaf** | Reads/writes Blackboard and drives the character controller / state machine | `MoveToCoverLeaf`, `MeleeStrikeLeaf` |

---

## 2. Blackboard Architecture (Individual + Squad)

Never store transient AI memory inside individual BT nodes (allowing a single immutable BT definition to be shared across 50 enemy instances). Store state in a two-tier **Blackboard**:

1. **Agent Blackboard (Per Enemy)**:
   - `self_hp_ratio: float`
   - `target_pos_known: Vector3`
   - `time_since_saw_player: float`
   - `alert_level: int` (`0 = Unaware`, `1 = Suspicious`, `2 = Combat`)
   - `has_attack_token: bool`
2. **Squad Blackboard (Shared by Encounter Group)**:
   - `player_last_known_pos: Vector3`
   - `available_melee_tokens: int` (Default `2`)
   - `available_ranged_burst_tokens: int` (Default `2`)
   - `last_grenade_timestamp: float` (Global squad cooldown `>= 8.0 s`)

---

## 3. Squad Attack Token Protocol (Anti-Dogpiling)

Without squad coordination, 8 melee enemies rush the player simultaneously and overlap their attacks into an unreadable death ball.

1. **Inner Ring vs Outer Ring**:
   - Only agents holding a **Melee Attack Token** (`max = 2`) may enter the **Inner Strike Ring (`1.5–2.5 m`)** and initiate a melee combo.
   - All other melee enemies stay in the **Outer Flank Ring (`4.5–6.5 m`)**, strafing laterally and playing taunt/ready animations.
2. **Token Release Guarantee**:
   - A token is held for at most `2.5 seconds` or until the attack recovery finishes.
   - If an enemy holding a token is staggered or killed, its state machine `exit()` hook **must** immediately return the token to the Squad Blackboard.

---

## 4. Perception Slicing & Honest Sensory Barks

- **Time-Sliced Vision Raycasts**:
  - Evaluate vision cone (`dot(forward, dir_to_player) > cos(55°)` and `dist < 18.0 m`) before casting a single physics occlusion ray.
  - Stagger vision updates at `10 Hz`: Agent `i` runs its perception check when `(physics_frame + i) % 6 == 0`.
- **Legibility Barks / Telegraphs**:
  - When transitioning `Unaware -> Suspicious`, pause for `0.4 s` with an audio cue (`"Huh?"`) and a visual indicator.
  - When transitioning to `GranadeThrow` or `FlankMove`, play an explicit callout (`"Flanking left!"`) so the player feels outsmarted rather than blindsided.
