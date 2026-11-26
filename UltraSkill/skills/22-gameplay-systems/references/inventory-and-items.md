# Inventory and Items

Separate **immutable Item Definitions** (static archetypes stored in data tables) from **mutable Item Instances** (runtime stack counts, durability, or rolled affixes stored in the player's inventory and save file).

---

## 1. Archetype vs Instance Split

### Static Item Definition (`items.json` / Read-Only Resource)
```json
{
  "iron_halberd": {
    "id": "iron_halberd",
    "display_name_key": "ITEM_IRON_HALBERD_NAME",
    "category": "weapon_melee",
    "rarity": "uncommon",
    "max_stack": 1,
    "weight_kg": 4.5,
    "base_damage": 34,
    "attack_speed_hz": 1.15,
    "max_durability": 120,
    "sell_value": 85
  },
  "healing_tonic": {
    "id": "healing_tonic",
    "display_name_key": "ITEM_HEALING_TONIC_NAME",
    "category": "consumable",
    "rarity": "common",
    "max_stack": 10,
    "weight_kg": 0.25,
    "effect_type": "heal_flat",
    "effect_magnitude": 60,
    "sell_value": 15
  }
}
```

### Runtime Inventory Slot (`Save Payload`)
```json
{
  "slot_index": 0,
  "item_id": "iron_halberd",
  "qty": 1,
  "durability": 98,
  "modifiers": ["keen_edge_tier1"]
}
```
- **Why this matters**: If a balance patch changes `iron_halberd.base_damage` from `34` to `38`, existing player save files automatically inherit the updated base damage without breaking.

---

## 2. Transaction Safety (Add, Remove, Split, Swap)

All inventory mutations must be **atomic transactions** that validate preconditions before mutating state:

1. **`can_add_item(item_id, qty) -> bool`**:
   - First check existing partial stacks of `item_id` where `slot.qty < item_def.max_stack`.
   - Then count empty slots needed for the remainder: `ceil(remaining_qty / item_def.max_stack)`.
   - Also check encumbrance limit if applicable (`current_weight + qty * item_def.weight_kg <= max_weight`).
2. **`consume_ingredients(recipe_costs: Dictionary) -> bool`**:
   - Verify **all** required ingredient quantities are present before deducting **any** ingredient. Never partially deduct items and then fail mid-craft.
3. **UI Decoupling**:
   - The `InventoryModel` is pure data + transaction logic with zero references to UI `Control` nodes.
   - After any mutation, emit `inventory_changed(affected_slot_indices: Array[int])` so the UI redraws only changed slots.
