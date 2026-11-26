# Combat Frame Data, Time-to-Kill (TTK) & Enemy Role Synergies

## 1. The Three-Phase Attack Frame Contract (`60 Hz` Physics Tick)

Every melee swing, projectile cast, or boss slam consists of three strictly separated frame intervals at `60 Hz` (`1 frame = 16.67 ms`):

```text
|<--- Startup (Windup) --->|<-- Active -->|<--- Recovery (Whiff Punish) --->|
  Player: 5-14 frames        2-6 frames     10-22 frames
  Enemy:  24-42 frames       3-6 frames     24-45 frames
```

1. **Startup (Telegraph Windup)**:
   - **Player attacks (`5–14 frames`, `83–233 ms`)**: Fast enough to feel snappy, long enough that the animation pose reads before the hitbox spawns.
   - **Enemy attacks (`24–42 frames`, `400–700 ms`)**: Human visual reaction + thumb press takes `~250 ms`. Never give an enemy a damaging attack with `< 18 frames` (`300 ms`) startup—players cannot react to it and perceive it as unfair RNG.
2. **Active (Hitbox Live)**:
   - Enable the damaging `Area3D`/`Area2D` hitbox **only** during the `2–6` active strike frames (`33–100 ms`). Leaving an enemy's weapon hitbox active during startup or recovery causes players to take damage by bumping into a resting sword!
3. **Recovery (Commitment & Punish Window)**:
   - After an enemy misses a heavy slam, hold them in a `30–48 frame` (`500–800 ms`) recovery posture so a player who dodged the attack has a clean window to counter-strike.

## 2. The 4-Archetype Enemy Chessboard

Never populate an arena with 8 identical melee grunts. Combine up to 3 distinct functional roles per wave:

| Archetype Role | Movement & Range | Tactical Purpose | TTK Target (`Seconds of Sustained Player DPS`, Starting Value) |
|---|---|---|---|
| **1. Swarmer / Rusher (Pawn)** | Fast (`5.5 m/s`), melee (`1.5 m`) | Forces the player to move from stationary cover and use AoE/cleave attacks. | `1.2 – 2.2 s` (`2–3` light hits) |
| **2. Ranged Suppressor (Bishop)** | Stationary / kiting (`10–18 m`), slow projectile (`12 m/s`) | Fires telegraphed projectiles that deny lanes and force lateral dashing. | `2.0 – 3.5 s` (`3–4` hits) |
| **3. Shield / Area Denier (Rook)** | Slow (`2.5 m/s`), frontal block or AoE hazard zone | Cannot be spammed from the front; requires flanking behind or heavy guard-break. | `6.0 – 10.0 s` |
| **4. Commander / Disabler (Queen)** | Mid-range (`6–10 m`), buffs pawns or casts delayed tether | High-priority target that changes the arena puzzle until eliminated first. | `8.0 – 14.0 s` |
