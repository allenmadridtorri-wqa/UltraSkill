# Anti-Cheat and Server Validation

The fundamental law of multiplayer security: **The client is in the hands of the adversary.** Any packet arriving from a client is a *request*, never a *fact*.

---

## 1. Top 5 Client Exploits & Server Countermeasures

| Exploit Type | How Cheaters Do It | Server-Authoritative Defense |
|---|---|---|
| **Speedhack / Teleport** | Sending `60` input packets in `200 ms` or editing client coordinates | Server ignores client coordinates; processes at most `1` input per server simulation tick (`60 Hz`); clamps `delta_pos <= max_speed * dt * 1.05` |
| **Rapid-Fire / Cooldown Bypass** | Sending `FireWeapon` packets every tick ignoring local cooldown timers | Server maintains authoritative `next_allowed_fire_tick[player_id]` and drops early fire requests |
| **Wallhack / ESP Radar** | Reading memory for all entity transforms sent in global snapshots | **Fog-of-War Interest Filtering**: Server omits hostile entities that are outside line-of-sight + acoustic radius from that client's snapshot |
| **Damage / Currency Spoofing** | Calling `ApplyDamage(boss_id, 999999)` or `AddGold(50000)` | Remove all client-to-server mutation RPCs; server calculates damage from server weapon tables when a server raycast/hitbox confirms impact |
| **Backtrack / Fake Lag Switch** | Stamping a shot packet with a timestamp `1,500 ms` in the past to hit a player who already ran behind cover | Clamp Lag-Compensation rewind window to **`max_rewind = 200 ms`** based on server-measured smoothed RTT |

---

## 2. Server-Side Lag Compensation (Historical Hitbox Rewind)

When a player with `120 ms` RTT fires a hitscan rifle at a moving target, the target on their screen is rendered at `T_server - 60 ms (one-way latency) - 100 ms (interpolation buffer) = T_server - 160 ms`. If the server raycasts against the target's *current* `T_server` position, the player has to lead their shots artificially.

### Safe Rewind Algorithm
1. Server maintains a **1-second (60-tick) ring buffer** of historical bounding boxes and bone transforms for all Hurtboxes.
2. Client input packet includes `client_view_tick` (the interpolated server tick the client was seeing when they pulled the trigger).
3. Server clamps `target_tick = clamp(client_view_tick, current_server_tick - 12, current_server_tick)` (`12 ticks @ 60 Hz = 200 ms` max rewind).
4. Server temporarily restores candidate enemy hurtboxes to their transforms at `target_tick`, performs the server raycast from the shooter's authoritative eye position at `current_server_tick`, applies damage if hit, and immediately restores current transforms.
