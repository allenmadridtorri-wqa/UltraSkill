# Dialogue and Interaction

World interactions (doors, chests, NPCs, terminals) and branching dialogue must use a unified **Interaction Interface** and a deterministic **Dialogue Node Graph**.

---

## 1. Unified Spatial Interaction Protocol

Never place bespoke raycast checks inside every door, chest, and NPC script. Instead:
1. **Player `InteractionSensor`**:
   - Cast a short shape/ray (`2.2 m` reach in 1st person, `2.8 m` from character chest in 3rd person) on Collision Layer `Interactables`.
   - Score overlapping candidates by `score = dot(camera_forward, dir_to_target) - 0.15 * distance`.
   - Highlight the single best candidate and display its localized prompt (`[E] Open Chest`, `[E] Speak to Vera`).
2. **`Interactable` Component Contract**:
   - `can_interact(actor: Node) -> bool`
   - `get_prompt_key(actor: Node) -> StringName`
   - `interact(actor: Node) -> void`

---

## 2. Branching Dialogue Graph Schema

Represent conversations as directed graphs where edges have optional **Condition Guards** and nodes emit **Side-Effect Actions**:

```json
{
  "conversation_id": "npc_vera_hub_01",
  "entry_node": "n_greeting",
  "nodes": {
    "n_greeting": {
      "speaker_key": "NPC_VERA",
      "text_key": "DLG_VERA_GREETING_01",
      "voice_cue": "vo_vera_001",
      "choices": [
        {
          "text_key": "DLG_CHOICE_ASK_BEACON",
          "target": "n_beacon_info"
        },
        {
          "text_key": "DLG_CHOICE_HAND_OVER_CREST",
          "condition": {"has_item": "sentinel_crest"},
          "target": "n_reward_branch"
        },
        {
          "text_key": "DLG_CHOICE_LEAVE",
          "target": "END"
        }
      ]
    },
    "n_beacon_info": {
      "speaker_key": "NPC_VERA",
      "text_key": "DLG_VERA_BEACON_INFO",
      "on_enter_actions": [
        {"type": "set_flag", "flag": "spoke_vera_about_beacon", "value": true}
      ],
      "next": "n_greeting"
    },
    "n_reward_branch": {
      "speaker_key": "NPC_VERA",
      "text_key": "DLG_VERA_THANKS",
      "on_enter_actions": [
        {"type": "remove_item", "item_id": "sentinel_crest", "qty": 1},
        {"type": "complete_quest", "quest_id": "q_restore_beacon"}
      ],
      "next": "END"
    }
  }
}
```

---

## 3. Typewriter Pacing & Skip Ergonomics

- **Typewriter Speed**: `45–60 characters/second` default, with punctuation pauses (`,` = `120 ms`, `.` / `!` / `?` = `250 ms`).
- **Two-Stage Advance Button**:
  - Pressing `Interact` / `Accept` **while text is still typing**: instantly reveals the full line (never skips the line unread).
  - Pressing `Interact` / `Accept` **when the line is fully revealed**: advances to the next node or activates choice selection.
