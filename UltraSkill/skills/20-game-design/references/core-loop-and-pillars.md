# The 30-Second Core Loop & Design Pillars as Razor Filters

## 1. Design Pillars Must Be Falsifiable Razor Filters

Bad design pillars are generic adjectives that nobody would disagree with ("Fun", "Immersive", "High Quality", "Smooth Controls"). A veteran creative director writes **3 Falsifiable Razor Pillars** that tell the team what to **reject**:

| Bad Generic Pillar | Veteran Falsifiable Razor Pillar | What This Pillar Forces Us to Cut |
|---|---|---|
| "Exciting Combat" | **"Every Strike Is a Commitment (No Animation Canceling After Active Frame 1)"** | Cuts button-mashing spam; forces clear enemy telegraph windows (`>= 450 ms`) and stamina management. |
| "Atmospheric World" | **"Zero HUD Clutter During Exploration (Diegetic Instruments Only)"** | Cuts floating minimaps and compass arrows; forces clear architectural sightlines and lit landmark weenies. |
| "Accessible Everywhere" | **"Instant 30+ FPS Playability on a 4 GB Intel UHD Laptop"** | Cuts dynamic ray-traced shadows and 4K texture streaming; mandates baked Cycles lightmaps and pooled projectiles. |

## 2. Three Nested Time Horizon Loops

Every engaging game nests three feedback loops that lock together like clockwork gears:

```text
[Second-to-Second Micro Loop (0.5s - 3.0s)]
  Read Telegraph -> Position / Dash / Aim -> Strike -> Hitstop + SFX/VFX Juice
        │
        ▼
[Minute-to-Minute Tactics Loop (30s - 90s)]
  Enter Arena / Puzzle Room -> Prioritize Threats -> Clear Wave / Unlock Shortcut -> Collect Drop
        │
        ▼
[Session Meta Loop (15m - 30m)]
  Return to Safe Hub -> Spend Resources at Sink -> Unlock New Mechanic Twist -> Open Next Zone
```

## 3. The Greybox 30-Second Toy Test (Round 1 Gate)

Before modeling a single textured character (`11-modeling`) or building a multi-room level:
1. Build a single `20 m x 20 m` untextured greybox room containing the player capsule, 3 obstacle blocks, and 2 primitive enemy capsules.
2. Play inside that room for 60 seconds.
3. If moving, jumping, dashing, and striking the primitive capsule does not feel satisfying through **acceleration curves, coyote time, `60 ms` hitstop, knockback impulse, and crisp sound transients**, stop all content production and tune the Second-to-Second loop in `22-gameplay-systems` until it does.
