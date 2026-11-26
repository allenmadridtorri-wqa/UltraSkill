# Serialization and Save Migrations

A production save system must survive power loss mid-write, detect tampering or bit-rot, never execute arbitrary code during deserialization, and cleanly migrate v1 saves to v2+ when the game is patched.

---

## 1. Security First: Pure Data Formats Only

- **NEVER** use Godot binary `ResourceLoader.load()` on untrusted `.tres`/`.res` user saves (they can embed inline `GDScript` and execute arbitrary OS commands).
- **NEVER** use Python `pickle` or C# `BinaryFormatter`.
- **USE** versioned JSON (with SHA-256 or CRC32 checksum envelope) or schema-validated binary buffers (MessagePack / FlatBuffers) parsed strictly as data dictionaries.

---

## 2. Canonical Save File Envelope

Every save file on disk must wrap its payload in a top-level metadata envelope:

```json
{
  "schema_version": 2,
  "game_version": "1.1.0",
  "timestamp_utc": "2026-05-01T14:30:00Z",
  "playtime_seconds": 14520,
  "checksum_sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
  "payload": {
    "player": {
      "level": 12,
      "hp_current": 140,
      "hp_max": 150,
      "position": [12.5, 0.0, -44.2],
      "inventory": [
        {"item_id": "iron_blade", "qty": 1, "durability": 85}
      ]
    },
    "world_flags": {
      "boss_01_defeated": true,
      "bridge_lowered": true
    }
  }
}
```

- **`checksum_sha256`**: Computed over the canonical JSON serialization of `"payload"` (sorted keys, no extra whitespace) plus a static application salt.

---

## 3. Atomic Write & `.bak` Rollback Protocol

Never open `save_slot_0.json` with `"w"` directly—if the laptop battery dies mid-write, the file is truncated to 0 bytes and the player loses 20 hours of progress.

### 4-Step Atomic Commit
1. Serialize and compute checksum in memory.
2. Write to temporary file `save_slot_0.json.tmp` and flush to disk.
3. Copy existing `save_slot_0.json` (if valid) to `save_slot_0.json.bak`.
4. Atomically rename `save_slot_0.json.tmp` over `save_slot_0.json`.

### Recovery on Load
When loading `save_slot_0.json`:
1. Parse JSON and verify `checksum_sha256`.
2. If JSON parse fails or checksum mismatches, log a warning and fall back to `save_slot_0.json.bak`.

---

## 4. Sequential Schema Migration Pipeline (`v1 -> v2 -> v3`)

Never put `if save.version == 1:` checks scattered across gameplay classes. Centralize migrations in a pure pipeline before handing data to gameplay systems:

```python
def migrate_save_dict(doc: dict) -> dict:
    version = doc.get("schema_version", 1)
    payload = doc["payload"]

    if version == 1:
        # v1 -> v2: convert flat item ID strings into structured item objects
        old_items = payload.get("player", {}).get("inventory", [])
        payload["player"]["inventory"] = [
            {"item_id": item_id, "qty": 1, "durability": 100}
            if isinstance(item_id, str) else item_id
            for item_id in old_items
        ]
        version = 2

    if version == 2:
        # v2 -> v3: ensure world_flags dictionary exists
        payload.setdefault("world_flags", {})
        version = 3

    doc["schema_version"] = version
    return doc
```
