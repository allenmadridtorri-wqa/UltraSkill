# Milestones and Scoping

Games fail to ship for two primary reasons: **building wide content before the core 30-second loop is fun**, and **refusing to cut P2/P3 features when schedule buffer runs out**.

---

## 1. The 6 Production Gates

| Gate | Core Objective | Exit Criteria (Must ALL be True to Advance) |
|---|---|---|
| **1. Prototype (Greybox)** | Prove the 30-second core loop is fun with zero art polish | Untextured primitive greybox; character movement, camera, and primary verb feel crisp at 60 FPS |
| **2. Vertical Slice (Gold Bar)** | Prove 1 complete 3–5 minute slice at final shipping quality | Final art direction, PBR lighting, audio bus mix, HUD, and 60 FPS on `LOW` preset proved on 1 encounter |
| **3. Alpha (Feature Complete)** | All core mechanics, UI flows, and levels playable start-to-finish | Game can be played from Title Screen to Credits; placeholder art allowed in late levels; save/load works |
| **4. Beta (Content Locked)** | All art, audio, dialogue, and localization locked | Zero new features added; 100% of assets in-engine; memory (`<= 1.8 GB` RAM / `512 MB` VRAM) passes |
| **5. Release Candidate (RC)** | Zero known `S0` (Crash/Blocker) or `S1` (Major) bugs | Cloud Windows + Web builds verified on clean environments; full regression soak passes |
| **6. Gold Master** | Packaged, signed/checksummed, store page ready | Checksum manifest generated; day-1 hotfix pipeline verified |

---

## 2. Ruthless Scope Triage (`P0 / P1 / P2`)

Categorize every feature in the backlog into three buckets:
- **`P0` (Survival Core — 50% of time budget)**: If missing, the game literally cannot be played from start to finish (movement, 1 core weapon, 3 core enemy types, save/load, pause/settings, main levels).
- **`P1` (Depth & Variety — 30% of time budget)**: Multiplies replayability using existing systems (2nd weapon, elite enemy variant, side quests, interactive music stems).
- **`P2` (Stretch Polish — 20% of time budget, first to be cut)**: Photo mode, minigames, complex crafting sub-trees.

**The Scoping Law**: If a milestone slips by `> 15%`, immediately cut or defer `P2` items rather than compressing QA and optimization at the end.
