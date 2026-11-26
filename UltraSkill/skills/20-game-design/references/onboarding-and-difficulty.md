# Invisible Onboarding (Safe Teach -> Gated Test -> Twist) & Difficulty Tuning

## 1. The Kishotenketsu 4-Beat Mechanic Tutorial

Never teach a core mechanic (Dash, Parry, Grapple, Pressure Vent) by pausing the game on frame 1 and displaying a 3-paragraph tutorial modal. Teach every mechanic through a 4-beat spatial level sequence:

1. **Beat 1 — Safe Teach (Zero Penalty)**:
   - Place the player in a calm room where the only way forward requires performing the new action once (e.g., a `2.5 m` floor gap with a shallow `0.5 m` pit underneath that deals `0` damage and has steps right back up, paired with a single clean diegetic prompt `[Space] Dash`).
2. **Beat 2 — Gated Verification Test**:
   - Immediately follow with a clear test under mild timing pressure (e.g., dashing past a slow rhythmic steam vent firing every `2.5 seconds`). The player cannot leave the room without demonstrating they understood Beat 1.
3. **Beat 3 — Escalation / Combination**:
   - Combine the new mechanic with a previously learned mechanic (e.g., dash through the steam vent and strike the exposed valve switch before the gate closes).
4. **Beat 4 — Mastery Twist / Reward**:
   - Present a high-intensity combat encounter or optional secret chest that rewards mastering the mechanic's timing window (e.g., dashing through an enemy's shockwave ring to stun them).

## 2. Fair Difficulty Curves & Assist Options

1. **Sawtooth Intensity Pacing**:
   - Alternate `3–5 minutes` of escalating combat/platforming tension with a `60–90 second` safe quiet beat (loot room, scenic vista, story clue, workbench upgrade) so player focus and hands can reset before the next spike.
2. **Modular Assist Sliders Over Blunt "Easy/Hard" HP Multipliers**:
   - Simply multiplying enemy HP by `3.0x` on Hard mode turns fun combat into a tedious sponge-fest.
   - Instead, scale difficulty via **Enemy Attack Token Concurrency** (`1` attacker on Story mode vs `2` on Veteran), **Telegraph Window Padding** (`+150 ms` parry/dodge grace on Assist mode), and explicit Accessibility toggles (`Damage Taken Multiplier 50%..100%`, `Stamina Cost Toggle`; see `25-ui-audio`).
