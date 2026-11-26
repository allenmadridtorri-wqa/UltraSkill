# Game Narrative, Barks & Ludonarrative Alignment

## 1. Never Interrupt Active Gameplay With Unskippable Text Boxes

When a player enters a new room with full stamina and adrenaline, freezing their controls for a 45-second text dialogue exchange kills momentum. Separate narrative delivery into three non-intrusive tiers based on gameplay intensity:

| Gameplay Intensity State | Permitted Narrative Delivery Channel | Length & Cooldown Rules (Starting Values) |
|---|---|---|
| **1. High Combat / Platforming** | **Combat Barks** (`1–5 words` spoken + bottom-third subtitle tag: `"[ENEMY]: Flanking left!"`) | Max `1.8 s` duration; minimum `6.0 s` global bark cooldown so enemies do not talk over each other; never locks player controls. |
| **2. Traversal / Safe Corridor Walk** | **Walk-and-Talk Radio / Companion Banter** + **Environmental Storytelling** | `2–4` short lines (`<= 15 words` each) played while the player retains 100% movement and camera control. If combat starts mid-line, interrupt smoothly (`"Wait—contacts ahead!"`) and resume after combat clears. |
| **3. Safe Hub / Camp / Inspectable Clue** | **Interactive Branching Dialogue / Forensic Inspection** (`18-interactive-story`) | Triggered voluntarily by the player pressing `[Interact]`; `<= 45 words` per node; instant skip/advance button always active. |

## 2. Writing Authentic AI Barks (Communicate State, Not Fluff)

Enemy and companion barks exist primarily to **telegraph hidden AI state transitions (`23-ai-physics`) to the player**:
- **Bad Bark**: `"You will pay for your crimes, intruder!"` (Tells the player zero tactical information).
- **Veteran State-Telegraph Bark**:
  - On acquiring attack token (`State -> Attacking`): `"Pushing in—cover me!"`
  - On losing line-of-sight (`State -> Searching`): `"Lost visual—checking the catwalk!"`
  - On grenade throw (`State -> AreaDenial`): `"Flushing them out!"`
  - On last enemy remaining (`Morale -> Panicked`): `"Squad's down—I need backup!"`
