# Combat Hitboxes and Game Feel

Crisp action combat relies on three pillars: **distinct 3-phase attack frames**, **decoupled Hitbox/Hurtbox volumes**, and **multi-sensory impact feedback (hit-stop, knockback, VFX, SFX)**.

---

## 1. Three-Phase Attack Frame Windows (60 Hz Baseline)

Every melee or enemy attack is divided into three non-overlapping phases:

| Phase | Typical Frames (60 Hz) | Hitbox Active? | Vulnerability & Cancel Rules |
|---|---|---|---|
| **1. Startup (Windup / Telegraph)** |Light: `6–9f` (`100–150 ms`)<br>Heavy: `16–24f` (`266–400 ms`) | `false` | Can be interrupted by taking stagger damage; silhouette clearly telegraphs strike arc |
| **2. Active (Strike Window)** | `3–6f` (`50–100 ms`) | `true` | Weapon trail renders; Hitbox queries overlapping Hurtboxes; cannot cancel |
| **3. Recovery (Follow-Through)** | Light: `10–14f`<br>Heavy: `20–30f` | `false` | Late recovery (`last 40%`) opens **Cancel Window** into next combo swing or Dodge |

---

## 2. Hitbox vs Hurtbox Separation

Never use a character's physics movement capsule (`CharacterBody3D` collision shape) as their combat hurtbox or attack hitbox.

1. **Movement Capsule**: Collides only with world geometry and pushes against other characters.
2. **Hurtbox (`Area3D`)**: Attached to torso/limbs; slightly more generous for the player when attacking enemies (`+15%` radius on enemy hurtboxes) and slightly tighter on the player (`-10%` radius on player hurtbox) so near-misses feel heroic.
3. **Hitbox (`Area3D`)**: Attached to the weapon socket or attack arc; enabled **only** during Active frames.
4. **Deduplication Set**:
   - Store `var _hit_registry: Dictionary = {}` on the `Hitbox`.
   - When `enable_hitbox()` is called at the start of Active frames, call `_hit_registry.clear()`.
   - When `area_entered(hurtbox)` fires, check `if _hit_registry.has(hurtbox.owner_id): return`, then record `_hit_registry[hurtbox.owner_id] = true`.

---

## 3. Hit-Stop (Frame Freeze) & Impact Juice

When a melee strike lands, briefly freezing the attacker and defender gives the brain time to register weight and force:

1. **Localized Hit-Stop (Preferred over Global `Engine.time_scale`)**:
   - Set `animation_player.speed_scale = 0.0` and pause velocity integration on the **attacker and struck victim(s) only** for:
     - Light hit: `45 ms` (`~3 frames`)
     - Heavy / Critical hit: `85 ms` (`~5 frames`)
     - Lethal finishing blow: `120 ms` (`~7 frames`)
2. **Victim Hit-Shake**:
   - During hit-stop, oscillate the victim's visual mesh root horizontally by `±0.06 m` at `60 Hz` while their physics capsule stays stationary.
3. **Hit Flash**:
   - Override the victim's material emission/overlay parameter to pure white for `33 ms` (`2 frames`), followed by red for `50 ms` (`3 frames`).
4. **Knockback Impulse**:
   - Apply knockback velocity **when hit-stop ends**, not before, so the freeze frame shows the blade inside the impact contact point.
