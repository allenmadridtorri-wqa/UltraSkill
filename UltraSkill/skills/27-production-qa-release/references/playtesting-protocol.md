# Playtesting Protocol

Developers are the worst judges of their own onboarding and difficulty—you already know where the hidden switch is and the exact frame to parry the boss. Structured playtesting replaces opinion with empirical observation.

---

## 1. The Rule of Silent Observation

During a live or recorded playtest:
1. **Do Not Coach the Tester**:
   - Never say *"Oh, press Left Shift to dodge through that laser"* or *"Go through the blue door on the left."*
   - In the real world, you will not be standing behind the buyer's chair explaining the controls. If the player doesn't know what to do, **the game failed to communicate it**.
2. **Watch Hands and Eyes, Not Post-Session Compliments**:
   - Players are polite in post-test interviews (*"Yeah, it was cool!"*). Trust **where they hesitated, where they died 4 times in a row, and which menus they opened repeatedly** over polite verbal praise.

---

## 2. Automated Local Playtest Telemetry (`playtest_events.jsonl`)

Write lightweight JSON-Lines events during playtest builds so every session produces objective metrics:

```json
{"t": 12.4, "event": "zone_entered", "zone": "tutorial_courtyard"}
{"t": 28.1, "event": "damage_taken", "source": "shield_trooper", "amount": 25, "pos": [14.2, 0.0, -8.1]}
{"t": 44.0, "event": "player_death", "cause": "fall_hazard", "zone": "gap_jump_02", "attempt": 1}
{"t": 115.6, "event": "objective_completed", "id": "clear_courtyard", "duration_sec": 103.2}
```

---

## 3. Quantitative Triage Thresholds

| Observed Telemetry Metric | Threshold Triggering Mandatory Fix | Root Cause & Action |
|---|---|---|
| **Tutorial Stall Rate** | `>= 20%` of testers take `> 90 s` on a 15-second prompt | Prompt blends into HUD or mechanic requires un-taught simultaneous buttons; isolate prompt in safe room |
| **Blind-Shot Damage Rate** | `>= 30%` of damage taken comes from off-screen enemies the player never looked at | Add directional off-screen threat arc + louder audio attack telegraph |
| **Mechanic Neglect** | `>= 50%` of testers finish the slice without using a core verb (`Parry` / `Heavy Attack`) | Verb lacks clear reward or startup risk is too high; add a gated teaching enemy weak specifically to that verb |
| **Encounter Wipe Ratio** | `> 40%` death rate on non-boss encounter | Check enemy attack token cap (`<= 2`) and placement of health recovery / cover |
