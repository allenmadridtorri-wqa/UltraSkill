# Quest and Objective Systems

Quests should never be coded as bespoke per-quest scripts that poll the scene tree every frame. Build a **data-driven Objective State Machine** that listens to domain events on the global `EventBus`.

---

## 1. Quest Lifecycle States

Every quest and individual objective step transitions monotonically through four states:
1. **`LOCKED`**: Prerequisites not yet met; hidden from journal.
2. **`AVAILABLE`**: Can be accepted from a quest giver or discovery trigger.
3. **`ACTIVE`**: In the player's journal; subscribed to relevant domain events.
4. **`COMPLETED`** (or **`FAILED`**): Rewards granted; unsubscribed from events; persisted in save flags.

---

## 2. Declarative Quest Schema

```json
{
  "quest_id": "q_restore_beacon",
  "title_key": "QUEST_RESTORE_BEACON_TITLE",
  "prerequisites": ["q_tutorial_escape"],
  "steps": [
    {
      "step_id": "clear_courtyard",
      "type": "kill_count",
      "target_archetype": "corrupted_sentinel",
      "required_count": 3,
      "retroactive_flag": "courtyard_sentinels_cleared"
    },
    {
      "step_id": "insert_power_cell",
      "type": "interact_prop",
      "target_id": "beacon_console_01",
      "required_item": "ancient_power_cell",
      "consume_item": true
    }
  ],
  "rewards": {
    "xp": 450,
    "currency": {"gold": 120},
    "items": [{"item_id": "sentinel_crest", "qty": 1}]
  }
}
```

---

## 3. Handling Out-of-Order Player Actions (Sequence Breaking)

Players frequently kill a quest target or pick up a quest item *before* talking to the NPC who assigns the quest. If the quest only listens to live `entity_defeated` events while `ACTIVE`, the quest permanently soft-locks.

### Three Rules to Prevent Quest Soft-Locks
1. **World Fact Blackboard (`world_flags` & `inventory`)**:
   - Whenever an objective step becomes `ACTIVE`, immediately evaluate current state against the blackboard:
     - For `collect_item` objectives: count how many of `target_item` the player *already holds* in their inventory.
     - For unique bosses or world events: check if `retroactive_flag` is already `true` in `world_flags`.
2. **Quest Item Protection**:
   - Items tagged `"quest_critical": true` cannot be sold, dropped, or destroyed until their referencing quest reaches `COMPLETED`.
3. **Idempotent Reward Granting**:
   - Record `"q_restore_beacon_rewarded": true` in the same atomic transaction that grants XP and items so reloading or double-clicking dialogue never duplicates rewards.
