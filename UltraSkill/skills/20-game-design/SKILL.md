---
name: 20-game-design
description: >-
  A-to-AAA game design skill covering 30-second core loops, design pillars,
  tabular living GDDs, spatial level metrics, economy faucets/sinks, combat
  time-to-kill (TTK), narrative barks, onboarding, and Monte Carlo balance simulation.
---

# 20-Game-Design: Core Loops, Spatial Metrics & Monte Carlo Balance

A veteran game director never writes a 120-page novel of lore before proving a responsive 30-second greybox core loop, locking physical spatial metrics in meters, and verifying combat/economy math with a deterministic Monte Carlo simulation.

## When to use

Load this skill whenever designing a new game or playable mode, authoring a Game Design Document (GDD), defining level geometry metrics, tuning combat framing and Time-to-Kill (TTK), designing progression/economy tables, or writing in-game narrative and tutorials.

## Inputs

- Approved `BRIEF.md` and `BARS.md` from `00-director`.
- Target platform and hardware floor (default: 4 GB RAM / 1 GB Intel UHD laptop running Godot 4 Compatibility or Three.js on `LOW`).

## Steps

1. **Lock Design Pillars & the 30-Second Core Loop**:
   - Fill out [`templates/GDD_ONE_PAGER.md`](templates/GDD_ONE_PAGER.md) using [`references/core-loop-and-pillars.md`](references/core-loop-and-pillars.md) and [`references/game-design-document.md`](references/game-design-document.md).
   - Define 3 non-negotiable Design Pillars as razor filters (any feature that does not serve at least one pillar is cut) and specify the Second-to-Second (`0.5–3 s`), Minute-to-Minute (`30–90 s`), and Session-to-Session (`15–30 min`) loops.
2. **Freeze Spatial Level & Movement Metrics Before Modeling**:
   - Fill out [`templates/LEVEL_METRICS.md`](templates/LEVEL_METRICS.md) using [`references/level-design-and-metrics.md`](references/level-design-and-metrics.md).
   - Every doorway, jump gap, cover wall, and corridor width must map to exact integer multiples of the character's capsule radius, walk speed, and jump envelope.
3. **Design Combat Framing & Economy Sinks/Faucets in Tables**:
   - Follow [`references/combat-and-encounter-balance.md`](references/combat-and-encounter-balance.md) and [`references/economy-and-progression.md`](references/economy-and-progression.md): specify attack startup/active/recovery frames at `60 Hz`, enemy role synergies, and closed-loop resource sinks.
4. **Verify Balance Numerically with the Monte Carlo Simulator**:
   - Run `python3 skills/20-game-design/scripts/balance_simulator.py` across `1,000+` simulated combat encounters and progression levels to prove player win rates, TTK windows, and gold/XP inflation stay inside design tolerances before writing engine code.
5. **Integrate Environmental Narrative & Invisible Onboarding**:
   - Follow [`references/narrative-and-worldbuilding.md`](references/narrative-and-worldbuilding.md) and [`references/onboarding-and-difficulty.md`](references/onboarding-and-difficulty.md): teach every mechanic through the **Safe Teach -> Gated Test -> Mastery Twist** sequence rather than pop-up text walls.

## Numbers and defaults

All values below are **starting values** at a `60 Hz` (`16.67 ms/tick`) gameplay update rate:

| Design Metric | Starting Value | Verification Method |
|---|---|---|
| **Player Capsule Dimensions** | `0.80 m` diameter (`0.40 m` radius) x `1.80 m` height | `LEVEL_METRICS.md` |
| **Walk / Sprint Speed** | `4.5 m/s` walk / `7.2 m/s` sprint (`1.6x` ratio) | `LEVEL_METRICS.md` |
| **Jump Envelope** | `1.35 m` max vertical height (`1.20 m` comfortable ledge), `4.0 m` running horizontal gap | `LEVEL_METRICS.md` |
| **Corridor Width (Single / Combat)** | `2.0 m` single utility hall / `4.0 m` two-way combat hall (`5x` player diameter) | `LEVEL_METRICS.md` |
| **Light Melee Attack Frame Data (`60 Hz`)** | `6 f` (`100 ms`) startup, `4 f` (`67 ms`) active hitbox, `12 f` (`200 ms`) recovery | `combat-and-encounter-balance.md` |
| **Heavy / Enemy Telegraph Attack (`60 Hz`)** | `24 – 36 f` (`400 – 600 ms`) readable telegraph windup (`>= 250 ms` human visual reaction floor) | `combat-and-encounter-balance.md` |
| **Standard Fodder / Elite / Boss TTK** | Fodder `1.5 – 3.0 s` (`2–4` hits), Elite `8 – 15 s`, Boss phase `45 – 75 s` | `balance_simulator.py` |

## Failure modes and fixes

- **Enemy attacks hit the player with `< 12 frames` (`200 ms`) startup telegraph**: Human visual reaction + motor input takes `220 – 280 ms`. Attacks faster than `18 frames` (`300 ms`) feel like unavoidable cheap damage. Give enemy attacks a clear `24–36 frame` silhouette windup and distinct audio cue.
- **Runaway late-game currency inflation**: Faucets scale exponentially while repair/upgrade sinks scale linearly. Ensure every currency faucet has a progressive sink tested via `balance_simulator.py`.
- **Claustrophobic third-person combat rooms**: Corridors narrower than `3.5 m` cause third-person spring-arm cameras (`22-gameplay-systems`) to collide constantly with walls. Widen combat arenas to `>= 12 m x 12 m` with `3.0 m` spacing between cover pillars.

## Done check

- `GDD_ONE_PAGER.md` and `LEVEL_METRICS.md` are completed with concrete numbers.
- `balance_simulator.py` exits with code `0` confirming TTK and win-rate targets over `1,000` trials.

## Related files

- [`references/core-loop-and-pillars.md`](references/core-loop-and-pillars.md)
- [`references/game-design-document.md`](references/game-design-document.md)
- [`references/level-design-and-metrics.md`](references/level-design-and-metrics.md)
- [`references/economy-and-progression.md`](references/economy-and-progression.md)
- [`references/combat-and-encounter-balance.md`](references/combat-and-encounter-balance.md)
- [`references/narrative-and-worldbuilding.md`](references/narrative-and-worldbuilding.md)
- [`references/onboarding-and-difficulty.md`](references/onboarding-and-difficulty.md)
- [`templates/GDD_ONE_PAGER.md`](templates/GDD_ONE_PAGER.md)
- [`templates/LEVEL_METRICS.md`](templates/LEVEL_METRICS.md)
- [`scripts/balance_simulator.py`](scripts/balance_simulator.py)
